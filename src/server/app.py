import contextlib

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from . import settings
from .resources import resources
from .routes import routes

middleware = [Middleware(SessionMiddleware, secret_key=settings.SECRET_KEY, https_only=True, same_site="strict")]


@contextlib.asynccontextmanager
async def lifespan(app):
    await resources.startup()
    print("Application resources started")
    try:
        yield
    finally:
        await resources.shutdown()
        print("Application resources shutdown")


app = Starlette(
    debug=settings.DEBUG,
    middleware=middleware,
    routes=routes,
    lifespan=lifespan,
)
