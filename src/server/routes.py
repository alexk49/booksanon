from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from . import views, settings

static = StaticFiles(directory=str(settings.STATIC_DIR))

routes = [
    Route("/", views.home, name="home"),
    Route("/add-book", views.add_book, name="add_book"),
    Route("/submission", views.submission, name="submission"),
    Route("/csrf_token", views.set_csrf_token, name="csrf_token"),
    Route("/search_books", views.search_books, name="search_books", methods=["POST"]),
    Route("/submit_book", views.submit_book, name="submit_book", methods=["POST"]),
    Mount("/static", static, name="static"),
]
