from starlette.templating import Jinja2Templates
from repositories import repositories
from . import settings
from . import resources


templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))


async def home(request):
    template = "index.html"
    books = await repositories.get_most_recent_books(resources.db)
    context = {"request": request, "books": books}
    return templates.TemplateResponse(template, context=context)


async def add_books(request):
    return
