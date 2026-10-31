from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/criminals", tags=["Wanted Criminals"])


@router.get(
    "/",
    response_model=list[schemas.CriminalOut],
    summary="Список разыскиваемых бананчиков",
    description=(
        "Все фильтры необязательны и работают вместе (логическое И).\n\n"
        "Пример: `/api/criminals/?min_reward=5000&armed=true&sort=-reward`"
    ),
)
def list_criminals(
    min_reward: int | None = Query(None, ge=0, description="Минимальная награда"),
    max_reward: int | None = Query(None, ge=0, description="Максимальная награда"),
    armed: bool | None = Query(None, description="Вооружён"),
    has_crew: bool | None = Query(None, description="Есть команда"),
    escape_master: bool | None = Query(None, description="Мастер побега"),
    sort: Literal["reward", "-reward"] | None = Query(
        None, description="Сортировка по награде: `reward` (по возрастанию) или `-reward` (по убыванию)"
    ),
    db: Session = Depends(get_db),
):
    if min_reward is not None and max_reward is not None and min_reward > max_reward:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "min_reward must not be greater than max_reward")

    C = models.WantedCriminal
    query = select(C)

    if min_reward is not None:
        query = query.where(C.reward >= min_reward)
    if max_reward is not None:
        query = query.where(C.reward <= max_reward)
    if armed is not None:
        query = query.where(C.armed == armed)
    if has_crew is not None:
        query = query.where(C.has_crew == has_crew)
    if escape_master is not None:
        query = query.where(C.escape_master == escape_master)

    if sort == "reward":
        query = query.order_by(C.reward.asc(), C.id)
    elif sort == "-reward":
        query = query.order_by(C.reward.desc(), C.id)
    else:
        query = query.order_by(C.id)

    return db.scalars(query).all()


@router.get("/{criminal_id}/", response_model=schemas.CriminalOut, summary="Детали преступника")
def get_criminal(criminal_id: int, db: Session = Depends(get_db)):
    criminal = db.get(models.WantedCriminal, criminal_id)
    if criminal is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Criminal not found")
    return criminal
