"""Unit tests for infinite scroll on index page."""
import sqlite3
from urllib.parse import urljoin

import requests

import utils
import test_index


def test_infinite_scroll(live_server, driver):
    """Test infinite scroll.

    'live_server' is a fixture function that starts a live server.

    'driver' is a fixture fuction that provides access to a headless Chrome web
    browser via the Selenium library.

    Fixtures are implemented in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    # Delete all likes, comments and posts.  The default database contains
    # postids {1,2,3,4}.  We're going to delete those and add new posts later
    # in this test.  The new posts will start with postid=5.
    connection = sqlite3.connect("var/insta485.sqlite3")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("DELETE FROM likes")
    connection.execute("DELETE FROM comments")
    connection.execute("DELETE FROM posts")
    connection.commit()
    connection.close()

    # Create exactly 11 posts with "fox.jpg".  We're making requests directly
    # to the server-side dynamic pages server here, not using Selenium.
    session = requests.Session()
    response = session.get(live_server.url())
    assert response.status_code == 200

    accounts_url = urljoin(live_server.url(), "/accounts/")
    response = session.post(
        accounts_url,
        data={
            "operation": "login",
            "username": "awdeorio",
            "password": "password"
        }
    )
    assert response.status_code == 200
    pic_path = utils.TEST_DIR/"testdata/fox.jpg"
    post_url = urljoin(live_server.url(), "/posts/")
    for _ in range(11):
        with pic_path.open("rb") as pic:
            response = session.post(
                post_url,
                files={"file": pic},
                data={
                    "create_post": "upload new post",
                    "operation": "create"
                }
            )
        assert response.status_code == 200

    # Log in by reusing test from test_index
    test_index.test_login(live_server, driver)

    # Verify 10 most recent posts are on the page (postids 6-15 inclusive)
    for post_id in range(6, 15 + 1):
        assert driver.find_elements_by_xpath(
            f"//a[@href='/posts/{post_id}/']"
        )

    # Scroll to the bottom of the page
    utils.scroll_to_bottom_of_page(driver)

    # Verify there are 11 posts now
    assert driver.find_elements_by_xpath("//a[@href='/posts/5/']")


def test_infinite_scroll_many(live_server, driver):
    """Test many infinite scrolls.

    'live_server' is a fixture function that starts a live server.

    'driver' is a fixture fuction that provides access to a headless Chrome web
    browser via the Selenium library.

    Fixtures are implemented in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    # Delete all likes, comments and posts.  The default database contains
    # postids {1,2,3,4}.  We're going to delete those and add new posts later
    # in this test.  The new posts will start with postid=5.
    connection = sqlite3.connect("var/insta485.sqlite3")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("DELETE FROM likes")
    connection.execute("DELETE FROM comments")
    connection.execute("DELETE FROM posts")
    connection.commit()
    connection.close()

    # Create exactly 30 posts with "fox.jpg".  We're making requests directly
    # to the server-side dynamic pages server here, not using Selenium.
    session = requests.Session()
    response = session.get(live_server.url())
    assert response.status_code == 200

    accounts_url = urljoin(live_server.url(), "/accounts/")
    response = session.post(
        accounts_url,
        data={
            "operation": "login",
            "username": "awdeorio",
            "password": "password"
        }
    )
    assert response.status_code == 200
    pic_path = utils.TEST_DIR/"testdata/fox.jpg"
    post_url = urljoin(live_server.url(), "/posts/")
    for _ in range(30):
        with pic_path.open("rb") as pic:
            response = session.post(
                post_url,
                files={"file": pic},
                data={
                    "create_post": "upload new post",
                    "operation": "create"
                }
            )
        assert response.status_code == 200

    # Log in by reusing test from test_index
    test_index.test_login(live_server, driver)

    # Verify 10 newest posts are included.  Note: a side effect of this code is
    # to tell Selenium to wait until all 10 posts have been loaded.  Our
    # subsequent check for the number of posts depends on all 10 being loaded.
    for post_id in range(25, 34 + 1):
        assert driver.find_elements_by_xpath(
            f"//a[@href='/posts/{post_id}/']"
        )
    posts = driver.find_elements_by_xpath("//a[contains(@href, '/posts/')]")
    assert len(posts) == 10

    # Scroll to the bottom of the page
    utils.scroll_to_bottom_of_page(driver)

    # Verify 20 posts
    for post_id in range(15, 34 + 1):
        assert driver.find_elements_by_xpath(
            f"//a[@href='/posts/{post_id}/']"
        )
    posts = driver.find_elements_by_xpath("//a[contains(@href, '/posts/')]")
    assert len(posts) == 20

    # Scroll to the bottom of the page
    utils.scroll_to_bottom_of_page(driver)

    # Verify 30 posts
    for post_id in range(5, 34 + 1):
        assert driver.find_elements_by_xpath(
            f"//a[@href='/posts/{post_id}/']"
        )
    posts = driver.find_elements_by_xpath("//a[contains(@href, '/posts/')]")
    assert len(posts) == 30

    # Scroll to the bottom of the page a couple times, no errors
    utils.scroll_to_bottom_of_page(driver)
    utils.scroll_to_bottom_of_page(driver)
    utils.scroll_to_bottom_of_page(driver)


def test_scroll_refresh(live_server, driver):
    """Test infinite scroll with refresh afterward.

    Go to main page, scroll to trigger infinite scroll, make a post from
    background, refresh the page, make sure only 10 posts appear including
    the previously made, new post.

    'live_server' is a fixture function that starts a live server.

    'driver' is a fixture fuction that provides access to a headless Chrome web
    browser via the Selenium library.

    Fixtures are implemented in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    # Delete all likes, comments and posts.  The default database contains
    # postids {1,2,3,4}.  We're going to delete those and add new posts later
    # in this test.  The new posts will start with postid=5.
    connection = sqlite3.connect("var/insta485.sqlite3")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("DELETE FROM likes")
    connection.execute("DELETE FROM comments")
    connection.execute("DELETE FROM posts")
    connection.commit()
    connection.close()

    # Create exactly 11 posts with "fox.jpg".  We're making requests directly
    # to the server-side dynamic pages server here, not using Selenium.
    session = requests.Session()
    response = session.get(live_server.url())
    assert response.status_code == 200

    accounts_url = urljoin(live_server.url(), "/accounts/")
    response = session.post(
        accounts_url,
        data={
            "operation": "login",
            "username": "awdeorio",
            "password": "password"
        }
    )
    assert response.status_code == 200
    pic_path = utils.TEST_DIR/"testdata/fox.jpg"
    post_url = urljoin(live_server.url(), "/posts/")
    for _ in range(11):
        with pic_path.open("rb") as pic:
            response = session.post(
                post_url,
                files={"file": pic},
                data={
                    "create_post": "upload new post",
                    "operation": "create"
                }
            )
        assert response.status_code == 200

    # Log in by reusing test from test_index
    test_index.test_login(live_server, driver)

    # Verify 10 most recent posts are on the page (postids 2-11 inclusive)
    for post_id in range(6, 15 + 1):
        assert driver.find_elements_by_xpath(
            f"//a[@href='/posts/{post_id}/']"
        )

    # Scroll to the bottom of the page
    utils.scroll_to_bottom_of_page(driver)

    # Verify there are 11 posts now
    assert driver.find_elements_by_xpath("//a[@href='/posts/5/']")

    # Log in as jflinn and create a new post.  We're making requests directly
    # to the server-side dynamic pages server here, not using Selenium.
    test_index.jflinn_login_and_create_fox_post(live_server)

    # awdeorio refreshes the page
    driver.refresh()

    # Verify 10 most recent posts are on the page
    for post_id in range(7, 16 + 1):
        assert driver.find_elements_by_xpath(
            f"//a[@href='/posts/{post_id}/']"
        )
