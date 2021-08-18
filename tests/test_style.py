"""
Check Python style with pycodestyle, pydocstyle and pylint.

EECS 485 Project 1

Andrew DeOrio <awdeorio@umich.edu>
"""
import subprocess
import utils


def test_pycodestyle():
    """Run `pycodestyle setup.py insta485generator`."""
    assert_no_prohibited_terms()
    subprocess.run(
        ["pycodestyle", "setup.py", "insta485generator"],
        check=True,
    )


def test_pydocstyle():
    """Run `pydocstyle setup.py insta485generator`."""
    assert_no_prohibited_terms()
    subprocess.run(["pydocstyle", "setup.py", "insta485generator"], check=True)


def test_pylint():
    """Run pylint."""
    assert_no_prohibited_terms()
    subprocess.run([
        "pylint",
        "--rcfile", utils.TEST_DIR/"testdata/pylintrc",
        "--disable=no-value-for-parameter",
        "setup.py",
        "insta485generator",
    ], check=True)


def assert_no_prohibited_terms():
    """Check for prohibited terms in student solution."""
    prohibited_terms = ['nopep8', 'noqa', 'pylint']
    for term in prohibited_terms:
        completed_process = subprocess.run(
            ["grep", "-r", "-n", term, "--include=*.py", "insta485generator"],
            check=False,  # We'll check the return code manually
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )

        # Grep exit code should be non-zero, indicating that the prohibited
        # term was not found.  If the exit code is zero, crash and print a
        # helpful error message with a filename and line number.
        assert completed_process.returncode != 0, (
            "The term '{term}' is prohibited.\n{message}"
            .format(term=term, message=completed_process.stdout)
        )
