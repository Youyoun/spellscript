import pytest

from spellscript import SpellScriptInterpreter

@pytest.fixture
def interpreter():
    return SpellScriptInterpreter()

def incantation(details):
    return f"begin the grimoire. {details} close the grimoire."


def test_inscribe(interpreter, capsys):
    """Test inscribe: print a string"""
    spell = incantation("inscribe whispers of \"Mortal plane, I greet thee\".")
    interpreter.parse_and_execute(spell)
    captured = capsys.readouterr()
    assert "Mortal plane, I greet thee" in captured.out

def test_spell():
    """test that running spellscript on test.spell works"""
    interpreter = SpellScriptInterpreter()
    with open("test.spell") as f:
        interpreter.parse_and_execute(f.read())
