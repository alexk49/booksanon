from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from . import settings
from .resources import resources
from .routes import routes

startup_events = [resources.startup]

shutdown_events = [resources.shutdown]

middleware = [Middleware(SessionMiddleware, secret_key=settings.SECRET_KEY, https_only=True, same_site="strict")]

app = Starlette(
    debug=settings.DEBUG,
    middleware=middleware,
    routes=routes,
    on_startup=startup_events,
    on_shutdown=shutdown_events,
)
