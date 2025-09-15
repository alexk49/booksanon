from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from config import settings
from . import views


static = StaticFiles(directory=str(settings.STATIC_DIR))

routes = [
    Mount("/static", static, name="static"),
    # page routes
    Route("/", views.home, name="home"),
    Route("/add-book", views.add_book, name="add_book"),
    Route("/submission", views.submission, name="submission"),
    Route("/search", views.search, name="search", methods=["GET", "POST"]),
    Route("/book/{book_id:int}", views.book_page, name="book"),
    Route("/author/{author_id:int}", views.author_page, name="author"),
    Route("/review/{review_id:int}", views.review_page, name="review"),
    # api routes
    Route("/api/csrf-token", views.set_csrf_token, name="csrf-token"),
    Route("/api/search", views.local_search_api, name="search-api", methods=["POST"]),
    Route("/api/search-openlib", views.search_openlib, name="search-openlib", methods=["POST"]),
    Route("/api/submit-book", views.submit_book, name="submit-book", methods=["POST"]),
]
