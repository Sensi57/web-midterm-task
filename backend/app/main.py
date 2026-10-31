import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from . import models
from .database import Base, engine
from .routers import criminals, hunts


# ==================================================
#  DATABASE ARC: ПРОБУЖДЕНИЕ ДРЕВНЕЙ БАЗЫ
#  "Оян, база! Твой разработчик ждёт!"
# ==================================================

def init_db(retries: int = 15, delay: float = 2.0) -> None:
    """Создаём таблицы. Databаза, сен менің соңғы үмітімсің."""

    # Даём базе 15 шансов. Даже Ким Ын столько не сдавался
    for attempt in range(1, retries + 1):
        try:
            # Призываем таблицы через SQL no Jutsu.
            Base.metadata.create_all(bind=engine)
            print("🔥 БАЗА ПРОБУДИЛАСЬ! Базар жоқ!")
            return

        except OperationalError:
            # База опять в гендзюцу... Разбудим через пару секунд
            print(
                f"💀 Database asleep ({attempt}/{retries}). "
                f"Wake up, dattebayo! Қане, тұр!"
            )
            time.sleep(delay)

    # Даже Итачи не смог бы подключиться к этой базе.
    raise RuntimeError("Қап! Database connection failed.")


# ==================================================
#  LIFESPAN ARC: РОЖДЕНИЕ ГЛАВНОГО ГЕРОЯ
# ==================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Перед началом приключения проверяем базу.
    print("⚡ Server transformation arc begins...")

    init_db()

    # Всё готово. Идём к вершине, dattebayo!
    print("🚀 SERVER ONLINE! Алға, басты кейіпкер!")

    yield

    # Финал сезона. Сервер уходит на заслуженный отдых.
    print("🌙 Server shutdown... Көріскенше, батыр!")


# ==================================================
#  MAIN CHARACTER: SPACE BOUNTY HUNTERS API
# ==================================================


app = FastAPI(
    title="Space Bounty Hunters API",
    version="1.0.0",
    description="REST API для охотников за головами: база разыскиваемых преступников и журнал попыток поимки.",
    lifespan=lifespan,
)


# ==================================================
#  ROUTER SUMMONING: КОМАНДА СОБРАНА
# ==================================================

# Он ищет жалмауыза, а не друзей.
app.include_router(criminals.router)

# Журнал охоты. Каждый бой достоин отдельной серии.
app.include_router(hunts.router)


# ==================================================
#  HEALTH CHECK: ПРОВЕРКА ЖИЗНЕННОЙ ЭНЕРГИИ
# ==================================================

@app.get("/health", tags=["Health"], summary="Проверка работоспособности")
def health():
    # Проверяем чакру базы данных. Если SELECT 1 прошёл — живём.
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    # БАЗА ЖИВА! Құдайға шүкір!
    return {"status": "ok"}