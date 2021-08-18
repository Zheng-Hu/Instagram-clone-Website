"""
Check index page at /index.html URL.

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
    """Verify jinja is used properly."""
    tmpdir = TMPDIR/"insta485_html"
    shutil.rmtree(tmpdir, ignore_errors=True)
    subprocess.run(["insta485generator", "insta485", "-o", tmpdir], check=True)
    assert Path(tmpdir/"index.html").exists()

    # Verify template uses jinja, not hardcoded HTML
    utils.assert_template_not_hardcoded("insta485/templates/index.html")


def test_images():
    """Verify all images are present in / URL."""
    tmpdir = TMPDIR/"insta485_html"
    shutil.rmtree(tmpdir, ignore_errors=True)
    subprocess.run(["insta485generator", "insta485", "-o", tmpdir], check=True)

    # Parse HTML, then extract image source urls
    with open(tmpdir/"index.html") as infile:
        soup = bs4.BeautifulSoup(infile, "html.parser")
    srcs = [x.get("src") for x in soup.find_all('img')]

    # Verify images present of Flinn, DeOrio, postid 1, postid 2, postid 3
    assert "/uploads/505083b8b56c97429a728b68f31b0b2a089e5113.jpg" in srcs
    assert "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg" in srcs
    assert "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg" in srcs
    assert "/uploads/ad7790405c539894d25ab8dcf0b79eed3341e109.jpg" in srcs
    assert "/uploads/9887e06812ef434d291e4936417d125cd594b38a.jpg" in srcs

    # Verify template uses jinja, not hardcoded HTML
    utils.assert_template_not_hardcoded("insta485/templates/index.html")


def test_links():
    """Verify expected links present in / URL."""
    tmpdir = TMPDIR/"insta485_html"
    shutil.rmtree(tmpdir, ignore_errors=True)
    subprocess.run(["insta485generator", "insta485", "-o", tmpdir], check=True)

    # Parse HTML, then extract image source urls
    with open(tmpdir/"index.html") as infile:
        soup = bs4.BeautifulSoup(infile, "html.parser")
    links = [x.get("href") for x in soup.find_all("a")]

    # Verify links are present
    assert "/" in links
    assert "/u/awdeorio/" in links
    assert "/u/jflinn/" in links
    assert "/u/michjc/" in links
    assert "/p/1/" in links
    assert "/p/2/" in links
    assert "/p/3/" in links

    # Verify links are not present
    assert "/u/jag/" not in links
    assert "/p/4/" not in links

    # Verify template uses jinja, not hardcoded HTML
    utils.assert_template_not_hardcoded("insta485/templates/index.html")


def test_likes():
    """Verify expected "likes" are present in / URL."""
    tmpdir = TMPDIR/"insta485_html"
    shutil.rmtree(tmpdir, ignore_errors=True)
    subprocess.run(["insta485generator", "insta485", "-o", tmpdir], check=True)

    # Parse HTML, then convert all whitespace to single spaces
    with open(tmpdir/"index.html") as infile:
        soup = bs4.BeautifulSoup(infile, "html.parser")
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)

    # Verify expected content is in text on generated HTML page
    assert "1 like" in text
    assert "2 likes" in text
    assert "3 likes" in text

    # Verify unexpected content is not in text on generated HTML page
    assert "1 likes" not in text
    assert "2 like " not in text
    assert "3 like " not in text
    assert "4 likes" not in text
    assert "0 likes" not in text

    # Verify template uses jinja, not hardcoded HTML
    utils.assert_template_not_hardcoded("insta485/templates/index.html")


def test_timestamps():
    """Verify expected timestamps are present in / URL."""
    tmpdir = TMPDIR/"insta485_html"
    shutil.rmtree(tmpdir, ignore_errors=True)
    subprocess.run(["insta485generator", "insta485", "-o", tmpdir], check=True)

    # Parse HTML, then convert all whitespace to single spaces
    with open(tmpdir/"index.html") as infile:
        soup = bs4.BeautifulSoup(infile, "html.parser")
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)

    # Verify expected content is in text on generated HTML page
    assert "10 minutes ago" in text
    assert "4 hours ago" in text
    assert "a day ago" in text

    # Verify template uses jinja, not hardcoded HTML
    utils.assert_template_not_hardcoded("insta485/templates/index.html")


def test_comments():
    """Verify expected comments are present in / URL."""
    tmpdir = TMPDIR/"insta485_html"
    shutil.rmtree(tmpdir, ignore_errors=True)
    subprocess.run(["insta485generator", "insta485", "-o", tmpdir], check=True)

    # Parse HTML, then convert all whitespace to single spaces
    with open(tmpdir/"index.html") as infile:
        soup = bs4.BeautifulSoup(infile, "html.parser")
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)

    # Verify expected content is in text on generated HTML page
    assert "awdeorio #chickensofinstagram" in text
    assert "jflinn I <3 chickens" in text
    assert "michjc Cute overload!" in text
    assert "awdeorio Sick #crossword" in text
    assert "jflinn Walking the plank #chickensofinstagram" in text
    assert "awdeorio This was after trying to teach them to do a #crossword" \
        in text

    # Verify template uses jinja, not hardcoded HTML
    utils.assert_template_not_hardcoded("insta485/templates/index.html")
