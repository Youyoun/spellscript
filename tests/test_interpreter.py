import pytest

from conftest import incantation


def test_inscribe(interpreter, capsys):
    """Test inscribe: print a string"""
    spell = incantation("inscribe whispers of \"Mortal plane, I greet thee\".")
    interpreter.parse_and_execute(spell)
    captured = capsys.readouterr()
    assert "Mortal plane, I greet thee" in captured.out

def test_inscribe_variable(interpreter, capsys):
    """Test inscribe: print a variable value"""
    spell = incantation('summon the x with essence of 42. inscribe x.')
    interpreter.parse_and_execute(spell)
    captured = capsys.readouterr()
    assert "42" in captured.out

def test_inscribe_array(interpreter, capsys):
    """Test inscribe: print an array"""
    spell = incantation('summon the nums with essence of collection holding 1 and 2 and 3. inscribe nums.')
    interpreter.parse_and_execute(spell)
    captured = capsys.readouterr()
    assert "[1, 2, 3]" in captured.out

def test_spell():
    """test that running spellscript on test.spell works"""
    import os
    from spellscript import SpellScriptInterpreter
    interpreter = SpellScriptInterpreter()
    spell_path = os.path.join(os.path.dirname(__file__), "test.spell")
    with open(spell_path) as f:
        interpreter.parse_and_execute(f.read())

def test_summon_no_value(interpreter):
    """Test summon without a value initializes to None"""
    spell = incantation('summon the x.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["x"] is None

def test_summon_with_value(interpreter):
    """Test summon with a numeric value"""
    spell = incantation('summon the x with essence of 42.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["x"] == 42

def test_summon_with_string(interpreter):
    """Test summon with a string value"""
    spell = incantation('summon the name with essence of whispers of "alice".')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["name"] == "alice"

def test_enchant(interpreter):
    """Test enchant: reassign a variable"""
    spell = incantation('summon the x with essence of 1. enchant x with 99.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["x"] == 99

def test_enchant_at_position(interpreter):
    """Test enchant: modify array element"""
    spell = incantation('summon the arr with essence of collection holding 1 and 2 and 3. '
                        'enchant arr at position 1 with 99.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["arr"] == [1, 99, 3]

def test_banish(interpreter):
    """Test banish: delete a variable"""
    spell = incantation('summon the temp with essence of 5. banish the temp.')
    interpreter.parse_and_execute(spell)
    assert "temp" not in interpreter.variables

def test_banish_unknown(interpreter):
    """Test banish: error on unknown variable"""
    spell = incantation('banish the nonexistent.')
    with pytest.raises(NameError):
        interpreter.parse_and_execute(spell)

def test_append(interpreter):
    """Test append: add element to array"""
    spell = incantation('summon the arr with essence of collection holding 1 and 2. '
                        'append 3 to arr.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["arr"] == [1, 2, 3]

def test_collection_holding(interpreter):
    """Test collection holding: create arrays"""
    spell = incantation('summon the nums with essence of collection holding 10 and 20 and 30.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["nums"] == [10, 20, 30]

def test_at_position(interpreter):
    """Test at position: access array element"""
    spell = incantation('summon the arr with essence of collection holding 10 and 20 and 30. '
                        'summon the val with essence of arr at position 1.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["val"] == 20

def test_length_of(interpreter):
    """Test length of: get array length"""
    spell = incantation('summon the arr with essence of collection holding 1 and 2 and 3. '
                        'summon the len with essence of length of arr.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["len"] == 3

def test_greater_by(interpreter):
    """Test greater by: addition"""
    spell = incantation('summon the x with essence of 3 greater by 4.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["x"] == 7

def test_lesser_by(interpreter):
    """Test lesser by: subtraction"""
    spell = incantation('summon the x with essence of 10 lesser by 3.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["x"] == 7

def test_multiplied_by(interpreter):
    """Test multiplied by: multiplication"""
    spell = incantation('summon the x with essence of 6 multiplied by 7.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["x"] == 42

def test_divided_by(interpreter):
    """Test divided by: division"""
    spell = incantation('summon the x with essence of 10 divided by 2.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["x"] == 5

def test_divided_by_zero(interpreter):
    """Test divided by: zero division error"""
    spell = incantation('summon the x with essence of 10 divided by 0.')
    with pytest.raises(ZeroDivisionError):
        interpreter.parse_and_execute(spell)

def test_residue_of(interpreter):
    """Test residue of: modulo"""
    spell = incantation('summon the a with essence of 10 residue of 3. '
                        'summon the b with essence of 7 residue of 2. '
                        'summon the c with essence of 15 residue of 5.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["a"] == 1
    assert interpreter.variables["b"] == 1
    assert interpreter.variables["c"] == 0

def test_float_point(interpreter):
    """Test point syntax for floating point numbers"""
    spell = incantation('summon the x with essence of 3point14.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["x"] == 3.14

def test_bound_with(interpreter):
    """Test bound with: string concatenation"""
    spell = incantation('summon the msg with essence of whispers of "hello" bound with whispers of " world".')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["msg"] == "hello world"

def test_truth_falsehood(interpreter):
    """Test truth and falsehood literals"""
    spell = incantation('summon the a with essence of truth. summon the b with essence of falsehood.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["a"] is True
    assert interpreter.variables["b"] is False

def test_conditional_if(interpreter, capsys):
    """Test if the signs show: conditional"""
    spell = incantation('summon the x with essence of 10. '
                        'if the signs show x greater than 5 then inscribe whispers of "big".')
    interpreter.parse_and_execute(spell)
    captured = capsys.readouterr()
    assert "big" in captured.out

def test_conditional_if_else(interpreter, capsys):
    """Test if-else: conditional with otherwise"""
    spell = incantation('summon the x with essence of 3. '
                        'if the signs show x greater than 5 then inscribe whispers of "big" '
                        'otherwise inscribe whispers of "small".')
    interpreter.parse_and_execute(spell)
    captured = capsys.readouterr()
    assert "small" in captured.out

def test_condition_equals(interpreter, capsys):
    """Test equals comparison"""
    spell = incantation('summon the x with essence of 5. '
                        'if the signs show x equals 5 then inscribe whispers of "match".')
    interpreter.parse_and_execute(spell)
    captured = capsys.readouterr()
    assert "match" in captured.out

def test_condition_less_than(interpreter, capsys):
    """Test less than comparison"""
    spell = incantation('summon the x with essence of 3. '
                        'if the signs show x less than 5 then inscribe whispers of "yes".')
    interpreter.parse_and_execute(spell)
    captured = capsys.readouterr()
    assert "yes" in captured.out

def test_condition_and(interpreter, capsys):
    """Test logical and"""
    spell = incantation('summon the x with essence of 5. '
                        'if the signs show x greater than 2 and x less than 10 then inscribe whispers of "in range".')
    interpreter.parse_and_execute(spell)
    captured = capsys.readouterr()
    assert "in range" in captured.out

def test_condition_or(interpreter, capsys):
    """Test logical or"""
    spell = incantation('summon the x with essence of 1. '
                        'if the signs show x equals 1 or x equals 2 then inscribe whispers of "match".')
    interpreter.parse_and_execute(spell)
    captured = capsys.readouterr()
    assert "match" in captured.out

def test_condition_not(interpreter, capsys):
    """Test logical not"""
    spell = incantation('summon the x with essence of 5. '
                        'if the signs show not x equals 3 then inscribe whispers of "not three".')
    interpreter.parse_and_execute(spell)
    captured = capsys.readouterr()
    assert "not three" in captured.out

def test_repeat_loop(interpreter, capsys):
    """Test repeat the incantation: loop"""
    spell = incantation('summon the i with essence of 0. '
                        'repeat the incantation 3 times to begin: '
                        'enchant i with i greater by 1. '
                        'end loop.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["i"] == 3

def test_repeat_inline(interpreter, capsys):
    """Test repeat the incantation: inline loop"""
    spell = incantation('summon the i with essence of 0. '
                        'repeat the incantation 5 times do enchant i with i greater by 1.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["i"] == 5

def test_traverse(interpreter, capsys):
    """Test traverse: iterate over array"""
    spell = incantation('summon the arr with essence of collection holding 10 and 20 and 30. '
                        'summon the total with essence of 0. '
                        'traverse arr with each item to begin: '
                        'enchant total with total greater by item. '
                        'end traverse.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["total"] == 60

def test_traverse_with_index(interpreter):
    """Test traverse with index variable"""
    spell = incantation('summon the arr with essence of collection holding 10 and 20. '
                        'summon the last with essence of 0. '
                        'traverse arr with each item at idx to begin: '
                        'enchant last with idx. '
                        'end traverse.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["last"] == 1

def test_ritual_single_line(interpreter):
    """Test single-line ritual definition"""
    spell = incantation('conjure ritual named double with x to return x multiplied by 2. '
                        'summon the result with essence of through ritual double with 5.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["result"] == 10

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

def test_invoke_ritual(interpreter, capsys):
    """Test invoke the ritual: standalone function call"""
    spell = incantation('conjure ritual named greet with name to begin: '
                        'inscribe whispers of "hello " bound with name. '
                        'end ritual. '
                        'invoke the ritual greet with whispers of "world".')
    interpreter.parse_and_execute(spell)
    captured = capsys.readouterr()
    assert "hello world" in captured.out

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

def test_transmute_to_number(interpreter):
    """Test transmute: convert string to number"""
    spell = incantation('summon the x with essence of whispers of "42". transmute x into number.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["x"] == 42

def test_transmute_to_text(interpreter):
    """Test transmute: convert number to text"""
    spell = incantation('summon the x with essence of 42. transmute x into text.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["x"] == "42"

def test_transmute_to_truth(interpreter):
    """Test transmute: convert to boolean"""
    spell = incantation('summon the x with essence of 1. transmute x into truth.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["x"] is True

def test_gaze_upon(interpreter, capsys):
    """Test gaze upon: debug print condition"""
    spell = incantation('summon the x with essence of 5. gaze upon x greater than 3.')
    interpreter.parse_and_execute(spell)
    captured = capsys.readouterr()
    assert "Gazing reveals: True" in captured.out

def test_reveal_with_expression(interpreter, temp_text_file):
    """Test reveal: read file using a variable path"""
    interpreter.variables["filepath"] = temp_text_file
    spell = incantation('reveal knowledge from filepath into contents.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["contents"] == "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"

def test_scrolls_variable(interpreter):
    """Test that scrolls variable works as an array"""
    interpreter.variables["scrolls"] = ["hello", "world"]
    spell = incantation('summon the first with essence of scrolls at position 0. '
                        'summon the count with essence of length of scrolls.')
    interpreter.parse_and_execute(spell)
    assert interpreter.variables["first"] == "hello"
    assert interpreter.variables["count"] == 2
