import unittest

from bs4 import BeautifulSoup
import requests

from app import app, query_db, TEST_DATABASE


class TestCase(unittest.TestCase):
    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()
        self.db = TEST_DATABASE

    def tearDown(self):
        self.ctx.pop()

    def test_homepage(self):
        """Tests for homepage"""
        print("Testing homepage loads with correct status code")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.data, "html.parser")

        print("testing homepage title is correct")
        self.assertEqual(soup.head.title.text, "BooksAnon: Recommendations")

        number_of_books = len(soup.find_all("tr"))

        # if database has loaded correctly
        # then there will be at least 2 table rows
        # one for header and one for a book from db
        print("testing some books from database have loaded")
        self.assertGreater(number_of_books, 2)

        print("testing correct number of books is showing")
        # table should have 11 rows max
        # 10 books listed and one header
        self.assertLessEqual(number_of_books, 11)

        print("testing navbar has loaded")
        nav_links = soup.find_all("a", {"class": "nav-link"})
        self.assertEqual(len(nav_links), 4)

        self.assertEqual(
            str(nav_links[0]), '<a class="nav-link" href="/recommend">Recommend</a>'
        )


if __name__ == "__main__":
    unittest.main()
