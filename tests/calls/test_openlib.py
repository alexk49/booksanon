import asyncio
import pytest

from unittest.mock import AsyncMock, patch, MagicMock

from calls.client import Client
from calls.openlib import OpenLibCaller, extract_year, validate_openlib_work_id


@pytest.fixture
async def openlib_caller():
    client = Client(max_retries=3, retry_delay=0.1)
    caller = OpenLibCaller(client=client, max_concurrent_requests=2)

    yield caller

    await client.close_session()


async def test_semaphore_limits_concurrency(openlib_caller: OpenLibCaller):
    in_flight_counter = [0]
    max_in_flight = [0]

    async def fake_request(*args, **kwargs):
        in_flight_counter[0] += 1
        max_in_flight[0] = max(max_in_flight[0], in_flight_counter[0])

        await asyncio.sleep(0.1)

        in_flight_counter[0] -= 1

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"ok": True}
        return mock_resp

    with patch("calls.client.Client.fetch_results", new=AsyncMock(side_effect=fake_request)):
        urls = [f"https://fakeurl.com/{i}" for i in range(5)]

        tasks = [openlib_caller.fetch_with_semaphore(url) for url in urls]
        await asyncio.gather(*tasks)

        assert max_in_flight[0] <= 2
        assert max_in_flight[0] == 2


def test_get_general_query_url(openlib_caller):
    url = openlib_caller.get_general_query_url("test query", limit="2", lang="fr")
    assert url == "https://openlibrary.org/search.json?q=test query&limit=2&lang=fr"

    url = openlib_caller.get_general_query_url("another query")
    assert url == "https://openlibrary.org/search.json?q=another query&limit=1&lang=en"


def test_get_complex_query_url(openlib_caller):
    url = openlib_caller.get_complex_query_url(title="Oliver Twist", author="Charles Dickens")
    assert "title=Oliver Twist" in url
    assert "author=Charles Dickens" in url
    assert url.startswith("https://openlibrary.org/search.json?")

    with pytest.raises(ValueError):
        openlib_caller.get_complex_query_url(invalid_param="some value")


def test_get_author_url(openlib_caller):
    assert openlib_caller.get_author_url("OL1A") == "https://openlibrary.org/authors/OL1A.json"
    assert openlib_caller.get_author_url("/authors/OL1A") == "https://openlibrary.org/authors/OL1A.json"
    assert openlib_caller.get_author_url("invalid") is None


def test_get_work_id_url(openlib_caller):
    assert openlib_caller.get_work_id_url("OL24214484W") == "https://openlibrary.org/works/OL24214484W.json"
    assert openlib_caller.get_work_id_url("/works/OL24214484W") == "https://openlibrary.org/works/OL24214484W.json"
    assert openlib_caller.get_work_id_url("invalid") is None


def test_get_editions_url(openlib_caller):
    assert openlib_caller.get_editions_url("OL24214484W") == "https://openlibrary.org/works/OL24214484W/editions.json"


""" Tests for Parsers """


def test_parse_work_id_page(openlib_caller):
    response = {
        "title": "Test Book",
        "authors": [{"key": "authors/OL1A"}],
        "description": "A test book.",
        "subjects": ["testing"],
        "links": [],
        "key": "/works/OL1W",
        "covers": [12345],
    }
    parsed = openlib_caller.parse_work_id_page(response)
    assert parsed["title"] == "Test Book"
    assert parsed["openlib_work_key"] == "/works/OL1W"
    assert parsed["number_of_pages_median"] == 0


def test_parse_author_id_page():
    response = {
        "name": "Test Author",
        "death_date": "2025-01-01",
        "birth_date": "2000-01-01",
        "key": "/authors/OL1A",
        "remote_ids": {"wikidata": "Q12345"},
    }
    parsed = OpenLibCaller.parse_author_id_page(response)
    assert parsed["name"] == "Test Author"
    assert parsed["key"] == "/authors/OL1A"


def test_parse_books_search_results():
    response = {
        "num_found": 2,
        "docs": [
            {
                "title": "Book 1",
                "author_name": ["Author 1"],
                "author_key": ["key1"],
                "first_publish_year": 2001,
                "key": "/works/work1",
                "cover_i": 1,
            },
            {
                "title": "Book 2",
                "author_name": ["Author 2"],
                "author_key": ["key2"],
                "first_publish_year": 2002,
                "key": "/works/work2",
                "cover_i": 2,
                "number_of_pages_median": 100,
            },
        ],
    }
    parsed = OpenLibCaller.parse_books_search_results(response, limit=2)
    assert len(parsed) == 2
    assert parsed[0]["title"] == "Book 1"
    assert parsed[1]["number_of_pages"] == 100
    assert parsed[0]["number_of_pages"] == 0


def test_parse_editions_response():
    response = {
        "entries": [
            {
                "isbn_13": ["978-1234567890"],
                "isbn_10": ["1234567890"],
                "publishers": ["Test Publisher"],
                "publish_date": "2023-01-01",
                "number_of_pages": 100,
            },
            {
                "publishers": ["Another Publisher"],
                "publish_date": "2022",
                "number_of_pages": 120,
            },
        ]
    }
    book = {"title": "Test Book"}
    parsed = OpenLibCaller.parse_editions_response(response, book)
    assert "978-1234567890" in parsed["isbns_13"]
    assert "Test Publisher" in parsed["publishers"]
    assert parsed["first_publish_year"] == 2022
    # Assuming median of [100, 120] is 110
    assert parsed["number_of_pages_median"] == 110


""" Test helper functions """


def test_extract_year():
    assert extract_year("2023-01-15") == 2023
    assert extract_year("2023/01/15") == 2023
    assert extract_year("2023") == 2023
    assert not extract_year("invalid-date")


def test_validate_openlib_work_id():
    assert validate_openlib_work_id("/works/OL12345W") is True
    assert validate_openlib_work_id("OL12345W") is True
    assert validate_openlib_work_id("invalid") is False
    assert validate_openlib_work_id("OL12345") is False


""" Tests for API calling methods """


@pytest.mark.asyncio
async def test_get_work_id_results(openlib_caller):
    openlib_caller.fetch_with_semaphore = AsyncMock(return_value={"title": "Test"})

    # Patch the staticmethod on the class where it's looked up
    with patch("calls.openlib.OpenLibCaller.parse_work_id_page", return_value={"parsed": True}) as mock_parse:
        result = await openlib_caller.get_work_id_results("OL12345W")

        openlib_caller.fetch_with_semaphore.assert_called_once()
        mock_parse.assert_called_once_with({"title": "Test"}, book=None)
        assert result == {"parsed": True}

    # Test None response
    openlib_caller.fetch_with_semaphore.reset_mock()
    openlib_caller.fetch_with_semaphore.return_value = None
    result = await openlib_caller.get_work_id_results("some_id")
    assert result is None


@pytest.mark.asyncio
async def test_get_author_results(openlib_caller):
    openlib_caller.fetch_with_semaphore = AsyncMock(return_value={"name": "Test Author"})
    openlib_caller.parse_author_id_page = MagicMock(return_value={"parsed": True})

    result = await openlib_caller.get_author_results("author_id")

    openlib_caller.fetch_with_semaphore.assert_called_once()
    openlib_caller.parse_author_id_page.assert_called_once_with({"name": "Test Author"})
    assert result == {"parsed": True}

    # Test None response
    openlib_caller.fetch_with_semaphore.reset_mock()
    openlib_caller.fetch_with_semaphore.return_value = None
    result = await openlib_caller.get_author_results("author_id")
    assert result is None


@pytest.mark.asyncio
async def test_search_books(openlib_caller):
    openlib_caller.fetch_with_semaphore = AsyncMock(return_value={"docs": []})
    openlib_caller.parse_books_search_results = MagicMock(return_value=[{"parsed": True}])

    # Test with title and author
    result = await openlib_caller.search_books(title="t", author="a")
    openlib_caller.fetch_with_semaphore.assert_called_once()
    openlib_caller.parse_books_search_results.assert_called_once_with(response={"docs": []}, limit=10)
    assert result == [{"parsed": True}]

    # Test with search_query
    openlib_caller.fetch_with_semaphore.reset_mock()
    openlib_caller.parse_books_search_results.reset_mock()
    result = await openlib_caller.search_books(search_query="query")
    openlib_caller.fetch_with_semaphore.assert_called_once()
    openlib_caller.parse_books_search_results.assert_called_once_with(response={"docs": []}, limit=10)
    assert result == [{"parsed": True}]

    # Test with no args
    with pytest.raises(ValueError):
        await openlib_caller.search_books()

    # Test None response
    openlib_caller.fetch_with_semaphore.reset_mock()
    openlib_caller.fetch_with_semaphore.return_value = None
    result = await openlib_caller.search_books(title="t")
    assert result is None


@pytest.mark.asyncio
async def test_get_complete_book_data(openlib_caller):
    # Mock get_work_id_results to return a book dict
    openlib_caller.get_work_id_results = AsyncMock(return_value={"key": "work_id"})

    # Define a side effect for fetch_with_semaphore to return different data based on URL
    async def fetch_side_effect(url):
        if "search.json" in url:
            # Mock search API response expected by _enrich_book_from_search
            return {"docs": [], "num_found": 0}
        elif "editions.json" in url:
            # Mock editions API response expected by _get_complete_book_data
            return {"entries": []}
        else:
            # Default fallback (if needed)
            return None

    openlib_caller.fetch_with_semaphore = AsyncMock(side_effect=fetch_side_effect)

    with patch(
        "calls.openlib.OpenLibCaller.parse_editions_response", return_value={"key": "work_id", "parsed_editions": True}
    ) as mock_parse_editions:
        # Input book with openlib_work_key triggers enrichment & work ID fetch
        book_input = {"openlib_work_key": "OL12345W"}

        result = await openlib_caller._get_complete_book_data(book=book_input)

        # Check get_work_id_results called with correct work_id
        openlib_caller.get_work_id_results.assert_called_once_with("OL12345W", book=book_input)

        # Check fetch_with_semaphore called at least twice (search + editions)
        assert openlib_caller.fetch_with_semaphore.call_count >= 2

        # Check parse_editions_response called with editions response and enriched book
        mock_parse_editions.assert_called_once_with({"entries": []}, {"key": "work_id"})

        # Confirm result includes what parse_editions_response returns
        assert result.get("parsed_editions") is True

    # Additional test cases:

    # Test with work_id argument instead of book dict
    openlib_caller.get_work_id_results.reset_mock()
    openlib_caller.fetch_with_semaphore.reset_mock()
    result = await openlib_caller._get_complete_book_data(work_id="OL12345W")
    openlib_caller.get_work_id_results.assert_called_once_with("OL12345W", book={})

    # Test with neither book nor work_id
    result = await openlib_caller._get_complete_book_data()
    assert result is None

    # Test get_work_id_results returns None
    openlib_caller.get_work_id_results.return_value = None
    result = await openlib_caller._get_complete_book_data(work_id="OL12345W")
    assert result is None

    # Reset get_work_id_results return value for next test
    openlib_caller.get_work_id_results.return_value = {"key": "OL12345W"}

    # Test fetch_with_semaphore returns None for editions
    async def fetch_none(url):
        if "search.json" in url:
            return {"docs": [], "num_found": 0}
        elif "editions.json" in url:
            return None
        return None

    openlib_caller.fetch_with_semaphore = AsyncMock(side_effect=fetch_none)
    result = await openlib_caller._get_complete_book_data(work_id="OL12345W")
    assert result is not None  # It should still return the book from get_work_id_results


@pytest.mark.asyncio
async def test_get_book_data_for_db(openlib_caller):
    with patch("calls.openlib.validate_openlib_work_id", return_value=True):
        book_data = {
            "authors": [{"author": {"key": "author_key1"}}, {"author": {"key": "author_key2"}}],
            "title": "Test Book",
        }
        author_data = {"name": "Test Author", "key": "author_key1"}

        openlib_caller._get_complete_book_data = AsyncMock(return_value=book_data)
        openlib_caller.get_author_results = AsyncMock(return_value=author_data)

        book, authors = await openlib_caller.get_book_data_for_db(work_id="OL12345")

        assert openlib_caller._get_complete_book_data.call_count == 1
        assert openlib_caller.get_author_results.call_count == 2
        openlib_caller.get_author_results.assert_any_call("author_key1")
        openlib_caller.get_author_results.assert_any_call("author_key2")

        assert book["title"] == "Test Book"
        assert "Test Author" in book["author_names"]
        assert "author_key1" in book["author_keys"]
        assert len(authors) == 2
        assert authors[0]["name"] == "Test Author"

    # Test invalid work id
    with patch("calls.openlib.validate_openlib_work_id", return_value=False):
        result = await openlib_caller.get_book_data_for_db("invalid_work_id")
        assert result is None

    # Test no book data
    with patch("calls.openlib.validate_openlib_work_id", return_value=True):
        openlib_caller._get_complete_book_data.return_value = None
        result = await openlib_caller.get_book_data_for_db("work_id")
        assert result is None
        openlib_caller._get_complete_book_data.return_value = book_data  # reset

    # Test no author data in book
    with patch("calls.openlib.validate_openlib_work_id", return_value=True):
        book_data_no_authors = {"title": "Test Book", "authors": []}
        openlib_caller._get_complete_book_data.return_value = book_data_no_authors
        result = await openlib_caller.get_book_data_for_db("work_id")
        assert result is None


@pytest.mark.asyncio
async def test_get_complete_books_data(openlib_caller):
    clean_results = [
        {"openlib_work_key": "work1"},
        {"openlib_work_key": "work2"},
    ]
    complete_book_data = {"title": "Complete Book", "author_keys": ["author1", "author2"]}
    author_data = {"name": "Author Name"}

    openlib_caller._get_complete_book_data = AsyncMock(return_value=complete_book_data)
    openlib_caller.get_author_results = AsyncMock(return_value=author_data)

    books, authors = await openlib_caller.get_complete_books_data(clean_results)

    assert openlib_caller._get_complete_book_data.call_count == 2
    assert openlib_caller.get_author_results.call_count == 4  # 2 books * 2 authors each
    assert len(books) == 2
    assert len(authors) == 4
    assert books[0]["title"] == "Complete Book"
    assert authors[0]["name"] == "Author Name"

    # Test no complete book data
    openlib_caller._get_complete_book_data.reset_mock()
    openlib_caller._get_complete_book_data.return_value = None
    result = await openlib_caller.get_complete_books_data(clean_results)
    assert result is None
