from starlette.applications import Starlette
from . import settings
from .resources import db
from .routes import routes

startup = [db.start_up]

shutdown = [db.close_down]

app = Starlette(
    debug=settings.DEBUG,
    routes=routes,
    on_startup=startup,
    on_shutdown=shutdown,
)
