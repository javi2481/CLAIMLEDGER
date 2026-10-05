"""Document, Issuer, Period, and Statement. Identity fields only."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from claimledger.identity import PERIOD_1T26, PERIOD_2T26

ISSUED_BY = "ISSUED_BY"
FOR_PERIOD = "FOR_PERIOD"
OF_STATEMENT = "OF_STATEMENT"

_QUARTERLY_PERIODS = frozenset({PERIOD_1T26, PERIOD_2T26})


class Issuer(BaseModel):
    model_config = ConfigDict(graph_id_fields=["issuer"])

    issuer: Literal["BYMA"]


class Period(BaseModel):
    model_config = ConfigDict(graph_id_fields=["period"])

    period: str

    @field_validator("period")
    @classmethod
    def _quarterly(cls, value: str) -> str:
        if value not in _QUARTERLY_PERIODS:
            raise ValueError(f"period is not a quarterly id: {value!r}")
        return value


class Statement(BaseModel):
    model_config = ConfigDict(graph_id_fields=["statement"])

    statement: Literal["income_statement"]


class Document(BaseModel):
    model_config = ConfigDict(graph_id_fields=["artifact_hash"])

    artifact_hash: str
    kind: str
    doubt: str | None = None
    issued_by: Issuer = Field(json_schema_extra={"edge_label": ISSUED_BY})
    for_period: Period | None = Field(
        default=None, json_schema_extra={"edge_label": FOR_PERIOD}
    )
    of_statement: Statement | None = Field(
        default=None, json_schema_extra={"edge_label": OF_STATEMENT}
    )
