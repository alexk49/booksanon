from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates
from . import settings
from . import resources


templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))

""" html page routes """


async def home(request: Request):
    template = "index.html"
    books = await resources.book_repo.get_most_recent_books(resources.db)
    context = {"request": request, "books": books}
    return templates.TemplateResponse(template, context=context)


async def add_book(request: Request):
    template = "add_book.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context=context)


""" API routes """


async def search_books(request):
    form = await request.form()
    search_query = form.get("search-query")
    results = await resources.openlib_caller.search_books(search_query=search_query, limit=10)

    return JSONResponse({"success": True, "results": results})


async def submit_book(request):
    form = await request.form()

    openlib_id = form.get("openlib_id_hidden")
    review = form.get("review")

    print(openlib_id)
    print(review)
    results = {"openlib_id": openlib_id, "review": review}
    return JSONResponse({"success": True, "results": results})
