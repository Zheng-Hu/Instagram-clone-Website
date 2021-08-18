"""
Check hand coded index page in html/index.html file.

EECS 485 Project 1

Andrew DeOrio <awdeorio@umich.edu>
"""
import re
from pathlib import Path
import bs4


def test_files():
    """Verify files are present in filesystem."""
    assert Path("html/index.html").exists()
    assert Path("html/u/awdeorio/index.html").exists()
    assert Path(
        "html/uploads/505083b8b56c97429a728b68f31b0b2a089e5113.jpg"
    ).exists()
    assert Path(
        "html/uploads/5ecde7677b83304132cb2871516ea50032ff7a4f.jpg"
    ).exists()
    assert Path(
        "html/uploads/73ab33bd357c3fd42292487b825880958c595655.jpg"
    ).exists()
    assert Path(
        "html/uploads/ad7790405c539894d25ab8dcf0b79eed3341e109.jpg"
    ).exists()
    assert Path(
        "html/uploads/9887e06812ef434d291e4936417d125cd594b38a.jpg"
    ).exists()
    assert Path(
        "html/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg"
    ).exists()
    assert Path(
        "html/uploads/2ec7cf8ae158b3b1f40065abfb33e81143707842.jpg"
    ).exists()
    assert Path(
        "html/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg"
    ).exists()


def test_images():
    """Verify all images are present in /index.html."""
    with open("html/index.html") as infile:
        soup = bs4.BeautifulSoup(infile, "html.parser")
    srcs = [x.get("src") for x in soup.find_all('img')]
    assert "/uploads/505083b8b56c97429a728b68f31b0b2a089e5113.jpg" in srcs
    assert "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg" in srcs
    assert "/uploads/9887e06812ef434d291e4936417d125cd594b38a.jpg" in srcs
    assert "/uploads/ad7790405c539894d25ab8dcf0b79eed3341e109.jpg" in srcs
    assert "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg" in srcs


def test_links():
    """Verify expected links present in /index.html."""
    with open("html/index.html") as infile:
        soup = bs4.BeautifulSoup(infile, "html.parser")
    links = [x.get("href") for x in soup.find_all("a")]
    assert "/" in links
    assert "/u/awdeorio/" in links
    assert "/u/jflinn/" in links
    assert "/u/michjc/" in links
    assert "/p/1/" in links
    assert "/p/2/" in links
    assert "/p/3/" in links
    assert "/p/4/" not in links
    assert "/u/jag/" not in links


def test_likes():
    """Verify expected "likes" are present in /index.html."""
    with open("html/index.html") as infile:
        soup = bs4.BeautifulSoup(infile, "html.parser")
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)
    assert "1 like" in text
    assert "1 likes" not in text
    assert "2 likes" in text
    assert "2 like " not in text
    assert "3 likes" in text
    assert "3 like " not in text
    assert "4 likes" not in text
    assert "0 likes" not in text


def test_comments():
    """Verify expected comments are present in /index.html."""
    with open("html/index.html") as infile:
        soup = bs4.BeautifulSoup(infile, "html.parser")
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)
    assert "awdeorio #chickensofinstagram" in text
    assert "jflinn I <3 chickens" in text
    assert "michjc Cute overload!" in text
    assert "awdeorio Sick #crossword" in text
    assert "jflinn Walking the plank #chickensofinstagram" in text
    assert "awdeorio This was after trying to teach them to do a #crossword" \
        in text


def test_timestamps():
    """Verify expected timestamps are present in /index.html."""
    with open("html/index.html") as infile:
        soup = bs4.BeautifulSoup(infile, "html.parser")
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)
    assert "10 minutes ago" in text
    assert "4 hours ago" in text
    assert "a day ago" in text
