import unittest

from bs4 import BeautifulSoup

from app import app, query_db, TEST_DATABASE


class TestWebPage(unittest.TestCase):
    """These tests are carried out on every webpage"""

    def setUp(self):
        """Default sets ups"""
        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()
        self.db = TEST_DATABASE

        # These will get overrided on each class
        # that is not the homepage
        self.page = "/"
        self.response = self.client.get(self.page)
        self.soup = BeautifulSoup(self.response.data, "html.parser")

    def tearDown(self):
        self.ctx.pop()

    def test_webpage_response(self):
        """Testing webpage response code"""
        print(f"Testing {self.page} loads with correct status code")
        self.assertEqual(self.response.status_code, 200)

    def test_navbar_has_loaded(self):
        print(f"testing navbar has loaded on {self.page}")
        nav_links = self.soup.find_all("a", {"class": "nav-link"})
        self.assertEqual(len(nav_links), 4)

        self.assertEqual(
            str(nav_links[0]), '<a class="nav-link" href="/recommend">Recommend</a>'
        )


class TestHomePage(TestWebPage):
    def test_homepage_table(self):
        number_of_books = len(self.soup.find_all("tr"))

        # if database has loaded correctly
        # then there will be at least 2 table rows
        # one for header and one for a book from db
        print("testing some books from database have loaded")
        self.assertGreater(number_of_books, 2)

        print("testing correct number of books is showing")
        # table should have 11 rows max
        # 10 books listed and one header
        self.assertLessEqual(number_of_books, 11)

    def test_homepage_title(self):
        print("testing homepage title is correct")
        self.assertEqual(self.soup.head.title.text, "BooksAnon: Recommendations")


class TestAboutPage(TestWebPage):
    def setUp(self):
        super().setUp()
        self.page = "/about"
        self.response = self.client.get(self.page)
        self.soup = BeautifulSoup(self.response.data, "html.parser")

    def test_about_title(self):
        print("testing about page title is correct")
        self.assertEqual(self.soup.head.title.text, "BooksAnon: About")

    def test_links_in_about(self):
        print("testing links on about page")

        about_page_links = [
            "https://cs50.harvard.edu/",
            "https://github.com/alexk49/booksanon",
            "https://openlibrary.org/",
        ]

        main = self.soup.find("main")
        html_links = main.find_all("a")

        for link in html_links:
            assert link["href"] in about_page_links


class TestRecommendPage(TestWebPage):
    def setUp(self):
        super().setUp()
        self.page = "/recommend"
        self.response = self.client.get(self.page)
        self.soup = BeautifulSoup(self.response.data, "html.parser")

    def test_recommend_title(self):
        print(f"testing about {self.page} title is correct")
        self.assertEqual(self.soup.head.title.text, "BooksAnon: Recommend")

    def test_empty_post_method(self):
        response = self.client.post(self.page, data={"search-term": ""})
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.data, "html.parser")

        error_message = soup.find("p", {"class": "error"})
        self.assertEqual(
            error_message.text,
            "Error: That search query returned no results, please try again.",
        )


class TestHistoryPage(TestWebPage):
    def setUp(self):
        super().setUp()
        self.page = "/history"
        self.response = self.client.get(self.page)
        self.soup = BeautifulSoup(self.response.data, "html.parser")

    def test_recommend_title(self):
        print(f"testing about {self.page} title is correct")
        self.assertEqual(self.soup.head.title.text, "BooksAnon: History")

    def test_top_ten_filter(self):
        response = self.client.post(self.page, data={"selected_filter": "Top Ten"})
        soup = BeautifulSoup(response.data, "html.parser")
        number_of_books = len(self.soup.find_all("tr"))

        # if database has loaded correctly
        # then there will be at least 2 table rows
        # one for header and one for a book from db
        print("testing some books from database have loaded")
        self.assertGreater(number_of_books, 2)

        print("testing correct number of books is showing")
        # table should have 11 rows max
        # 10 books listed and one header
        self.assertLessEqual(number_of_books, 11)

        print("testing count header has been added")
        count_header = soup.find("th", text="Count")
        self.assertEqual(str(count_header), "<th>Count</th>")

    def test_all_books_filter(self):
        response = self.client.post(self.page, data={"selected_filter": "All Books"})
        soup = BeautifulSoup(response.data, "html.parser")

        all_books = query_db('SELECT title FROM "books"')

        for row in all_books:
            title = row["title"]
            self.assertEqual(title, soup.find(text=title))

    def test_recommendations_ordered_by_count(self):
        response = self.client.post(
            self.page, data={"selected_filter": "Recommendations Ordered by Count"}
        )
        soup = BeautifulSoup(response.data, "html.parser")
        all_books = query_db('SELECT title FROM "books"')

        for row in all_books:
            title = row["title"]
            self.assertEqual(title, soup.find(text=title))

        print("testing count header has been added")
        count_header = soup.find("th", text="Count")
        self.assertEqual(str(count_header), "<th>Count</th>")

    def test_invalid_filter(self):
        response = self.client.post(
            self.page, data={"selected_filter": "INVALID FILTER"}
        )
        soup = BeautifulSoup(response.data, "html.parser")

        flash_message = soup.find("ul", {"class": "flashes"})
        self.assertEqual(flash_message.find("li").text, "Please select a valid filter")


class TestSearchPage(TestWebPage):
    def setUp(self):
        super().setUp()
        self.page = "/search_history"
        self.response = self.client.get(self.page)
        self.soup = BeautifulSoup(self.response.data, "html.parser")

    def test_recommend_title(self):
        print(f"testing about {self.page} title is correct")
        self.assertEqual(self.soup.head.title.text, "BooksAnon: Search")


class TestSubmitPage(TestWebPage):
    def setUp(self):
        super().setUp()
        self.page = "/submit"
        self.response = self.client.get(self.page)
        self.soup = BeautifulSoup(self.response.data, "html.parser")

    def test_webpage_response(self):
        """Testing webpage response code"""
        print(f"Testing {self.page} rejects get requests")
        # submit page is only accessible through POST request
        # meaning expected result is 405
        response = self.client.get(self.page)
        self.assertEqual(response.status_code, 405)

    def test_navbar_has_loaded(self):
        print(f"testing navbar has is not viewable loaded on {self.page}")
        nav_links = self.soup.find_all("a", {"class": "nav-link"})
        self.assertEqual([], nav_links)


if __name__ == "__main__":
    unittest.main()
