import unittest

from bs4 import BeautifulSoup

from app import app, TEST_DATABASE


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


class TestRecommendPage(TestWebPage):
    def setUp(self):
        super().setUp()
        self.page = "/recommend"
        self.response = self.client.get(self.page)
        self.soup = BeautifulSoup(self.response.data, "html.parser")

    def test_recommend_title(self):
        print(f"testing about {self.page} title is correct")
        self.assertEqual(self.soup.head.title.text, "BooksAnon: Recommend")


class TestHistoryPage(TestWebPage):
    def setUp(self):
        super().setUp()
        self.page = "/history"
        self.response = self.client.get(self.page)
        self.soup = BeautifulSoup(self.response.data, "html.parser")

    def test_recommend_title(self):
        print(f"testing about {self.page} title is correct")
        self.assertEqual(self.soup.head.title.text, "BooksAnon: History")


class TestSearchPage(TestWebPage):
    def setUp(self):
        super().setUp()
        self.page = "/search_history"
        self.response = self.client.get(self.page)
        self.soup = BeautifulSoup(self.response.data, "html.parser")

    def test_recommend_title(self):
        print(f"testing about {self.page} title is correct")
        self.assertEqual(self.soup.head.title.text, "BooksAnon: Search")


if __name__ == "__main__":
    unittest.main()
