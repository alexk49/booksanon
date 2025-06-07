from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from . import views, settings

static = StaticFiles(directory=str(settings.STATIC_DIR))

routes = [
    Route("/", views.home, name="home"),
    Route("/addbooks", views.add_books, name="add_books"),
    Mount("/static", static, name="static"),
]
