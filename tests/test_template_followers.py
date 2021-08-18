"""
Test /u/<user_url_slug/followers/index.html URLs.

EECS 485 Project 1

Andrew DeOrio <awdeorio@umich.edu>
"""
import shutil
import re
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
    assert Path(tmpdir/"u/awdeorio/followers/index.html").exists()
    assert Path(tmpdir/"u/michjc/followers/index.html").exists()
    assert Path(tmpdir/"u/jag/followers/index.html").exists()
    assert Path(tmpdir/"u/jflinn/followers/index.html").exists()

    # Verify template uses jinja, not hardcoded HTML
    utils.assert_template_not_hardcoded("insta485/templates/followers.html")


def test_awdeorio_followers():
    """Check content at /u/awdeorio/followers/index.html URL."""
    tmpdir = TMPDIR/"insta485_html"
    shutil.rmtree(tmpdir, ignore_errors=True)
    subprocess.run(["insta485generator", "insta485", "-o", tmpdir], check=True)
    with open(tmpdir/"u/awdeorio/followers/index.html") as infile:
        soup = bs4.BeautifulSoup(infile, "html.parser")
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)
    links = [x.get("href") for x in soup.find_all("a")]
    srcs = [x.get("src") for x in soup.find_all('img')]

    # Every page should have these
    assert "/" in links
    assert "/explore/" in links
    assert "/u/awdeorio/" in links

    # Links specific to /u/awdeorio/followers/
    assert "/u/jflinn/" in links
    assert "/u/michjc/" in links
    assert "/u/jag/" not in links

    # Check for images
    assert "/uploads/5ecde7677b83304132cb2871516ea50032ff7a4f.jpg" in srcs
    assert "/uploads/505083b8b56c97429a728b68f31b0b2a089e5113.jpg" in srcs
    assert "/uploads/73ab33bd357c3fd42292487b825880958c595655.jpg" not in srcs

    # Check for text
    assert text.count("following") == 2
    assert "not following" not in text

    # Verify template uses jinja, not hardcoded HTML
    utils.assert_template_not_hardcoded("insta485/templates/followers.html")


def test_michjc_followers():
    """Check content at /u/michjc/followers/index.html URL."""
    tmpdir = TMPDIR/"insta485_html"
    shutil.rmtree(tmpdir, ignore_errors=True)
    subprocess.run(["insta485generator", "insta485", "-o", tmpdir], check=True)
    with open(tmpdir/"u/michjc/followers/index.html") as infile:
        soup = bs4.BeautifulSoup(infile, "html.parser")
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)
    links = [x.get("href") for x in soup.find_all("a")]
    srcs = [x.get("src") for x in soup.find_all('img')]

    # Every page should have these
    assert "/" in links
    assert "/explore/" in links
    assert "/u/awdeorio/" in links
    # Links specific to /u/michjc/followers/
    assert "/u/jflinn/" in links
    assert "/u/jag/" in links
    assert "/u/michjc/" not in links

    # Check for images
    assert "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg" in srcs
    assert "/uploads/73ab33bd357c3fd42292487b825880958c595655.jpg" in srcs
    assert "/uploads/505083b8b56c97429a728b68f31b0b2a089e5113.jpg" in srcs
    assert "/uploads/5ecde7677b83304132cb2871516ea50032ff7a4f.jpg" not in srcs

    # Check for text
    assert text.count("following") == 2
    assert text.count("not following") == 1

    # Verify template uses jinja, not hardcoded HTML
    utils.assert_template_not_hardcoded("insta485/templates/followers.html")


def test_jag_followers():
    """Check content at /u/jag/followers/index.html URL."""
    tmpdir = TMPDIR/"insta485_html"
    shutil.rmtree(tmpdir, ignore_errors=True)
    subprocess.run(["insta485generator", "insta485", "-o", tmpdir], check=True)
    with open(tmpdir/"u/jag/followers/index.html") as infile:
        soup = bs4.BeautifulSoup(infile, "html.parser")
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)
    srcs = [x.get("src") for x in soup.find_all('img')]
    links = [x.get("href") for x in soup.find_all("a")]

    # Every page should have these
    assert "/" in links
    assert "/explore/" in links
    assert "/u/awdeorio/" in links

    # Check for images
    assert "/uploads/5ecde7677b83304132cb2871516ea50032ff7a4f.jpg" in srcs
    assert "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg" not in srcs
    assert "/uploads/73ab33bd357c3fd42292487b825880958c595655.jpg" not in srcs
    assert "/uploads/505083b8b56c97429a728b68f31b0b2a089e5113.jpg"not in srcs

    # Links specific to /u/michjc/followers/
    assert "/u/michjc/" in links
    assert "/u/jflinn/" not in links
    assert "/u/jag/" not in links

    # Check for text
    assert "following" in text
    assert "not following" not in text

    # Verify template uses jinja, not hardcoded HTML
    utils.assert_template_not_hardcoded("insta485/templates/followers.html")


def test_jflinn_followers():
    """Check content at /u/jflinn/followers/index.html URL."""
    tmpdir = TMPDIR/"insta485_html"
    shutil.rmtree(tmpdir, ignore_errors=True)
    subprocess.run(["insta485generator", "insta485", "-o", tmpdir], check=True)
    with open(tmpdir/"u/jflinn/followers/index.html") as infile:
        soup = bs4.BeautifulSoup(infile, "html.parser")
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)
    srcs = [x.get("src") for x in soup.find_all('img')]
    links = [x.get("href") for x in soup.find_all("a")]

    # Every page should have these
    assert "/" in links
    assert "/explore/" in links
    assert "/u/awdeorio/" in links

    # Links specific to /u/michjc/followers/
    assert "/u/jflinn/" not in links
    assert "/u/jag/" not in links
    assert "/u/michjc/" not in links

    # Check for images
    assert "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg" in srcs
    assert "/uploads/5ecde7677b83304132cb2871516ea50032ff7a4f.jpg" not in srcs
    assert "/uploads/73ab33bd357c3fd42292487b825880958c595655.jpg" not in srcs
    assert "/uploads/505083b8b56c97429a728b68f31b0b2a089e5113.jpg" not in srcs

    # Check for text
    assert "not following" not in text
    assert "following" not in text

    # Verify template uses jinja, not hardcoded HTML
    utils.assert_template_not_hardcoded("insta485/templates/followers.html")
