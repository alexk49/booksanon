import asyncio
import logging
import secrets
from collections.abc import Callable
from datetime import timedelta
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from db.models import Book
from .form_validators import book_submit_fields, clean_results, fetch_more_reviews_fields, get_errors, search_form_fields, validate_form
from config import settings
from .resources import resources
from .tasks import process_review_submission


logger = logging.getLogger("app")

templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))


""" html page routes """


async def home(request: Request):
    if "session_id" not in request.session:
        request.session["session_id"] = await create_csrf_token()
    template = "index.html"
    reviews = await resources.review_repo.get_most_recent_book_reviews()
    logger.debug("fetching latest reviews: %s", reviews)

    next_cursor = str(reviews[-1].created_at.isoformat() if reviews else None)
    review_id = str(reviews[-1].id if reviews else None)
    logger.debug("next_cursor: %s, review_id: %s", next_cursor, review_id)

    context = {
        "request": request,
        "reviews": reviews,
        "cursor": next_cursor,
        "review_id": review_id
    }
    return templates.TemplateResponse(request, template, context=context)


async def about(request: Request):
    template = "about.html"
    context = {"request": request}
    return templates.TemplateResponse(request, template, context=context)


async def add_book(request: Request):
    if "session_id" not in request.session:
        request.session["session_id"] = await create_csrf_token()
    template = "add-book.html"
    context = {"request": request}
    return templates.TemplateResponse(request, template, context=context)


async def submission(request: Request):
    template = "submission.html"
    context = {"request": request}
    return templates.TemplateResponse(request, template, context=context)


async def review_page(request: Request):
    """
    Use /review/review.id to return individual review
    """
    review_id = request.path_params["review_id"]
    review = await resources.review_repo.get_review_and_book_by_review_id(review_id=review_id)
    template = "review.html"
    context = {"request": request, "review": review}
    return templates.TemplateResponse(request, template, context=context)


async def book_page(request: Request):
    """
    Use /books/book.id to return a book page
    """
    book_id = request.path_params["book_id"]
    book, reviews = await resources.book_repo.get_book_and_reviews_by_book_id(book_id=book_id)
    template = "book.html"
    context = {"request": request, "book": book, "reviews": reviews}
    return templates.TemplateResponse(request, template, context=context)


async def author_page(request: Request):
    author_id = int(request.path_params["author_id"])

    author_task = resources.author_repo.get_author_by_id(author_id)
    books_task = resources.book_repo.get_books_with_reviews_by_author(author_id)

    author, books = await asyncio.gather(author_task, books_task)

    logger.debug(author)
    logger.debug(books)
    context = {
        "request": request,
        "author": author,
        "books": books,
    }
    return templates.TemplateResponse(request, "author.html", context=context)


async def search(request):
    async def on_success(clean_form):
        q = clean_form["search_query"].replace(" ", "+")
        return RedirectResponse(
            url=f"/search?q={q}",
            status_code=303,
        )

    async def on_failure(errors):
        request.session["flash_errors"] = errors
        return RedirectResponse(
            url="/search",
            status_code=303,
        )

    async def search_get(request):
        query = (request.query_params.get("q", "")).replace("+", " ")
        # get errors and reset session flash_errors storage
        errors = request.session.pop("flash_errors", None)
        results = []
        if query:
            results = await resources.book_repo.search_books(search_query=query)
        return templates.TemplateResponse(
            request, "search.html", {"request": request, "query": query, "results": results, "errors": errors}
        )

    if request.method == "POST":
        return await handle_form(request, search_form_fields, on_success, on_failure)

    if request.method == "GET":
        return await search_get(request)


""" Error handling pages """


async def not_found(request: Request, exc: Exception):
    context = {
        "request": request,
        "title": "404 Page Not Found",
        "message": "The page you are looking for does not exist.",
    }
    return templates.TemplateResponse(request, "error.html", context=context)


async def bad_request(request: Request, exc: Exception):
    context = {
        "request": request,
        "title": "400 Bad Request",
        "message": "The request was malformed or invalid. Please check your input.",
    }
    return templates.TemplateResponse("error.html", context=context)


async def unauthorized(request: Request, exc: Exception):
    context = {
        "request": request,
        "title": "401 Unauthorized",
        "message": "You need to log in to access this resource. Please log in and try again.",
    }
    return templates.TemplateResponse("error.html", context=context)


async def forbidden(request: Request, exc: Exception):
    context = {
        "request": request,
        "title": "403 Forbidden",
        "message": "You do not have permission to access this resource.",
    }
    return templates.TemplateResponse("error.html", context=context)


async def rate_limit_exceeded(request: Request, exc: Exception):
    context = {
        "request": request,
        "title": "429 Too Many Requests",
        "message": "You have exceeded the rate limit. Please try again later.",
    }
    return templates.TemplateResponse("error.html", context=context)


async def server_error(request: Request, exc: Exception):
    context = {
        "request": request,
        "title": "500 Internal Server Error",
        "message": "An unexpected error occurred on the server. Please try again later.",
    }
    return templates.TemplateResponse("error.html", context=context)


async def service_unavailable(request: Request, exc: Exception):
    context = {
        "request": request,
        "title": "503 Service Unavailable",
        "message": "The service is temporarily unavailable. Please try again later.",
    }
    return templates.TemplateResponse("error.html", context=context)


async def gateway_timeout(request: Request, exc: Exception):
    context = {
        "request": request,
        "title": "504 Gateway Timeout",
        "message": "The server did not receive a timely response from an upstream server. Please try again.",
    }
    return templates.TemplateResponse("error.html", context=context)


""" API routes """


async def fetch_more_reviews(request: Request):
    async def on_success(clean_form):
        cursor = clean_form["cursor"]
        review_id = clean_form["review_id"]
        limit = 2

        results = await resources.review_repo.get_recent_reviews_by_cursor(
            limit=limit,
            cursor=cursor,
            review_id=review_id
        )
        logger.debug("results: %s", results)

        next_cursor = str(results[-1].created_at.isoformat() if results else None)
        next_review_id = str(results[-1].id if results else None)

        reviews = [review.to_json_dict() for review in results]

        if reviews:
            return await api_response(success=True, message="Reviews found", data={"results": reviews, "next_cursor": next_cursor, "next_review_id": next_review_id})
        return await api_response(
            success=True,
            message=f"No reviews after {cursor}",
            errors={"error": "No more reviews"},
            data={"results": [], "next_cursor": str(cursor), "next_review_id": review_id},
            status_code=200,
        )
    return await handle_form(request, fetch_more_reviews_fields, on_success)


async def local_search_api(request):
    async def on_success(clean_form):
        logging.info("searching locally for: %s", clean_form["search_query"])
        results = await resources.book_repo.search_books(search_query=clean_form["search_query"])
        if results:
            books = [book.to_json_dict() for book in results]
            return await api_response(success=True, message="Books found", data={"results": books})
        return await api_response(
            success=True,
            message="No results found",
            errors={"error": "No results found"},
            data={"results": []},
            status_code=200,
        )
    return await handle_form(request, search_form_fields, on_success)


async def search_openlib(request: Request):
    async def on_success(clean_form):
        logging.info("calling openlibrary with: %s", clean_form["search_query"])
        results = await resources.openlib_caller.search_books(search_query=clean_form["search_query"], limit=10)
        if results:
            logging.debug(results)
            books = [Book.from_dict(res).to_json_dict() for res in results]
            logging.debug(books)
            return await api_response(success=True, message="Books found", data={"results": books})
        return await api_response(
            success=True,
            message="No results found",
            errors={"detail": "No results found"},
            data={"results": []},
        )

    return await handle_form(request, search_form_fields, on_success)


async def submit_book(request: Request):
    async def on_success(clean):
        logger.info(f"inserting form data into queue: {clean}")
        submission_id = await resources.queue_repo.insert_review_submission(
            openlib_id=clean["openlib_id_hidden"], review=clean["review"]
        )

        logger.info(f"adding submission id to queue: {submission_id}")
        process_review_submission(submission_id)

        return await api_response(
            success=True,
            message="Thanks for adding a review! Your submission is being processed.",
            data={"submission_id": submission_id},
        )

    return await handle_form(request, book_submit_fields, on_success)


async def set_csrf_token(request: Request):
    if "session_id" not in request.session:
        request.session["session_id"] = await create_csrf_token()
    return JSONResponse({"csrf_token": request.session["session_id"]})


""" helper functions """


async def api_response(
    success: bool,
    message: str,
    status_code: int = 200,
    data: dict[str, Any] | None = None,
    errors: dict[str, Any] | None = None,
) -> JSONResponse:
    """
    Standardized API response format for all endpoints.
    """
    payload = {
        "success": success,
        "message": message,
        "data": data if data is not None else None,
        "errors": errors if errors is not None else None,
    }
    logger.debug(payload)
    return JSONResponse(payload, status_code=status_code)


async def handle_form(request: Request, form_fields: dict, on_success: Callable, on_failure: Callable | None = None):
    """
    Generic form handler, which requires on_success function from original view to be passed
    """
    form = dict(await request.form())
    session_token = request.session.get("session_id", "")

    result = validate_form(form, session_token, form_fields)
    logger.debug(result)
    errors = get_errors(result)

    if errors:
        logger.warning("Errors with form submission: %s", errors)
        if on_failure:
            return await on_failure(errors)
        return await api_response(
            success=False,
            message="There have been errors with your form.",
            errors=errors,
            status_code=400,
        )
    clean = clean_results(result)
    logger.info(clean)
    return await on_success(clean)


async def create_csrf_token():
    logger.info("creating new csrf token")
    return secrets.token_urlsafe(32)
