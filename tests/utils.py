"""P2 autograder utility functions."""
import pathlib
import shutil
import subprocess
import filecmp
from pathlib import Path


# Temporary directory. Tests will create files here.
TMPDIR = pathlib.Path("tmp")

# Directory containing unit tests
TEST_DIR = pathlib.Path(__file__).parent

# Directory containing unit test input files
TESTDATA_DIR = TEST_DIR/"testdata"


def get_input_dir(basename):
    """Return absolute path of input directory."""
    if TEST_DIR.name == "autograder":
        # In the autograder environment, inputs are in autograder/testdata/
        return TEST_DIR/"testdata"/basename

    # In the student environment, look for inputs in the project root,
    # which we assume to be the present working directory.
    return pathlib.Path(basename)


def get_output_dir(basename):
    """Return absolute path of html output directory."""
    if TEST_DIR.name == "autograder":
        # Autograder environment example: autograder/testdata/<basename>/html
        return TEST_DIR/"testdata"/basename/"html"

    # Student environment example: <basename>/html
    basename = pathlib.Path(basename)
    return basename/"html"


def assert_template_not_hardcoded(template_path):
    """Detect if jinja templates are hardcoded."""
    template_path = Path(template_path)
    stem = template_path.stem  # explore.html -> explore

    # Create two sites directories to run generator on with different configs
    site1_dir = TMPDIR/"template_not_hardcoded"/stem/"site1"
    site2_dir = TMPDIR/"template_not_hardcoded"/stem/"site2"
    shutil.rmtree(site1_dir, ignore_errors=True)
    shutil.rmtree(site2_dir, ignore_errors=True)
    site1_dir.mkdir(parents=True)
    site2_dir.mkdir(parents=True)

    # Copy jinja_check_configs for the given template type
    config_1 = TESTDATA_DIR/"template_not_hardcoded"/stem/"1/config.json"
    config_2 = TESTDATA_DIR/"template_not_hardcoded"/stem/"2/config.json"
    shutil.copy(config_1, site1_dir)
    shutil.copy(config_2, site2_dir)

    # Copy ALL student templates.  We copy everything to ensure that template
    # inheritance works correctly, e.g., "base.html".
    shutil.copytree(template_path.parent, site1_dir/"templates")
    shutil.copytree(template_path.parent, site2_dir/"templates")

    # Generate the two single site pages
    subprocess.run(["insta485generator", site1_dir], check=True)
    subprocess.run(["insta485generator", site2_dir], check=True)

    # Verify that pages are created
    site1_index = site1_dir/"html/index.html"
    site2_index = site2_dir/"html/index.html"
    assert site1_index.exists()
    assert site2_index.exists()

    # Verify two rendered pages are different.  If they were hardcoded, they
    # would be the same.
    assert not filecmp.cmp(site1_index, site2_index, shallow=False), \
        "Templates fail to generate unique sites using different configs"
