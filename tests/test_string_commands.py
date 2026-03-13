import pytest

from conftest import incantation


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

def test_decipher_single_group(interpreter):
    """Test decipher: extract single capture group"""
    spell = incantation('summon the text with essence of whispers of "Hello World". '
                      'decipher text with pattern "(\\w+) \\w+" into first.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["first"] == "Hello"

def test_decipher_multiple_groups(interpreter):
    """Test decipher: extract multiple capture groups"""
    spell = incantation('summon the text with essence of whispers of "John:42". '
                      'decipher text with pattern "(\\w+):(\\d+)" into name and age.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["name"] == "John"
    assert interpreter.variables["age"] == "42"

def test_decipher_no_match(interpreter):
    """Test decipher: pattern doesn't match"""
    spell = incantation('summon the text with essence of whispers of "Hello". '
                      'decipher text with pattern "(\\d+)" into num.')
    with pytest.raises(ValueError):
        interpreter.parse_and_execute(spell)
