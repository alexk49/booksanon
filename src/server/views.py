from starlette.templating import Jinja2Templates
from . import settings
from . import resources
from db.models import Book


templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))


async def home(request):
    template = "index.html"
    latest_book_records = await resources.db.run_query("get_most_recent_books")
    # latest_book_records = await resources.db.get_most_recent_books()
    books = [Book.from_db_record(r) for r in latest_book_records]
    context = {"request": request,
               "books": books}
    return templates.TemplateResponse(template, context=context)
