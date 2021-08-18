"""
Test /u/<user_url_slug/following/index.html URLs.

EECS 485 Project 1

Andrew DeOrio <awdeorio@umich.edu>
"""
import shutil
import subprocess
from pathlib import Path
import bs4
import utils
from utils import TMPDIR


def test_files():
    """Verify all expected files exist."""
    tmpdir = TMPDIR/"insta485_html"
    shutil.rmtree(tmpdir, ignore_errors=True)
    subprocess.run(["insta485generator", "insta485", "-o", tmpdir], check=True)
    assert Path(tmpdir/"u/awdeorio/following/index.html").exists()
    assert Path(tmpdir/"u/michjc/following/index.html").exists()
    assert Path(tmpdir/"u/jag/following/index.html").exists()
    assert Path(tmpdir/"u/jflinn/following/index.html").exists()

    # Verify template uses jinja, not hardcoded HTML
    utils.assert_template_not_hardcoded("insta485/templates/following.html")


def test_awdeorio_following():
    """Check content at /u/awdeorio/following/index.html URL."""
    tmpdir = TMPDIR/"insta485_html"
    shutil.rmtree(tmpdir, ignore_errors=True)
    subprocess.run(["insta485generator", "insta485", "-o", tmpdir], check=True)

    # Parse HTML, then convert all whitespace to single spaces
    with open(tmpdir/"u/awdeorio/following/index.html") as infile:
        soup = bs4.BeautifulSoup(infile, "html.parser")
    text = soup.get_text()
    srcs = [x.get("src") for x in soup.find_all('img')]
    links = [x.get("href") for x in soup.find_all("a")]

    # Every page should have these
    assert "/" in links
    assert "/explore/" in links
    assert "/u/awdeorio/" in links

    # Check for text
    assert text.count("following") == 2
    assert "not following" not in text

    # Check for images
    assert "/uploads/5ecde7677b83304132cb2871516ea50032ff7a4f.jpg" in srcs
    assert "/uploads/505083b8b56c97429a728b68f31b0b2a089e5113.jpg" in srcs
    assert "/uploads/73ab33bd357c3fd42292487b825880958c595655.jpg" not in srcs

    # Links specific to /u/awdeorio/followers/
    assert "/u/jflinn/" in links
    assert "/u/michjc/" in links
    assert "/u/jag/" not in links


def test_michjc_following():
    """Check content at /u/michjc/following/index.html URL."""
    tmpdir = TMPDIR/"insta485_html"
    shutil.rmtree(tmpdir, ignore_errors=True)
    subprocess.run(["insta485generator", "insta485", "-o", tmpdir], check=True)
    with open(tmpdir/"u/michjc/following/index.html") as infile:
        soup = bs4.BeautifulSoup(infile, "html.parser")
    srcs = [x.get("src") for x in soup.find_all('img')]
    links = [x.get("href") for x in soup.find_all("a")]

    # Every page should have these
    assert "/" in links
    assert "/explore/" in links
    assert "/u/awdeorio/" in links

    # Links specific to /u/michjc/followers/
    assert "/u/jflinn/" not in links
    assert "/u/michjc/" not in links

    # Check for images
    assert "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg" in srcs
    assert "/uploads/5ecde7677b83304132cb2871516ea50032ff7a4f.jpg" not in srcs
    assert "/uploads/505083b8b56c97429a728b68f31b0b2a089e5113.jpg" not in srcs

    # Verify template uses jinja, not hardcoded HTML
    utils.assert_template_not_hardcoded("insta485/templates/following.html")


def test_jag_following():
    """Check content at /u/jag/following/index.html URL."""
    tmpdir = TMPDIR/"insta485_html"
    shutil.rmtree(tmpdir, ignore_errors=True)
    subprocess.run(["insta485generator", "insta485", "-o", tmpdir], check=True)
    with open(tmpdir/"u/jag/following/index.html") as infile:
        soup = bs4.BeautifulSoup(infile, "html.parser")
    text = soup.get_text()
    srcs = [x.get("src") for x in soup.find_all('img')]
    links = [x.get("href") for x in soup.find_all("a")]

    # Every page should have these
    assert "/" in links
    assert "/explore/" in links
    assert "/u/awdeorio/" in links

    # Links specific to /u/michjc/followers/
    assert "/u/jflinn/" not in links
    assert "/u/jag/" not in links
    assert "/u/michjc/" in links

    # Check for images
    assert "/uploads/5ecde7677b83304132cb2871516ea50032ff7a4f.jpg" in srcs
    assert "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg" not in srcs
    assert "/uploads/73ab33bd357c3fd42292487b825880958c595655.jpg" not in srcs
    assert "/uploads/505083b8b56c97429a728b68f31b0b2a089e5113.jpg" not in srcs

    # Check for text
    assert "following" in text
    assert "not following" not in text

    # Verify template uses jinja, not hardcoded HTML
    utils.assert_template_not_hardcoded("insta485/templates/following.html")


def test_jflinn_following():
    """Check content at /u/jflinn/following/index.html URL."""
    tmpdir = TMPDIR/"insta485_html"
    shutil.rmtree(tmpdir, ignore_errors=True)
    subprocess.run(["insta485generator", "insta485", "-o", tmpdir], check=True)
    with open(tmpdir/"u/jflinn/following/index.html") as infile:
        soup = bs4.BeautifulSoup(infile, "html.parser")
    text = soup.get_text()
    srcs = [x.get("src") for x in soup.find_all('img')]
    links = [x.get("href") for x in soup.find_all("a")]

    # Every page should have these
    assert "/" in links
    assert "/explore/" in links
    assert "/u/awdeorio/" in links
    # Links specific to /u/michjc/followers/
    assert "/u/michjc/" in links
    assert "/u/jflinn/" not in links
    assert "/u/jag/" not in links

    # Check for images
    assert "/uploads/5ecde7677b83304132cb2871516ea50032ff7a4f.jpg" in srcs
    assert "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg" in srcs

    assert "/uploads/73ab33bd357c3fd42292487b825880958c595655.jpg" not in srcs
    assert "/uploads/505083b8b56c97429a728b68f31b0b2a089e5113.jpg" not in srcs

    # Check for text
    assert "not following" not in text
    assert text.count("following") == 1

    # Verify template uses jinja, not hardcoded HTML
    utils.assert_template_not_hardcoded("insta485/templates/following.html")
