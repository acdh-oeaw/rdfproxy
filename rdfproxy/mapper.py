"""ModelBindingsMapper: Functionality for mapping binding maps to a Pydantic model."""

from collections.abc import Iterator
from itertools import chain
from typing import Generic, get_args

import pandas as pd
from pandas.api.typing import DataFrameGroupBy
from pydantic import BaseModel
from rdfproxy.utils._types import ModelBoolPredicate, _TModelInstance
from rdfproxy.utils.mapper_utils import (
    _is_list_basemodel_type,
    _is_list_type,
    get_model_bool_predicate,
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

    def __init__(self, model: type[_TModelInstance], *bindings: dict):
        self.model = model
        self.bindings = bindings

        self.df = pd.DataFrame(data=self.bindings)
        self.df.replace(pd.NA, None, inplace=True)

    def get_models(self) -> list[_TModelInstance]:
        """Run the model mapping logic against bindings and collect a list of model instances."""
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
            group_by_object: DataFrameGroupBy = df.groupby(group_by, sort=False)

            for _, group_df in group_by_object:
                yield self._instantiate_grouped_model_from_df(group_df, model)

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

    def _instantiate_grouped_model_from_df(
        self, df: pd.DataFrame, model: type[_TModelInstance]
    ) -> _TModelInstance:
        """Instantiate a grouped model from a pd.DataFrame (a group dataframe).

        This handles the GROUPED code path in _ModelBindingsMapper._instantiate_models.
        """
        alias_map = FieldsBindingsMap(model=model)
        curried_model = CurryModel(model=model)

        for field_name, field_info in model.model_fields.items():
            if _is_list_basemodel_type(field_info.annotation):
                nested_model, *_ = get_args(field_info.annotation)
                value = self._get_unique_models(
                    self._instantiate_models(df, nested_model)
                )
            elif _is_list_type(field_info.annotation):
                value = list(dict.fromkeys(df[alias_map[field_name]].dropna()))
            elif isinstance(nested_model := field_info.annotation, type(BaseModel)):
                first_row = df.iloc[0]
                value = self._instantiate_ungrouped_model_from_row(
                    first_row,
                    nested_model,  # type: ignore
                )
            else:
                first_row = df.iloc[0]
                value = first_row.get(alias_map[field_name]) or field_info.default

            curried_model(**{field_name: value})

        model_instance = curried_model()
        assert isinstance(model_instance, model)  # type narrow
        return model_instance
