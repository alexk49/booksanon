from starlette.templating import Jinja2Templates
from . import settings
from . import resources


templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))


async def home(request):
    template = "index.html"
    books = await resources.book_repo.get_most_recent_books(resources.db)
    context = {"request": request, "books": books}
    return templates.TemplateResponse(template, context=context)


async def add_book(request):
    template = "add_book.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context=context)
