"""Unit tests for the index page when user is logged in.

Run with logs visible:
$ pytest -v --log-cli-level=INFO ../autograder/test_index.py
"""
import subprocess
from urllib.parse import urlparse, urljoin
from pathlib import Path
import requests
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import bs4
import utils


def test_anything(live_server, driver):
    """Verify server returns anything at all.

    'live_server' is a fixture function that starts a live server.

    'driver' is a fixture fuction that provides access to a headless Chrome web
    browser via the Selenium library.

    Fixtures are implemented in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    driver.get(live_server.url())
    assert driver.find_elements_by_xpath(".//*")


def test_login(live_server, driver):
    """Verify user awdeorio can log in.

    'live_server' is a fixture function that starts a live server.

    'driver' is a fixture fuction that provides access to a headless Chrome web
    browser via the Selenium library.

    Fixtures are implemented in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    # Load login page
    login_url = urljoin(live_server.url(), "/accounts/login")
    driver.get(login_url)
    assert driver.find_elements_by_xpath(".//*")

    # Log in
    assert driver.find_elements_by_name("username")
    assert driver.find_elements_by_name("password")
    username_field = driver.find_element_by_name("username")
    password_field = driver.find_element_by_name("password")
    username_field.send_keys("awdeorio")
    password_field.send_keys("password")
    submit_buttons = driver.find_elements_by_xpath(
        "//input[@type='submit' and @value='login']"
    )
    assert len(submit_buttons) == 1
    submit_button = submit_buttons[0]
    submit_button.click()

    # After logging in, we should be redirected to the "/" URL
    assert urlparse(driver.current_url).path == "/"

    # The "/" page should contain a React entry point called 'reactEntry'
    assert driver.find_elements_by_id("reactEntry")

    react_entry = driver.find_element_by_id("reactEntry")
    assert react_entry.find_elements_by_xpath(".//*"), \
        "Failed to find an element rendered by ReactJS"


def test_feed_load(live_server, driver):
    """Verify feed loads on index page.

    'live_server' is a fixture function that starts a live server.

    'driver' is a fixture fuction that provides access to a headless Chrome web
    browser via the Selenium library.

    Fixtures are implemented in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    test_login(live_server, driver)

    # Verify react is being used
    assert driver.find_elements_by_tag_name("script")
    script_element = driver.find_element_by_tag_name("script")
    assert "/static/js/bundle.js" in script_element.get_attribute("src")
    assert script_element.get_attribute("type") == 'text/javascript'

    # Verify links
    assert driver.find_elements_by_xpath("//a[@href='/posts/1/']")
    assert driver.find_elements_by_xpath("//a[@href='/posts/2/']")
    assert driver.find_elements_by_xpath("//a[@href='/posts/3/']")
    assert driver.find_elements_by_xpath("//a[@href='/users/awdeorio/']")
    assert driver.find_elements_by_xpath("//a[@href='/users/jflinn/']")
    assert driver.find_elements_by_xpath("//a[@href='/users/michjc/']")

    # Verify images
    assert driver.find_elements_by_xpath(  # Flinn
        "//img[@src='/uploads/505083b8b56c97429a728b68f31b0b2a089e5113.jpg']"
    )
    assert driver.find_elements_by_xpath(  # DeOrio
        "//img[@src='/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg']"
    )
    assert driver.find_elements_by_xpath(  # Postid 1
        "//img[@src='/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg']"
    )
    assert driver.find_elements_by_xpath(  # Postid 2
        "//img[@src='/uploads/ad7790405c539894d25ab8dcf0b79eed3341e109.jpg']"
    )
    assert driver.find_elements_by_xpath(
        "//img[@src='/uploads/9887e06812ef434d291e4936417d125cd594b38a.jpg']"
    )

    # Verify text
    assert driver.find_elements_by_xpath(
        "//*[normalize-space(text()) = '#chickensofinstagram']"
    )
    assert driver.find_elements_by_xpath(
        "//*[normalize-space(text()) = 'I <3 chickens']"
    )
    assert driver.find_elements_by_xpath(
        "//*[normalize-space(text()) = 'Cute overload!']"
    )
    assert driver.find_elements_by_xpath(
        "//*[normalize-space(text()) = 'Sick #crossword']"
    )
    assert driver.find_elements_by_xpath(
        "//*[normalize-space(text()) = '"
        "Walking the plank #chickensofinstagram"
        "']"
    )
    assert driver.find_elements_by_xpath(
        "//*[normalize-space(text()) = '"
        "This was after trying to teach them to do a #crossword"
        "']"
    )

    # Verify REST API requests.  A parallel process is writing the log, so we
    # need to wait for it to finish writing.
    flask_log = utils.wait_for_api_calls("flask.log", n_calls=1)
    assert "GET /api/v1/posts/" in flask_log


def test_new_comment(live_server, driver):
    """Verify new comment appears without refresh.

    'live_server' is a fixture function that starts a live server.

    'driver' is a fixture fuction that provides access to a headless Chrome web
    browser via the Selenium library.

    Fixtures are implemented in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    test_feed_load(live_server, driver)

    # Clear the Flask request log
    Path("flask.log").write_text("", encoding='utf-8')

    # Find comment field on for postid 3, which is the first one on the page
    comment_fields = driver.find_elements_by_xpath(
        "//form[contains(@class, 'comment-form')]//input[@type='text']"
    )
    assert comment_fields
    comment_field = comment_fields[0]

    # Type into comment field and submit by typing "enter"
    comment_field.send_keys("test comment")
    comment_field.send_keys(Keys.RETURN)

    # Verify new comment exists
    assert driver.find_elements_by_xpath(
        "//*[text()[contains(.,'test comment')]]"
    )

    # Verify REST API POST request from new comment is the *only* new request.
    # A parallel process is writing the log, so we need to wait for it to
    # finish writing.
    flask_log = utils.wait_for_api_calls("flask.log", n_calls=1)
    assert flask_log.count('\n') == 1, flask_log
    assert "POST /api/v1/comments/?postid=3" in flask_log


def test_delete_comment(live_server, driver):
    """Verify delete comment button works properly.

    live_server' is a fixture function that starts a live server.

    'driver' is a fixture fuction that provides access to a headless Chrome web
    browser via the Selenium library.

    Fixtures are implemented in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    test_feed_load(live_server, driver)

    # Clear the Flask request log
    Path("flask.log").write_text("", encoding='utf-8')

    # Verify awdeorio comment on post 3 exists
    assert driver.find_elements_by_xpath(
        "//*[text()[contains(.,'#chickensofinstagram')]]"
    )

    # Click the first delete button
    delete_buttons = driver.find_elements_by_xpath(
        "//button[contains(@class, 'delete-comment-button')]"
    )
    assert len(delete_buttons) == 3
    delete_button = delete_buttons[0]
    delete_button.click()

    # Verify REST API DELETE request from awdeorio's comment
    # is the *only* new request.
    # A parallel process is writing the log, so we need to wait for it to
    # finish writing.
    flask_log = utils.wait_for_api_calls("flask.log", n_calls=1)
    assert flask_log.count('\n') == 1, flask_log
    assert "DELETE /api/v1/comments/1/" in flask_log

    # Verify awdeorio comment on post 3 does not exists
    cur_comment = driver.find_elements_by_xpath(
        "//*[text()[contains(.,'#chickensofinstagram')]]"
    )
    # There are originally two comments with #chickensofinstagram
    # We deleted the first one
    assert len(cur_comment) == 1

    # Verify there is one less button
    delete_buttons = driver.find_elements_by_xpath(
        "//button[contains(@class, 'delete-comment-button')]"
    )
    assert len(delete_buttons) == 2


def test_new_comment_delete(live_server, driver):
    """Verify new comment appears without refresh.

    'live_server' is a fixture function that starts a live server.

    'driver' is a fixture fuction that provides access to a headless Chrome web
    browser via the Selenium library.

    Fixtures are implemented in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    test_feed_load(live_server, driver)

    # Clear the Flask request log
    Path("flask.log").write_text("", encoding='utf-8')

    # Find comment field on for postid 3, which is the first one on the page
    comment_fields = driver.find_elements_by_xpath(
        "//form[contains(@class, 'comment-form')]//input[@type='text']"
    )
    assert comment_fields
    comment_field = comment_fields[0]

    # Type into comment field and submit by typing "enter"
    comment_field.send_keys("test comment")
    comment_field.send_keys(Keys.RETURN)

    # Verify new comment exists
    assert driver.find_elements_by_xpath(
        "//*[text()[contains(.,'test comment')]]"
    )

    # Verify REST API POST request from new comment is the *only* new request.
    # A parallel process is writing the log, so we need to wait for it to
    # finish writing.
    flask_log = utils.wait_for_api_calls("flask.log", n_calls=1)
    assert flask_log.count('\n') == 1, flask_log
    assert "POST /api/v1/comments/?postid=3" in flask_log

    # Clear the Flask request log
    Path("flask.log").write_text("", encoding='utf-8')

    # Click the second delete button which should be for new comment
    delete_buttons = driver.find_elements_by_xpath(
        "//button[contains(@class, 'delete-comment-button')]"
    )
    assert len(delete_buttons) == 4
    delete_button = delete_buttons[1]
    delete_button.click()

    # Verify REST API DELETE request for new comment is the *only* new request.
    # A parallel process is writing the log, so we need to wait for it to
    # finish writing.
    flask_log = utils.wait_for_api_calls("flask.log", n_calls=1)
    assert flask_log.count('\n') == 1, flask_log
    assert "DELETE /api/v1/comments/8/" in flask_log

    # Verify new comment does not exists
    cur_comment = driver.find_elements_by_xpath(
        "//*[text()[contains(.,'test comment')]]"
    )
    assert len(cur_comment) == 0

    # Verify there is one less button
    delete_buttons = driver.find_elements_by_xpath(
        "//button[contains(@class, 'delete-comment-button')]"
    )
    assert len(delete_buttons) == 3


def test_like_unlike(live_server, driver):
    """Verify like/unlike button behavior without refresh.

    'live_server' is a fixture function that starts a live server.

    'driver' is a fixture fuction that provides access to a headless Chrome web
    browser via the Selenium library.

    Fixtures are implemented in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    test_feed_load(live_server, driver)

    # Clear the Flask request log
    Path("flask.log").write_text("", encoding='utf-8')

    # Click the first like button
    like_buttons = driver.find_elements_by_xpath(
        "//button[contains(@class, 'like-unlike-button')]"
    )
    assert len(like_buttons) == 3
    like_button = like_buttons[0]
    like_button.click()

    # First post started with 1 like by awdeorio, now it should be 0
    assert driver.find_elements_by_xpath("//*[normalize-space() = '0 likes']")

    # Click the first like button again
    like_buttons = driver.find_elements_by_xpath(
        "//button[contains(@class, 'like-unlike-button')]"
    )
    assert len(like_buttons) == 3
    like_button = like_buttons[0]
    like_button.click()

    # First post should now have 1 like
    assert driver.find_elements_by_xpath("//*[normalize-space() = '1 like']")

    # Verify REST API requests from like and unlike are the *only* new
    # requests.  A parallel process is writing the log, so we need to wait for
    # it to finish writing.
    flask_log = utils.wait_for_api_calls("flask.log", n_calls=2)
    assert flask_log.count('\n') == 2, flask_log
    assert "DELETE /api/v1/likes/6" in flask_log
    assert "POST /api/v1/likes/?postid=3" in flask_log


def test_double_click_like(live_server, driver):
    """
    Verify double clicking on an unliked image likes the image.

    Load main page, unlike first image, perform two double clicks on it,
    the first of which should like the image, the second should have no effect.

    'live_server' is a fixture function that starts a live server.

    'driver' is a fixture fuction that provides access to a headless Chrome web
    browser via the Selenium library.

    Fixtures are implemented in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    test_feed_load(live_server, driver)

    # Clear the Flask request log
    Path("flask.log").write_text("", encoding='utf-8')

    # Check that the like buttons exist
    like_buttons = driver.find_elements_by_xpath(
        "//button[contains(@class, 'like-unlike-button')]"
    )
    assert len(like_buttons) == 3

    # Click the like button for the first image
    # This will unlike the image which is already liked
    like_button = like_buttons[0]
    like_button.click()

    # First post started with 1 like, now it should be 0
    assert driver.find_elements_by_xpath("//*[normalize-space() = '0 likes']")

    # Verify first image exists
    images = driver.find_elements_by_xpath(
        "//img[@src='/uploads/9887e06812ef434d291e4936417d125cd594b38a.jpg']"
    )
    # assert that exactly one copy of the image exists on the page
    assert images
    assert len(images) == 1

    jflinn_post_image = images[0]

    # Perform double click on the first image
    # this should like the image again
    action_chains = ActionChains(driver)
    action_chains.double_click(jflinn_post_image).perform()

    # First post started with 1 like, now it should be 0
    assert driver.find_elements_by_xpath("//*[normalize-space() = '1 like']")

    # Perform another double click, this shouldn't do anything
    # because the image is already liked
    action_chains.double_click(jflinn_post_image).perform()

    # First post started with 1 like, now it should be 0
    assert driver.find_elements_by_xpath("//*[normalize-space() = '1 like']")

    # Verify REST API requests from like and unlike are the *only* new
    # requests.  A parallel process is writing the log, so we need to wait for
    # it to finish writing.
    flask_log = utils.wait_for_api_calls("flask.log", n_calls=2)
    assert flask_log.count('\n') == 2, flask_log
    assert "DELETE /api/v1/likes/6" in flask_log
    assert "POST /api/v1/likes/?postid=3" in flask_log


def jflinn_login_and_create_fox_post(live_server):
    """Log in as jflinn and create a post.

    This is a helper function, not a test.
    """
    session = requests.Session()
    response = session.get(live_server.url())
    assert response.status_code == 200

    accounts_url = urljoin(live_server.url(), "/accounts/")
    response = session.post(
        accounts_url,
        data={
            "operation": "login",
            "username": "jflinn",
            "password": "password"
        }
    )
    assert response.status_code == 200
    pic_path = utils.TEST_DIR/"testdata/fox.jpg"
    post_url = urljoin(live_server.url(), "/posts/")
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


def test_refresh(live_server, driver):
    """Verify refresh with content from another client.

    Load main page, create new post via another client, refresh the page,
    make sure both old posts and new post appear.

    'live_server' is a fixture function that starts a live server.

    'driver' is a fixture fuction that provides access to a headless Chrome web
    browser via the Selenium library.

    Fixtures are implemented in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    test_feed_load(live_server, driver)

    # Log in as jflinn and create a new post.  We're making requests directly
    # to the server-side dynamic pages server here, not using Selenium.
    jflinn_login_and_create_fox_post(live_server)

    # Clear Flask request log
    Path("flask.log").write_text("", encoding='utf-8')

    # Refresh
    driver.refresh()

    # Verify posts on page: 1,2,3 are old, 5 is new
    assert driver.find_elements_by_xpath("//a[@href='/posts/1/']")
    assert driver.find_elements_by_xpath("//a[@href='/posts/2/']")
    assert driver.find_elements_by_xpath("//a[@href='/posts/3/']")
    assert driver.find_elements_by_xpath("//a[@href='/posts/5/']")

    # Verify REST API requests.  A parallel process is writing the log, so we
    # need to wait for it to finish writing.
    flask_log = utils.wait_for_api_calls("flask.log", n_calls=1)
    assert "GET /api/v1/posts/" in flask_log


def test_html(live_server, driver):
    """Verify HTML5 compliance in HTML portion of the index page.

    'live_server' is a fixture function that starts a live server.

    'driver' is a fixture fuction that provides access to a headless Chrome web
    browser via the Selenium library.

    Fixtures are implemented in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    test_feed_load(live_server, driver)

    # Clean up
    index_path = utils.TMPDIR/"index.html"
    if index_path.exists():
        index_path.unlink()
    utils.TMPDIR.mkdir(exist_ok=True)

    # Prettify the HTML for easier debugging
    html = "<!DOCTYPE html>" + driver.page_source  # Selenium strips DOCTYPE
    soup = bs4.BeautifulSoup(html, "html.parser")
    html = soup.prettify()

    # Write HTML of current page source to file
    index_path.write_text(html, encoding='utf-8')

    # Run html5validator on the saved file
    print("html5validator tmp/index.html")
    subprocess.run(
        ["html5validator", "--ignore=JAVA_TOOL_OPTIONS", "tmp/index.html"],
        check=True,
    )
