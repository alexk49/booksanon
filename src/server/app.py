import contextlib
import logging
from logging.config import dictConfig

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from . import views
from config import settings
from .middleware import RateLimitMiddleware, RequestIDMiddleware
from .resources import resources
from .routes import routes
from config.logging_config import LOGGING_CONFIG

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("app")


middleware = [
    Middleware(SessionMiddleware, secret_key=settings.SECRET_KEY, https_only=True, same_site="strict"),
    Middleware(RequestIDMiddleware),
    Middleware(
        RateLimitMiddleware,
        default_limit=60,
        limit_period=60,
        cleanup_period=150,
        route_limits={
            "/api/submit-book": 1,
            "/api/search-openlib": 5,
        },
    ),
]

exception_handlers = {
    400: views.bad_request,
    401: views.unauthorized,
    403: views.forbidden,
    404: views.not_found,
    429: views.rate_limit_exceeded,
    500: views.server_error,
    503: views.service_unavailable,
    504: views.gateway_timeout,
}


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
    debug=settings.DEBUG, middleware=middleware, routes=routes, lifespan=lifespan, exception_handlers=exception_handlers
)
