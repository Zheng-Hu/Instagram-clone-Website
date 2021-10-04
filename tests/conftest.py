"""Shared test fixtures.

Pytest will automatically run the setup_teardown_selenium_driver() and
setup_teardown_live_server() functions before a test.  A test function should
use 'live_server' and 'driver' as inputs.

EXAMPLE:
>>> def test_anything(live_server, driver):
>>>     driver.get(live_server.url())
>>>     assert driver.find_elements_by_xpath(".//*")

Pytest fixture docs:
https://docs.pytest.org/en/latest/fixture.html#conftest-py-sharing-fixture-functions

Google Chrome: a web browser that supports headless browsing.

Selenium: a Python library for controlling a headless web browser.

Chromedriver: middle man executable between Selenium and Chrome.
"""
import logging
import socket
import subprocess
import threading
import time
import urllib
from pathlib import Path
import sqlite3

import flask
import pytest
import requests
import selenium
import selenium.webdriver
import insta485

# Set up logging
LOGGER = logging.getLogger("autograder")

# An implicit wait tells WebDriver to poll the DOM for a certain amount of
# time when trying to find any element (or elements) not immediately
# available. Once set, the implicit wait is set for the life of the
# WebDriver object.
#
# We'll need longer wait times on slow machines like the autograder.
#
# https://selenium-python.readthedocs.io/waits.html#implicit-waits
if Path("/home/autograder/working_dir").exists():
    IMPLICIT_WAIT_TIME = 30
else:
    IMPLICIT_WAIT_TIME = 10

# Implicit wait time when using a slow server
IMPLICIT_WAIT_TIME_SLOW_SERVER = 2 * IMPLICIT_WAIT_TIME

# Delay for intentionally slow REST API responses
SLOW_RESPONSE_DELAY = 0.5

# How long to wait for server in separate thread to start or stop
SERVER_START_STOP_TIMEOUT = 5


@pytest.fixture(name="chromedriver_path", scope="session")
def get_chromedriver_path():
    """
    Get path to chromedriver executable.

    This fixture is session-scoped since the chromedriver path will
    not change during the test run.
    """
    # If we are on the autograder, use chromedriver in the PATH.
    if Path("/home/autograder/working_dir").exists():
        return Path("chromedriver")

    node_modules_bin = subprocess.run(
        ["npm", "bin"],
        stdout=subprocess.PIPE,
        universal_newlines=True,
        check=True
    )
    node_modules_bin_path = node_modules_bin.stdout.strip()
    chromedriver_executable = Path(node_modules_bin_path) / "chromedriver"
    assert chromedriver_executable.exists()
    return chromedriver_executable


@pytest.fixture(name='app')
def setup_teardown_flask_app():
    """Configure a Flask app object to be used as a live server."""
    LOGGER.info("Setup test fixture 'app'")

    # Sanity check JavaScript distribution bundle.  If it doesn't exist or it's
    # out of date, generate it with webpack.
    bundle_path = Path("insta485/static/js/bundle.js")
    bundle_stale = False
    if bundle_path.exists():
        jsx_mtimes = [
            p.stat().st_mtime for p in Path("insta485/js").glob("*.jsx")
        ]
        bundle_mtime = bundle_path.stat().st_mtime
        bundle_stale = bundle_mtime < max(jsx_mtimes)
    if not bundle_path.exists() or bundle_stale:
        subprocess.run(["npx", "webpack"], check=True)

    # Reset the database
    subprocess.run(["bin/insta485db", "reset"], check=True)

    # Log requests to file. Later, we'll read the log to verify REST API
    # requests made by the client front end show up at the server backend.  We
    # need to log to a file, not an in-memory object because our live server
    # which creates this log will be run in a separate thread.
    flask_log_path = Path("flask.log")
    if flask_log_path.exists():
        flask_log_path.unlink()
    werkzeug_logger = logging.getLogger("werkzeug")
    assert not werkzeug_logger.handlers, "Unexpected handler already attached"
    werkzeug_logger.setLevel("INFO")
    werkzeug_logger.addHandler(logging.FileHandler("flask.log"))

    # Configure Flask app.  Testing mode so that exceptions are propagated
    # rather than handled by the the app's error handlers.
    insta485.app.config["TESTING"] = True

    # Transfer control to test.  The code before the "yield" statement is setup
    # code, which is executed before the test.  Code after the "yield" is
    # teardown code, which is executed at the end of the test.  Teardown code
    # is executed whether the test passed or failed.
    yield insta485.app

    # Teardown code starts here
    LOGGER.info("Teardown test fixture 'app'")
    werkzeug_logger.handlers.clear()
    flask_log_path.unlink()


@pytest.fixture(name='live_server')
def setup_teardown_live_server(app):
    """Start app in a separate thread."""
    LOGGER.info("Setup test fixture 'live_server'")

    # Start server.  It will automatically find an open port.
    live_server = LiveServer(app)
    live_server.start()

    # Transfer control to testcase
    yield live_server

    # Stop server
    LOGGER.info("Teardown test fixture 'live_server'")
    live_server.stop()


@pytest.fixture(name='driver')
def setup_teardown_selenium_driver(chromedriver_path):
    """Configure Selenium library to connect to a headless Chrome browser."""
    LOGGER.info("Setup test fixture 'driver'")

    # Configure Selenium
    #
    # Pro-tip: remove the "headless" option and set a breakpoint.  A Chrome
    # browser window will open, and you can play with it using the developer
    # console.
    options = selenium.webdriver.chrome.options.Options()

    # Don't open a browser GUI window
    options.add_argument("--headless")

    # Prevent issues in the Autograder Docker container
    options.add_argument("--no-sandbox")

    # More Autograder Docker container issues. By default, Docker runs a
    # container with a /dev/shm shared memory space of 64MB, which is too small
    # for Chrome and will cause Chrome to crash when rendering large
    # pages. This argument tells Chrome driver to write shared memory files
    # into /tmp instead of /dev/shm.
    options.add_argument("--disable-dev-shm-usage")

    # We use the "capabilities" object to access the Chrome logs, which is
    # similar to what you'd see in the developer console.   Later, we'll use
    # the logs to check for JavaScript exceptions.
    # Docs: https://stackoverflow.com/questions/44991009/
    capabilities = selenium.webdriver.common.desired_capabilities.\
        DesiredCapabilities.CHROME
    capabilities['goog:loggingPrefs'] = {'browser': 'SEVERE'}

    driver = selenium.webdriver.Chrome(
        options=options,
        desired_capabilities=capabilities,
        executable_path=str(chromedriver_path),
    )

    # An implicit wait tells WebDriver to poll the DOM for a certain amount of
    # time when trying to find any element (or elements) not immediately
    # available. Once set, the implicit wait is set for the life of the
    # WebDriver object.
    #
    # https://selenium-python.readthedocs.io/waits.html#implicit-waits
    driver.implicitly_wait(IMPLICIT_WAIT_TIME)
    LOGGER.info("IMPLICIT_WAIT_TIME=%s", IMPLICIT_WAIT_TIME)

    # Transfer control to test.  The code before the "yield" statement is setup
    # code, which is executed before the test.  Code after the "yield" is
    # teardown code, which is executed at the end of the test.  Teardown code
    # is executed whether the test passed or failed.
    yield driver

    # Teardown code starts here
    LOGGER.info("Teardown test fixture 'driver'")

    # Verify no errors in the browser console such as JavaScript exceptions
    # or failed page loads
    console_log = [err["message"] for err in driver.get_log("browser")]
    # Allow errors related to favicon.ico and third-party CSS frameworks
    error_exceptions = ["favicon.ico", "css"]
    console_log_errors = list(
        filter(
            lambda x: all(exp not in x.lower() for exp in error_exceptions),
            console_log,
        )
    )

    # Clean up the browser processes started by Selenium
    driver.quit()

    errors = "\n".join(console_log_errors)
    assert not console_log_errors,\
        f"Errors in browser console:\n{errors}"


@pytest.fixture(name='slow_driver')
def setup_teardown_selenium_slow_driver(driver):
    """Replicate 'driver' fixture, but with a longer timeout."""
    LOGGER.info("Setup test fixture 'slow_driver'")

    # Increase the implicit wait time
    driver.implicitly_wait(IMPLICIT_WAIT_TIME_SLOW_SERVER)
    LOGGER.info(
        "IMPLICIT_WAIT_TIME_SLOW_SERVER=%s ",
        IMPLICIT_WAIT_TIME_SLOW_SERVER,
    )

    # Transfer control to test.  The code before the "yield" statement is setup
    # code, which is executed before the test.  Code after the "yield" is
    # teardown code, which is executed at the end of the test.  Teardown code
    # is executed whether the test passed or failed.
    yield driver

    # Teardown code starts here
    LOGGER.info("Teardown test fixture 'slow_driver'")


@pytest.fixture(name='slow_live_server')
def setup_teardown_slow_live_server(app):
    """Start app in a separate thread, configured to be artificially slow."""
    LOGGER.info("Setup test fixture 'slow_live_server'")

    # Create a LiveServer object, but don't start it yet
    slow_live_server = LiveServer(app)

    # Function object injects artificial delay
    def delay_request():
        """Delay Flask response to a request."""
        if "/api/v1/" not in flask.request.path:
            return
        LOGGER.info(
            'Delaying response %ss to request "%s %s"',
            SLOW_RESPONSE_DELAY, flask.request.method, flask.request.path,
        )
        time.sleep(SLOW_RESPONSE_DELAY)

    # Register delay as a callback to be executed before each request.  Verify
    # that this function is not already registered.
    for funcs in slow_live_server.app.before_request_funcs.values():
        assert delay_request not in funcs
    app.before_request(delay_request)

    # Start live server *after* registering callback
    slow_live_server.start()

    # Transfer control to test.  The code before the "yield" statement is setup
    # code, which is executed before the test.  Code after the "yield" is
    # teardown code, which is executed at the end of the test.  Teardown code
    # is executed whether the test passed or failed.
    yield slow_live_server

    # Teardown code starts here.  Unregister callback.
    LOGGER.info("Teardown test fixture 'slow_live_server'")
    slow_live_server.stop()
    for funcs in slow_live_server.app.before_request_funcs.values():
        if delay_request in funcs:
            funcs.remove(delay_request)


@pytest.fixture(name="client")
def client_setup_teardown():
    """
    Start a Flask test server with a clean database.

    This fixture is used to test the REST API, it won't start a live server.

    Flask docs: https://flask.palletsprojects.com/en/1.1.x/testing/#testing
    """
    LOGGER.info("Setup test fixture 'client'")

    # Reset the database
    subprocess.run(["bin/insta485db", "reset"], check=True)

    # Configure Flask test server
    insta485.app.config["TESTING"] = True

    # Transfer control to test.  The code before the "yield" statement is setup
    # code, which is executed before the test.  Code after the "yield" is
    # teardown code, which is executed at the end of the test.  Teardown code
    # is executed whether the test passed or failed.
    with insta485.app.test_client() as client:
        yield client

    # Teardown code starts here
    LOGGER.info("Teardown test fixture 'client'")


class LiveServer:
    """Represent a Flask app running in a separate thread."""

    def __init__(self, app, port=None):
        """Find an open port and create a thread object."""
        self.app = app
        self.port = self.get_open_port() if port is None else port

        def shutdown_server():
            """Shut down Flask's underlying Werkzeug WSGI server."""
            shutdown_func = flask.request.environ.get(
                "werkzeug.server.shutdown"
            )
            if shutdown_func is None:
                raise RuntimeError("Not running with a Werkzeug Server.")
            shutdown_func()
            return "Shutting down live server..."

        # Monkey-patch Flask app with a shutdown route at runtime.
        # This is required since threads do not have an elegant method for
        # terminating execution (e.g. a programatic ctrl+c to end the server).
        # More info: https://stackoverflow.com/a/17053522/3820660
        if "shutdown" not in self.app.view_functions:
            self.app.add_url_rule(
                "/shutdown/",
                endpoint="shutdown",
                view_func=shutdown_server,
                methods=["POST"]
            )

        # Run Flask app in a new thread. Debug mode, code reloading, and
        # threaded mode are disabled to prevent potential bugs.
        # Run thread in daemon mode to ensure that the thread is killed
        # when the main Python program exits (e.g. in the case of a test
        # failure, uncaught exception, or premature exit)
        self.thread = threading.Thread(
            target=self.app.run,
            name="LiveServer",
            kwargs=({
                "port": self.port,
                "debug": False,
                "use_reloader": False,
                "threaded": False,
            }),
            daemon=True
        )

    def url(self):
        """Return base URL of running server."""
        return f"http://localhost:{self.port}/"

    def start(self):
        """Start server."""
        self.thread.start()
        assert self.wait_for_urlopen()

    def stop(self):
        """Stop server."""
        shutdown_url = urllib.parse.urljoin(self.url(), "/shutdown/")
        # Clear before_request functions to prevent authentication hooks
        # from redirecting the request to the shutdown route. This only
        # impacts student solutions that harness before_request functions.
        self.app.before_request_funcs.clear()
        requests.post(shutdown_url)
        # Attempt to join with the main thread until the specified timeout.
        # If the LiveServer thread fails to join with the main thread
        # (e.g. join times out), we will leave the shutdown and cleanup
        # duties to the daemon thread when the Python process exits.
        self.thread.join(timeout=SERVER_START_STOP_TIMEOUT)

    @staticmethod
    def get_open_port():
        """Return a port that is available for use on localhost."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(('', 0))
            port = sock.getsockname()[1]
        return port

    def wait_for_urlopen(self):
        """Call urlopen() in a loop, returning False if it times out."""
        for _ in range(SERVER_START_STOP_TIMEOUT):
            try:
                with urllib.request.urlopen(self.url()):
                    return True
            except urllib.error.HTTPError as err:
                # HTTP 404 and friends indicate a working server
                if err.code < 500:
                    return True
            except urllib.error.URLError:
                pass
            time.sleep(1)
        return False


@pytest.fixture(name="db_connection")
def db_setup_teardown():
    """
    Create an in-memory sqlite3 database.

    This fixture is used only for the database tests, not the insta485 tests.
    """
    # Create a temporary in-memory database
    db_connection = sqlite3.connect(":memory:")

    # Configure database to return dictionaries keyed on column name
    def dict_factory(cursor, row):
        """Convert database row objects to a dict keyed on column name."""
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    db_connection.row_factory = dict_factory

    # Foreign keys have to be enabled per-connection.  This is an sqlite3
    # backwards compatibility thing.
    db_connection.execute("PRAGMA foreign_keys = ON")

    # Transfer control to test.  The code before the "yield" statement is setup
    # code, which is executed before the test.  Code after the "yield" is
    # teardown code, which is executed at the end of the test.  Teardown code
    # is executed whether the test passed or failed.
    yield db_connection

    # Verify foreign key support is still enabled
    cur = db_connection.execute("PRAGMA foreign_keys")
    foreign_keys_status = cur.fetchone()
    assert foreign_keys_status["foreign_keys"],\
        "Foreign keys appear to be disabled."

    # Destroy database
    db_connection.close()
