"""
Validate handcoded HTML against HTML5 W3C spec.

EECS 485 Project 1

Andrew DeOrio <awdeorio@umich.edu>
"""
import subprocess
from pathlib import Path


def test_html():
    """Validate handcoded HTML5 in html/."""
    assert Path("html/index.html").exists()
    assert Path("html/u/awdeorio/index.html").exists()
    subprocess.run([
        "html5validator", "--root", "html", "--ignore", "JAVA_TOOL_OPTIONS",
    ], check=True)
