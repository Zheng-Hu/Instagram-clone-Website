"""
Test insta485generator command line interface.

EECS 485 Project 1

Andrew DeOrio <awdeorio@umich.edu>
"""
import shutil
import textwrap
import subprocess
from utils import TMPDIR, TESTDATA_DIR


def test_executable():
    """Verify that insta485generator exectuable is in my PATH."""
    assert shutil.which("insta485generator"), \
        "Can't find 'insta485generator' in PATH"


def test_help():
    """Verify insta485generator --help output."""
    output = subprocess.run(
        ["insta485generator", "--help"],
        check=True, stdout=subprocess.PIPE, universal_newlines=True,
    ).stdout
    assert output == textwrap.dedent("""\
        Usage: insta485generator [OPTIONS] INPUT_DIR

          Templated static website generator.

        Options:
          -o, --output PATH  Output directory.
          -v, --verbose      Print more output.
          --help             Show this message and exit.
    """)


def test_output():
    """Verify insta485generator --output changes output dir."""
    # Set up temporary directory
    tmpdir = TMPDIR/"test_output"
    shutil.rmtree(tmpdir, ignore_errors=True)
    tmpdir.mkdir(parents=True)
    shutil.copytree(TESTDATA_DIR/"hello", tmpdir/"hello")

    # Run insta485generator using the --output option
    subprocess.run(
        ["insta485generator", "--output", "myout", "hello"],
        check=True, cwd=tmpdir,
    )

    # Verify files are present in "myout/" direcotry
    assert (tmpdir/"myout").exists()
    assert (tmpdir/"myout/index.html").exists()
