import pytest
import os
import tempfile

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
    
    # Clean up the temporary file after test
    os.unlink(temp_file_path)

def test_reveal_knowledge(interpreter, temp_text_file):
    """Test reveal: read file contents into a variable"""
    spell = incantation(f'reveal knowledge from "{temp_text_file}" into scroll. inscribe scroll.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["scroll"] == "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"

def test_reveal_nonexistent_file(interpreter):
    """Test reveal: handle non-existent file"""
    spell = incantation('reveal knowledge from "nonexistent_file.txt" into scroll.')
    with pytest.raises(FileNotFoundError):
        interpreter.parse_and_execute(spell)

def test_dissect_string(interpreter):
    """Test dissect: split string by delimiter"""
    spell = incantation('summon the words with essence of whispers of "apple,banana,cherry". '
                      'dissect words by "," into fruits. '
                      'inscribe fruits.')
    interpreter.parse_and_execute(spell)
    assert "words" in interpreter.variables
    assert interpreter.variables["fruits"] == ["apple", "banana", "cherry"]

def test_extract_verse(interpreter):
    """Test extract: get specific line from multi-line text"""
    spell = incantation('summon the poem with essence of whispers of "First line\nSecond line\nThird line". '
                      'extract verse 2 from poem into second_line. '
                      'inscribe second_line.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["second_line"] == "Second line"

def test_extract_verse_out_of_range(interpreter):
    """Test extract: handle out of range line number"""
    spell = incantation('summon the poem with essence of whispers of "Single line". '
                      'extract verse 2 from poem into second_line.')
    with pytest.raises(IndexError):
        interpreter.parse_and_execute(spell)

def test_transform_string(interpreter):
    """Test transform: replace text in string"""
    spell = incantation('summon the incantation with essence of whispers of "Turn lead into gold". '
                      'transform incantation replacing "lead" with "silver" into new_incantation. '
                      'inscribe new_incantation.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["new_incantation"] == "Turn silver into gold"
