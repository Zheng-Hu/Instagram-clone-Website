"""
Validate generated HTML against HTML5 W3C spec.

EECS 485 Project 1

Andrew DeOrio <awdeorio@umich.edu>
"""
import shutil
import subprocess
from pathlib import Path
from utils import TMPDIR


def test_html():
    """Validate generated HTML5 in insta485/html/ ."""
    tmpdir = TMPDIR/"insta485_html"
    shutil.rmtree(tmpdir, ignore_errors=True)
    subprocess.run(["insta485generator", "insta485", "-o", tmpdir], check=True)

    # Verify expected files are present
    assert Path(tmpdir/"index.html")
    assert Path(
        # Drew
        tmpdir/"uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg"
    ).exists()
    assert Path(
        # Jag
        tmpdir/"uploads/73ab33bd357c3fd42292487b825880958c595655.jpg"
    ).exists()
    assert Path(
        # Mike
        tmpdir/"uploads/5ecde7677b83304132cb2871516ea50032ff7a4f.jpg"
    ).exists()
    assert Path(
        # Jason
        tmpdir/"uploads/505083b8b56c97429a728b68f31b0b2a089e5113.jpg"
    ).exists()
    assert Path(
        # Post 1
        tmpdir/"uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg"
    ).exists()
    assert Path(
        # Post 2
        tmpdir/"uploads/ad7790405c539894d25ab8dcf0b79eed3341e109.jpg"
    ).exists()
    assert Path(
        # Post 3
        tmpdir/"uploads/9887e06812ef434d291e4936417d125cd594b38a.jpg"
    ).exists()
    assert Path(
        # Post 4
        tmpdir/"uploads/2ec7cf8ae158b3b1f40065abfb33e81143707842.jpg"
    ).exists()

    # Verify HTML5
    subprocess.run([
        "html5validator",
        "--root", tmpdir,
        "--ignore", "JAVA_TOOL_OPTIONS",
    ], check=True)
