import os
import tempfile
import pytest

from spellscript import SpellScriptInterpreter


@pytest.fixture
def interpreter():
    return SpellScriptInterpreter()


def incantation(details):
    return f"begin the grimoire. {details} close the grimoire."


@pytest.fixture
def temp_text_file():
    """Create a temporary text file for testing file reading."""
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        f.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")
        temp_file_path = f.name

    yield temp_file_path

    os.unlink(temp_file_path)
