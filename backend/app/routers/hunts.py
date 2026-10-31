from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db


# Журнал охоты на жалмауыза. Поймал  красавчик/красавица, не поймал.

router = APIRouter(prefix="/api/hunts", tags=["Hunt Logs"])


def _get_hunt_or_404(hunt_id: int, db: Session) -> models.HuntLog:
    # Ищем запись по id. Сейчас проверим, кто тут у нас.
    hunt = db.get(models.HuntLog, hunt_id)

    # Не нашли? Значит, запись ушла за хлебом и не вернулась.
    if hunt is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Hunt log not found")

    return hunt


@router.get("/", response_model=list[schemas.HuntOut], summary="Список записей журнала")
def list_hunts(
    # Фильтр по преступнику. Ищем конкретного красавчика.
    criminal_id: int | None = Query(None, gt=0, description="Фильтр по преступнику"),
    db: Session = Depends(get_db),
):
    # Достаём все записи. Работаем, брат, жұмыс істе!
    query = select(models.HuntLog)

    # Если нужен конкретный преступник — остальных пока отпускаем.
    if criminal_id is not None:
        query = query.where(models.HuntLog.criminal_id == criminal_id)

    # Сортируем по ID, чтобы всё было по красоте.
    return db.scalars(query.order_by(models.HuntLog.id)).all()


@router.get("/{hunt_id}/", response_model=schemas.HuntOut, summary="Одна запись журнала")
def get_hunt(hunt_id: int, db: Session = Depends(get_db)):
    # Одна запись — один разговор, без лишнего базара.
    return _get_hunt_or_404(hunt_id, db)


@router.post(
    "/",
    response_model=schemas.HuntOut,
    status_code=status.HTTP_201_CREATED,
    summary="Записать попытку поимки",
    description="`created_at` выставляется сервером. Если передать его в теле запроса — будет 422.",
)
def create_hunt(data: schemas.HuntCreate, db: Session = Depends(get_db)):
    # Запись обязана ссылаться на существующего тигра ~ Ой, преступника!
    # Айналайын, сначала проверяем, кого вообще ловим.
    if db.get(models.WantedCriminal, data.criminal_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Criminal not found")

    # Создаём отчёт. Теперь всё официально, братан.
    hunt = models.HuntLog(**data.model_dump())

    # Добавляем в базу.
    db.add(hunt)

    # Сохраняем изменения. Құдай қаласа, без ошибок.
    db.commit()

    # Обновляем объект свежими данными из базы.
    db.refresh(hunt)

    # Отчёт готов. Базар жоқ!
    return hunt


@router.patch("/{hunt_id}/", response_model=schemas.HuntOut, summary="Обновить success или notes")
def update_hunt(hunt_id: int, data: schemas.HuntUpdate, db: Session = Depends(get_db)):
    # Сначала найдём запись, не будем искать иголку в стоге сена.
    hunt = _get_hunt_or_404(hunt_id, db)

    # Забираем только те поля, которые клиент реально передал.
    changes = data.model_dump(exclude_unset=True)

    # Ничего не передали? Брат, а что тогда обновлять?
    if not changes:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Provide at least one field: success or notes")

    # success не может быть пустым. Тут либо победа, либо поражение.
    if "success" in changes and changes["success"] is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "success must be true or false")

    # Применяем изменения. Всё чётко, как бешбармак на тоях.
    for field, value in changes.items():
        setattr(hunt, field, value)

    # Сохраняем обновления.
    db.commit()

    # Забираем актуальное состояние из базы.
    db.refresh(hunt)

    return hunt


@router.delete("/{hunt_id}/", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить запись журнала")
def delete_hunt(hunt_id: int, db: Session = Depends(get_db)):
    # Находим запись, которую собираемся отправить в историю.
    hunt = _get_hunt_or_404(hunt_id, db)

    # Удаляем. Болған іс болды, брат.
    db.delete(hunt)

    # Подтверждаем удаление в базе.
    db.commit()

    # Возвращаем 204. Записи больше нет, как и проблем.
    return Response(status_code=status.HTTP_204_NO_CONTENT)