import pytest

from spellscript import SpellScriptInterpreter

@pytest.fixture
def interpreter():
    return SpellScriptInterpreter()

@pytest.fixture
def test_spells():
    with open("test.spell", "r") as f:
        return f.read()


def test_inquire(interpreter, test_spells):
    interpreter.parse_and_execute(test_spells)
    assert interpreter.variables["test_var"] == "test input"

def test_append(interpreter, test_spells):
    interpreter.parse_and_execute(test_spells)
    assert interpreter.variables["test_array"] == [1, 2, 3, 4]

def test_enchant(interpreter, test_spells):
    interpreter.parse_and_execute(test_spells)
    assert interpreter.variables["test_dict"] == {"a": 1, "b": 2}

def test_transmute(interpreter, test_spells):
    interpreter.parse_and_execute(test_spells)
    assert interpreter.variables["test_number"] == 1
    assert interpreter.variables["test_text"] == "test"
    assert interpreter.variables["test_truth"] is True