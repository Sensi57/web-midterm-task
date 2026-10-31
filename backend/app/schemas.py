from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ---------- WantedCriminal ----------
class CriminalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str | None
    nickname: str
    reward: int
    latitude: float | None
    longitude: float | None
    last_known_note: str | None
    difficulty: int
    armed: bool
    has_crew: bool
    escape_master: bool


# ---------- HuntLog ----------
class HuntCreate(BaseModel):
    # extra="forbid": если клиент пришлёт created_at или id — получит 422
    model_config = ConfigDict(extra="forbid")

    criminal_id: int = Field(gt=0, examples=[3])
    success: bool = Field(examples=[False])
    notes: str | None = Field(default=None, max_length=2000, examples=["Target escaped through an asteroid field."])


class HuntUpdate(BaseModel):
    # PATCH меняет только success и notes
    model_config = ConfigDict(extra="forbid")

    success: bool | None = None
    notes: str | None = Field(default=None, max_length=2000)


class HuntOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    criminal_id: int
    success: bool
    notes: str | None
    created_at: datetime
