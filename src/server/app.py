from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from . import settings
from .resources import db, user_repo
from .routes import routes

startup = [db.start_up, user_repo.create_anon]

shutdown = [db.close_down]

middleware = [Middleware(SessionMiddleware, secret_key=settings.SECRET_KEY, https_only=True, same_site="strict")]

app = Starlette(
    debug=settings.DEBUG,
    middleware=middleware,
    routes=routes,
    on_startup=startup,
    on_shutdown=shutdown,
)
