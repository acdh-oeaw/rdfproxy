"""ModelBindingsMapper: Functionality for mapping binding maps to a Pydantic model."""

import abc
from collections.abc import Iterable, Iterator
from itertools import chain
from typing import Any, cast, get_args

import pandas as pd
from pandas.api.typing import DataFrameGroupBy
from pydantic import BaseModel
from rdfproxy.utils._types import (
    ModelBoolPredicate,
    _TModelInstance,
    _TSPARQLBindingValue,
)
from rdfproxy.utils.checkers.model_checker import check_model
from rdfproxy.utils.mapper_utils import get_model_bool_predicate
from rdfproxy.utils.type_utils import (
    _is_list_pydantic_model_static_type,
    _is_list_static_type,
    _is_pydantic_model_static_type,
    _is_pydantic_model_union_static_type,
)
from rdfproxy.utils.utils import CurryModel, FieldsBindingsMap, _SENTINEL


class _ModelConstructor(abc.ABC):
    """ABC for RDFProxy ModelConstructors.

    A ModelConstructor knows how to build a Pydantic model given a dataframe
    (either a row-dataframe for ungrouped models or a group-dataframe for grouped models).
    """

    def __init__(
        self,
        model: type[BaseModel],
        df: pd.DataFrame,
        context: pd.DataFrame | None = None,
    ) -> None:
        self.model = model
        self.df = df
        self.context = self.df if context is None else context

        self.alias_map = FieldsBindingsMap(model=model)
        self.curried_model = CurryModel(model=model)

    @abc.abstractmethod
    def get_model(self) -> BaseModel:
        """Run a ModelConstructor and instantiate a Pydantic model instance."""
        return NotImplemented

    @staticmethod
    def _get_constructor_type(model: type[BaseModel]) -> type["_ModelConstructor"]:
        """Get either an UngroupedModelConstructor or a GroupedModelConstructor given a model."""
        constructor: type[_ModelConstructor] = (
            UngroupedModelConstructor
            if model.model_config.get("group_by") is None
            else GroupedModelConstructor
        )

        return constructor

    def _get_model_union_field_value(self, model_union, default: Any) -> Any:
        """Resolve a model union and construct a model instance.

        The RDFProxy semantics for model unions are defined to instantiate
        the first model of a model union. Model union fields are required
        to define a default value and are checked against model_bool.
        """
        nested_model: type[BaseModel] = next(
            filter(_is_pydantic_model_static_type, get_args(model_union))
        )
        constructor: type[_ModelConstructor] = self._get_constructor_type(
            model=nested_model
        )
        nested_model_instance: BaseModel = constructor(
            model=nested_model, df=self._partition_df(nested_model=nested_model)
        ).get_model()

        model_bool_predicate: ModelBoolPredicate = get_model_bool_predicate(
            nested_model_instance
        )

        return (
            nested_model_instance
            if model_bool_predicate(nested_model_instance)
            else default
        )

    def _get_scalar_field_value(self, field_name: str, default: Any):
        """Get the field value for scalar type fields.

        Note that this assumes Non-Aggregated Field Sameness,
        so only the first row of the dataframe is consulted for value retrieval.
        See https://github.com/acdh-oeaw/rdfproxy/issues/243.
        """
        _field_name = self.alias_map[field_name]
        return (
            default
            if (value := self.df.iloc[0].get(_field_name, _SENTINEL)) is _SENTINEL
            else value
        )

    def _partition_df(self, nested_model: type[BaseModel]) -> pd.DataFrame:
        """Reverse-partition the context of an ungrouped model.

        Ungrouped models operate on single-row dataframes;
        if an ungrouped model has a grouped nested model,
        the row-df must be reverse-partitioned against the most recent context
        according to the grouping key of the nested model.

        For ungrouped models, the method simply returns the current dataframe.

        Note: _partition_df uses a mask/bool-indexing for reverse partitioning,
        I believe that this is more efficient than pd.DataFrame.groupby here.
        """
        _group_by = nested_model.model_config.get("group_by", _SENTINEL)

        if _group_by is _SENTINEL:
            return self.df

        alias_map = FieldsBindingsMap(model=nested_model)

        group_by = alias_map[_group_by]
        group_value = self.df[group_by].values[0]

        mask = (
            self.context[group_by].isna()
            if pd.isna(group_value)
            else self.context[group_by] == group_value
        )

        return cast(pd.DataFrame, self.context[mask])


class UngroupedModelConstructor(_ModelConstructor):
    """ModelConstructor for ungrouped models."""

    def get_model(self) -> BaseModel:
        """Run the UngroupedModelConstructor and instantiate a Pydantic model instance."""

        for field_name, field_info in self.model.model_fields.items():
            if _is_pydantic_model_static_type(field_info.annotation):
                nested_model = field_info.annotation
                constructor: type[_ModelConstructor] = self._get_constructor_type(
                    model=nested_model
                )

                df: pd.DataFrame = self._partition_df(nested_model=nested_model)

                field_value: BaseModel = constructor(
                    model=nested_model, df=df, context=self.context
                ).get_model()

            elif _is_pydantic_model_union_static_type(
                model_union := field_info.annotation
            ):
                field_value = self._get_model_union_field_value(
                    model_union=model_union, default=field_info.default
                )
            else:
                field_value = self._get_scalar_field_value(
                    field_name=field_name, default=field_info.default
                )

            self.curried_model(**{field_name: field_value})

        model_instance = self.curried_model()
        assert isinstance(model_instance, self.model)  # type narrow

        return model_instance


class GroupedModelConstructor(_ModelConstructor):
    """ModelConstructor for grouped models."""

    def get_model(self) -> BaseModel:
        """Run the GroupedModelConstructor and instantiate a Pydantic model instance."""

        for field_name, field_info in self.model.model_fields.items():
            if _is_list_pydantic_model_static_type(field_info.annotation):
                nested_model, *_ = get_args(field_info.annotation)
                mapper = _ModelBindingsMapper(model=nested_model, bindings=self.df)
                field_value = self._get_unique_models(iter(mapper.get_models()))

            elif _is_list_static_type(field_info.annotation):
                _field_name = self.alias_map[field_name]
                field_value = list(dict.fromkeys(self.df[_field_name].dropna()))

            elif _is_pydantic_model_static_type(nested_model := field_info.annotation):  # type: ignore
                constructor: type[_ModelConstructor] = self._get_constructor_type(
                    model=nested_model
                )
                field_value = constructor(
                    model=nested_model,
                    df=self.df,
                ).get_model()

            elif _is_pydantic_model_union_static_type(
                model_union := field_info.annotation
            ):
                field_value = self._get_model_union_field_value(
                    model_union=model_union, default=field_info.default
                )
            else:
                field_value = self._get_scalar_field_value(
                    field_name=field_name, default=field_info.default
                )

            self.curried_model(**{field_name: field_value})

        model_instance = self.curried_model()
        assert isinstance(model_instance, self.model)  # type narrow
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


class _ModelBindingsMapper:
    """Functionality for mapping bindings to nested/grouped Pydantic models.

    RDFProxy utilizes Pydantic models also as a modelling grammar for grouping
    and aggregation, mainly by treating the 'group_by' entry in ConfigDict in
    combination with list-type annoted model fields as grouping
    and aggregation indicators. _ModelBindingsMapper applies this grammar
    for mapping flat bindings to potentially nested and grouped Pydantic models.
    """

    def __init__(
        self,
        model: type[_TModelInstance],
        bindings: Iterable[dict[str, _TSPARQLBindingValue]] | pd.DataFrame,
    ) -> None:
        self.model = model
        self.bindings = bindings

        self.df: pd.DataFrame = (
            bindings
            if isinstance(bindings, pd.DataFrame)
            else pd.DataFrame(data=self.bindings, dtype=object)
        )

    def get_models(self) -> list[BaseModel]:
        """Run the RDFProxy mapper and generate a list of Pydantic model instances."""
        if self.df.empty:
            return []
        return list(self._instantiate_models())

    def _instantiate_models(self) -> Iterator[BaseModel]:
        _group_by = self.model.model_config.get("group_by", _SENTINEL)

        if _group_by is _SENTINEL:
            for i in range(len(self.df)):
                row_df = self.df.iloc[[i]]
                yield UngroupedModelConstructor(
                    model=self.model, df=row_df, context=self.df
                ).get_model()
        else:
            alias_map = FieldsBindingsMap(model=self.model)

            group_by = alias_map[_group_by]
            group_by_object: DataFrameGroupBy = self.df.groupby(
                group_by, sort=False, dropna=False
            )

            for _, group_df in group_by_object:
                yield GroupedModelConstructor(model=self.model, df=group_df).get_model()


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
