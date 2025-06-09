from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from . import views, settings

static = StaticFiles(directory=str(settings.STATIC_DIR))

routes = [
    Route("/", views.home, name="home"),
    Route("/addbook", views.add_book, name="add_book"),
    Mount("/static", static, name="static"),
]
