"""
Test insta485generator with published "hello_css" input.

EECS 485 Project 1

Andrew DeOrio <awdeorio@umich.edu>
"""
import re
import shutil
import textwrap
import subprocess
from pathlib import Path
from utils import TMPDIR, TESTDATA_DIR


def test_hello_css():
    """Diff check hello_css/index.html."""
    # Set up temporary directory
    tmpdir = TMPDIR/"test_hello_css"
    shutil.rmtree(tmpdir, ignore_errors=True)
    tmpdir.mkdir(parents=True)
    shutil.copytree(TESTDATA_DIR/"hello_css", tmpdir/"hello_css")

    # Run insta485generator in tmpdir
    subprocess.run(["insta485generator", "hello_css"], check=True, cwd=tmpdir)

    # Make sure generated files exist
    output_dir = tmpdir/"hello_css/html"
    output_html = output_dir/"index.html"
    output_css = output_dir/"css/style.css"
    assert output_dir.exists()
    assert output_html.exists()
    assert output_css.exists()

    # Verify output file content, normalized for whitespace
    actual_html = output_html.read_text()
    correct_html = textwrap.dedent("""
        <!DOCTYPE html>
        <html lang="en">
          <head>
             <title>Hello world</title>
             <link rel="stylesheet" type="text/css" href="/css/style.css">
          </head>
          <body>
            <div class="important">hello</div>
            <div class="important">world</div>
          </body>
        </html>
    """)
    correct_html = re.sub(r"\s+", "", correct_html)
    actual_html = re.sub(r"\s+", "", actual_html)
    assert actual_html == correct_html

    # Verify CSS content
    correct_css = textwrap.dedent("""
        body {
            background: pink;
        }

        div.important {
            font-weight: bold;
            font-size: 1000%;
        }
    """)
    actual_css = Path(output_css).read_text()
    correct_css = re.sub(r"\s+", "", correct_css)
    actual_css = re.sub(r"\s+", "", actual_css)
    assert actual_css == correct_css
