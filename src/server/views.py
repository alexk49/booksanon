import secrets
from collections.abc import Callable

from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from db.models import Book, Review
from .form_validators import book_submit_fields, clean_results, get_errors, search_form_fields, validate_form
from . import settings
from . import resources
from .tasks import process_review_submission


templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))


""" html page routes """


async def home(request: Request):
    template = "index.html"
    reviews = await resources.review_repo.get_most_recent_book_reviews(resources.db)
    context = {"request": request, "reviews": reviews}
    return templates.TemplateResponse(template, context=context)


async def add_book(request: Request):
    if "session_id" not in request.session:
        request.session["session_id"] = await create_csrf_token(request)
    template = "add-book.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context=context)


async def submission(request: Request):
    template = "submission.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context=context)


async def review_page(request: Request):
    """
    Use /review/review.id to return individual review
    """
    review_id = request.path_params["review_id"]
    review = await resources.review_repo.get_review_and_book_by_review_id(review_id=review_id)
    template = "review.html"
    context = {"request": request, "review": review}
    return templates.TemplateResponse(template, context=context)


async def book_page(request: Request):
    """
    Use /books/book.id to return a book page
    """
    book_id = request.path_params["book_id"]
    book, reviews = await resources.book_repo.get_book_and_reviews_by_book_id(book_id=book_id)
    template = "book.html"
    context = {"request": request, "book": book, "reviews": reviews}
    return templates.TemplateResponse(template, context=context)


async def author_page(request: Request):
    author_id = int(request.path_params["author_id"])
    author = await resources.author_repo.get_author_by_id(author_id)

    if author:
        books = await resources.book_repo.get_books_by_author(author_id)
        book_ids = [b.id for b in books]

        reviews = await resources.review_repo.get_reviews_for_books(book_ids)

        reviews_by_book: dict[int, list[Review]] = {}
        for rv in reviews:
            reviews_by_book.setdefault(rv.book_id, []).append(rv)

        for b in books:
            b.reviews = reviews_by_book.get(b.id, [])

        context = {
            "request": request,
            "author": author,
            "books": books,
        }
    return templates.TemplateResponse("author.html", context=context)


async def search(request):
    async def on_success(clean_form):
        q = clean_form["search_query"].replace(" ", "+")
        return RedirectResponse(
            url=f"/search?q={q}",
            status_code=303,
        )

    if request.method == "POST":
        return await handle_form(request, search_form_fields, on_success)

    if request.method == "GET":
        query = (request.query_params.get("q", "")).replace("+", " ")
        results = []
        if query:
            results = await resources.book_repo.search_books(search_query=query)
        return templates.TemplateResponse("search.html", {"request": request, "query": query, "results": results})


""" API routes """


async def search_api(request):
    async def on_success(clean_form):
        results = await resources.book_repo.search_books(search_query=clean_form["search_query"])
        books = [book.to_json_dict() for book in results]
        print(books)
        return JSONResponse({"success": True, "results": books})

    return await handle_form(request, search_form_fields, on_success)


async def search_openlib(request: Request):
    async def on_success(clean_form):
        results = await resources.openlib_caller.search_books(search_query=clean_form["search_query"], limit=10)
        books = [Book.from_dict(res).to_json_dict() for res in results]
        return JSONResponse({"success": True, "results": books})

    return await handle_form(request, search_form_fields, on_success)


async def submit_book(request: Request):
    async def on_success(clean):
        # submission_id = str(uuid.uuid4())
        # task = BackgroundTask(fetch_and_store_book_data, openlib_id=clean["openlib_id_hidden"], review=clean["review"])
        print(f"inserting form data into queue: {clean}")
        submission_id = await resources.queue_repo.insert_review_submission(
            openlib_id=clean["openlib_id_hidden"], review=clean["review"]
        )

        print(f"adding submission id to queue: {submission_id}")
        process_review_submission(submission_id)

        return JSONResponse(
            {
                "success": True,
                "message": "Thanks for adding a review! Your submission is being processed.",
                "submission_id": submission_id,
            },
        )

    return await handle_form(request, book_submit_fields, on_success)


async def set_csrf_token(request: Request):
    if "session_id" not in request.session:
        csrf_token = await create_csrf_token(request)
        request.session["session_id"] = csrf_token
    else:
        csrf_token = request.session["session_id"]
    return JSONResponse({"csrf_token": csrf_token})


""" helper functions """


async def handle_form(request: Request, form_fields: dict, on_success: Callable):
    """
    Generic form handler, which requires on_success function from original view to be passed
    """
    form = dict(await request.form())
    session_token = request.session.get("session_id", "")

    result = validate_form(form, session_token, form_fields)
    errors = get_errors(result)

    if errors:
        return JSONResponse(
            {
                "success": False,
                "message": "There have been errors with your form.",
                "errors": errors,
            },
            status_code=400,
        )

    clean = clean_results(result)
    return await on_success(clean)


async def create_csrf_token(request: Request):
    return secrets.token_urlsafe(32)
