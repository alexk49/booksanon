import contextlib
import logging
from logging.config import dictConfig

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from config import settings
from .middleware import RequestIDMiddleware
from .resources import resources
from .routes import routes
from config.logging_config import LOGGING_CONFIG

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("app")


middleware = [Middleware(SessionMiddleware, secret_key=settings.SECRET_KEY, https_only=True, same_site="strict"), Middleware(RequestIDMiddleware)]


@contextlib.asynccontextmanager
async def lifespan(app):
    await resources.startup()
    logger.info("Application resources started")
    try:
        yield
    finally:
        await resources.shutdown()
        logger.info("Application resources shutdown")


app = Starlette(
    debug=settings.DEBUG,
    middleware=middleware,
    routes=routes,
    lifespan=lifespan,
)
