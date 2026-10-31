from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class WantedCriminal(Base):
    __tablename__ = "wanted_criminals"
    __table_args__ = (
        CheckConstraint("reward >= 0", name="ck_reward_non_negative"),
        CheckConstraint("difficulty BETWEEN 1 AND 10", name="ck_difficulty_range"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # Настоящее имя может быть неизвестно -> nullable
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    nickname: Mapped[str] = mapped_column(String(100))
    reward: Mapped[int] = mapped_column(Integer, index=True)

    # Последнее известное местоположение: координаты и/или текстовая заметка
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_known_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    difficulty: Mapped[int] = mapped_column(Integer)
    armed: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    has_crew: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    escape_master: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    # Один преступник -> много попыток поимки
    hunts: Mapped[list["HuntLog"]] = relationship(back_populates="criminal", cascade="all, delete-orphan")


class HuntLog(Base):
    __tablename__ = "hunt_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    criminal_id: Mapped[int] = mapped_column(
        ForeignKey("wanted_criminals.id", ondelete="CASCADE"), index=True
    )
    success: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Время ставит сервер (БД), клиент его не передаёт
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    criminal: Mapped[WantedCriminal] = relationship(back_populates="hunts")
