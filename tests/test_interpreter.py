import pytest

from conftest import incantation


def test_inscribe(interpreter, capsys):
    """Test inscribe: print a string"""
    spell = incantation("inscribe whispers of \"Mortal plane, I greet thee\".")
    interpreter.parse_and_execute(spell)
    captured = capsys.readouterr()
    assert "Mortal plane, I greet thee" in captured.out

def test_spell():
    """test that running spellscript on test.spell works"""
    import os
    from spellscript import SpellScriptInterpreter
    interpreter = SpellScriptInterpreter()
    spell_path = os.path.join(os.path.dirname(__file__), "test.spell")
    with open(spell_path) as f:
        interpreter.parse_and_execute(f.read())

def test_ritual_with_conditionals(interpreter, capsys):
    """Test ritual definition and invocation with conditional returns"""
    script = """
    begin the grimoire.
    conjure ritual named getgrade with score to begin:
        if the signs show score greater than 90 then return whispers of "a".
        if the signs show score greater than 80 then return whispers of "b".
        if the signs show score greater than 70 then return whispers of "c".
        return whispers of "f".
    end ritual.

    inscribe whispers of "95 = " bound with through ritual getgrade with 95.
    inscribe whispers of "75 = " bound with through ritual getgrade with 75.
    close the grimoire.
    """
    interpreter.parse_and_execute(script)
    captured = capsys.readouterr()
    assert "95 = a" in captured.out
    assert "75 = c" in captured.out
