"""
Test insta485generator with published "hello" input.

EECS 485 Project 1

Andrew DeOrio <awdeorio@umich.edu>
"""
import re
import shutil
import subprocess
import textwrap
from utils import TMPDIR, TESTDATA_DIR


def test_hello():
    """Diff check hello/index.html."""
    # Set up temporary directory
    tmpdir = TMPDIR/"test_hello"
    shutil.rmtree(tmpdir, ignore_errors=True)
    tmpdir.mkdir(parents=True)
    shutil.copytree(TESTDATA_DIR/"hello", tmpdir/"hello")

    # Run insta485generator in tmpdir
    subprocess.run(["insta485generator", "hello"], check=True, cwd=tmpdir)

    # Make sure generated files exist
    output_dir = tmpdir/"hello/html"
    index_path = output_dir/"index.html"
    assert output_dir.exists()
    assert index_path.exists()

    # Verify output file content, normalized for whitespace
    actual = index_path.read_text()
    correct = textwrap.dedent("""
        <!DOCTYPE html>
        <html lang="en">
           <head>
             <title>
               Hello world
             </title>
           </head>
           <body>
             hello
             world
           </body>
        </html>
    """)
    correct = re.sub(r"\s+", "", correct)
    actual = re.sub(r"\s+", "", actual)
    assert actual == correct
