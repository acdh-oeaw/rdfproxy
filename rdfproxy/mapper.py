"""ModelBindingsMapper: Functionality for mapping binding maps to a Pydantic model."""

from collections.abc import Iterable, Iterator
from itertools import chain, tee
from typing import Generic, get_args
import warnings

import pandas as pd
from pandas.api.typing import DataFrameGroupBy, SeriesGroupBy
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from rdfproxy.utils._types import (
    ModelBoolPredicate,
    _TModelInstance,
    _TSPARQLBindingValue,
)
from rdfproxy.utils.checkers.model_checker import check_model
from rdfproxy.utils.exceptions import InconsistentGroupException
from rdfproxy.utils.mapper_utils import get_model_bool_predicate
from rdfproxy.utils.type_utils import (
    _is_list_pydantic_model_static_type,
    _is_list_static_type,
    _is_pydantic_model_static_type,
    _is_pydantic_model_union_static_type,
    _is_sparql_bound_field_type,
)
from rdfproxy.utils.utils import CurryModel, FieldsBindingsMap


class _ModelBindingsMapper(Generic[_TModelInstance]):
    """Utility class for mapping bindings to nested/grouped Pydantic models.

    RDFProxy utilizes Pydantic models also as a modelling grammar for grouping
    and aggregation, mainly by treating the 'group_by' entry in ConfigDict in
    combination with list-type annoted model fields as grouping
    and aggregation indicators. _ModelBindingsMapper applies this grammar
    for mapping flat bindings to potentially nested and grouped Pydantic models.

    Note: _ModelBindingsMapper is intended for use in rdfproxy.SPARQLModelAdapter and -
    since no model sanity checking runs in the mapper itself - somewhat coupled to
    SPARQLModelAdapter. The mapper can be useful in its own right though.
    For standalone use, the initializer should be overwritten and model sanity checking
    should be added to the _ModelBindingsMapper subclass.
    """

    def __init__(
        self,
        model: type[_TModelInstance],
        bindings: Iterable[dict[str, _TSPARQLBindingValue]],
    ) -> None:
        """Initializer for RDFProxy ModelBindingsMapper.

        Note: It is possible to instantiate an empty pd.DataFrame
        (according to pd.DataFrame.empty) from a non-empty/truthy Iterable;
        e.g. pd.DataFrame(data=[{}]) results in an empty df.
        This should be impossible to happen in RDFProxy, because bindings
        for _ModelBindingsMapper will come from rdfproxy.SPARQLWrapper,
        which either returns an empty Iterator or an Iterator of non-empty dicts;
        nonetheless this is something worth explicating i.e. asserting.
        """
        self.model = model
        self.bindings, self._assert_bindings = tee(bindings)

        self.df = pd.DataFrame(data=self.bindings, dtype=object)

        if self.df.empty:
            assert not tuple(self._assert_bindings), (
                "An empty dataframe should imply empty bindings."
            )

    def get_models(self) -> list[_TModelInstance]:
        """Run the model mapping logic against bindings and collect a list of model instances."""
        if self.df.empty:
            return []
        return list(self._instantiate_models(self.df, self.model))

    def _instantiate_models(
        self, df: pd.DataFrame, model: type[_TModelInstance]
    ) -> Iterator[_TModelInstance]:
        """Generate potentially nested and grouped model instances from a dataframe.

        Note: The DataFrameGroupBy object must not be sorted,
        else the result set order will not be maintained.
        """
        alias_map = FieldsBindingsMap(model=model)

        if (_group_by := model.model_config.get("group_by")) is None:
            for _, row in df.iterrows():
                yield self._instantiate_ungrouped_model_from_row(row, model)
        else:
            group_by = alias_map[_group_by]
            group_by_object: DataFrameGroupBy = df.groupby(
                group_by, sort=False, dropna=False
            )

            for _, group_df in group_by_object:
                yield self._instantiate_grouped_model_from_df(group_df, model)

    def _get_model_union_field_value(self, field_info: FieldInfo, row: pd.Series):
        """Compute the value for model union fields.

        The method instantiates the first model of a model union type
        and runs model_bool against that model instance. If model_bool is falsey
        the required default value is returned instead of the model instance.
        """
        assert not field_info.is_required(), "Default value required."

        model_union = field_info.annotation
        nested_model: type[BaseModel] = next(
            filter(_is_pydantic_model_static_type, get_args(model_union))
        )
        nested_model_instance: BaseModel = self._instantiate_ungrouped_model_from_row(
            row,
            nested_model,  # type: ignore
        )

        model_bool_predicate: ModelBoolPredicate = get_model_bool_predicate(
            nested_model_instance
        )

        return (
            nested_model_instance
            if model_bool_predicate(nested_model_instance)
            else field_info.default
        )

    def _instantiate_ungrouped_model_from_row(
        self, row: pd.Series, model: type[_TModelInstance]
    ) -> _TModelInstance:
        """Instantiate an ungrouped model from a pd.Series row.

        This handles the UNGROUPED code path in _ModelBindingsMapper._instantiate_models.
        """
        alias_map = FieldsBindingsMap(model=model)
        curried_model = CurryModel(model=model)

        for field_name, field_info in model.model_fields.items():
            if isinstance(nested_model := field_info.annotation, type(BaseModel)):
                curried_model(
                    **{
                        field_name: self._instantiate_ungrouped_model_from_row(
                            row,
                            nested_model,  # type: ignore
                        )
                    }
                )
            elif _is_pydantic_model_union_static_type(field_info.annotation):
                value = self._get_model_union_field_value(
                    field_info=field_info, row=row
                )
                curried_model(**{field_name: value})
            else:
                _sentinel = object()
                field_value = (
                    field_info.default
                    if (value := row.get(alias_map[field_name], _sentinel)) is _sentinel
                    else value
                )
                curried_model(**{field_name: field_value})

        model_instance = curried_model()
        assert isinstance(model_instance, model)  # type narrow
        return model_instance

    @staticmethod
    def _get_unique_models(models: Iterator[_TModelInstance]) -> list[_TModelInstance]:
        """Get a list of unique models from an iterable.

        Note: Unless frozen=True is specified in a model class,
        Pydantic models instances are not hashable, i.e. dict.fromkeys
        is not feasible for acquiring ordered unique models.

        Note: StopIteration in _get_unique_models should be unreachable,
        because the result of _instantiate_models (the input of _get_unique_models
        when called in _instantiate_grouped_model_from_df) gets called
        on grouped dataframes and empty groups do not exist.
        """
        unique_models = []

        _model = next(models, None)
        assert _model is not None, "StopIteration should be unreachable"

        model_bool_predicate: ModelBoolPredicate = get_model_bool_predicate(_model)

        for model in chain([_model], models):
            if (model not in unique_models) and (model_bool_predicate(model)):
                unique_models.append(model)

        return unique_models

    @staticmethod
    def _enforce_group_consistency(df, model: type[BaseModel]) -> None:
        """Runs a check on a grouped dataframe in order to detect possible data integrity problems.

        In a grouped dataframe, if there are distinct values across a column
        for any field that is not the group key or an aggregation target,
        a data integrity problem is likely and data will be lost in that grouping operation.

        The method checks for distinct values across any SPARQL-bound field column
        that is not an aggregation target and either raises an exception or warns
        if the group is inconsistent. The behavior can be controlled with the
        enforce_group_consistency model config setting.
        """
        alias_map = FieldsBindingsMap(model)
        enforce_group_consistency: bool = model.model_config.get(
            "enforce_group_consistency", True
        )

        for field_name, field_info in model.model_fields.items():
            if not _is_sparql_bound_field_type(field_info.annotation):
                continue

            column_name: str = alias_map[field_name]
            column: SeriesGroupBy = df[column_name]  # type: ignore

            if column.nunique(dropna=False) != 1:
                msg = (
                    "Grouped result set has distinct values for non-aggregated field "
                    f"'{field_name}' (column '{column_name}'). "
                    f"This might indicate a data integrity problem. \n{df}"
                )
                match enforce_group_consistency:
                    case True:
                        raise InconsistentGroupException(msg)
                    case False:
                        warnings.warn(msg)
                    case _:
                        value_err_msg = (
                            "Expected value of type bool for ConfigDict.enforce_group_consistency. "
                            f"Received '{enforce_group_consistency}'."
                        )
                        raise ValueError(value_err_msg)

    def _instantiate_grouped_model_from_df(
        self, df: pd.DataFrame, model: type[_TModelInstance]
    ) -> _TModelInstance:
        """Instantiate a grouped model  pd.DataFrame (a group dataframe).

        This handles the GROUPED code path in _ModelBindingsMapper._instantiate_models.
        """
        alias_map = FieldsBindingsMap(model=model)
        curried_model = CurryModel(model=model)

        self._enforce_group_consistency(df=df, model=model)

        for field_name, field_info in model.model_fields.items():
            if _is_list_pydantic_model_static_type(field_info.annotation):
                nested_model, *_ = get_args(field_info.annotation)
                value = self._get_unique_models(
                    self._instantiate_models(df, nested_model)
                )
            elif _is_list_static_type(field_info.annotation):
                value = list(dict.fromkeys(df[alias_map[field_name]].dropna()))
            elif isinstance(nested_model := field_info.annotation, type(BaseModel)):
                first_row = df.iloc[0]
                value = self._instantiate_ungrouped_model_from_row(
                    first_row,
                    nested_model,  # type: ignore
                )
            elif _is_pydantic_model_union_static_type(field_info.annotation):
                first_row = df.iloc[0]
                value = self._get_model_union_field_value(
                    field_info=field_info, row=first_row
                )
            else:
                first_row = df.iloc[0]

                _sentinel = object()
                value = (
                    field_info.default
                    if (_value := first_row.get(alias_map[field_name], _sentinel))
                    is _sentinel
                    else _value
                )

            curried_model(**{field_name: value})

        model_instance = curried_model()
        assert isinstance(model_instance, model)  # type narrow
        return model_instance


class ModelBindingsMapper(_ModelBindingsMapper):  # pragma: no cover
    """Functionality for mapping bindings to nested/grouped Pydantic models.

    This is a shallow subclass of _ModelBindingsMapper that runs model sanity checks
    upon initialization and is therefore recommended for public/standalone use.
    """

    def __init__(
        self,
        model: type[_TModelInstance],
        bindings: Iterable[dict[str, _TSPARQLBindingValue]],
    ) -> None:
        checked_model = check_model(model)
        super().__init__(model=checked_model, bindings=bindings)
