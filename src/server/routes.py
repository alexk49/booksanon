from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from . import views, settings

static = StaticFiles(directory=str(settings.STATIC_DIR))

routes = [
    Route("/", views.home, name="home"),
    Mount("/static", static, name="static"),
]
