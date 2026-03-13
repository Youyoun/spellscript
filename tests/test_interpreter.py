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

def test_recursive_ritual(interpreter, capsys):
    """Test that recursive ritual calls work correctly"""
    script = """
    begin the grimoire.
    conjure ritual named factorial with n to begin:
        if the signs show n less than 2 then return 1.
        return n multiplied by through ritual factorial with n lesser by 1.
    end ritual.
    inscribe through ritual factorial with 5.
    close the grimoire.
    """
    interpreter.parse_and_execute(script)
    captured = capsys.readouterr()
    assert "120" in captured.out

def test_modulo(interpreter):
    """Test the modulo operator"""
    script = """
    begin the grimoire.
    summon the a with essence of 10 residue of 3.
    summon the b with essence of 7 residue of 2.
    summon the c with essence of 15 residue of 5.
    close the grimoire.
    """
    interpreter.parse_and_execute(script)
    assert interpreter.variables["a"] == 1
    assert interpreter.variables["b"] == 1
    assert interpreter.variables["c"] == 0
