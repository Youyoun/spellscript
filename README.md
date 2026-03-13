<div align="center">
  <h1>spellscript</h1>
  <img src="https://hc-cdn.hel1.your-objectstorage.com/s/v3/70eec7a3eb552f1b5747b73942b2ee1daac25647_untitled_design.png" alt="image" width="300">
</div>

an esoteric programming language where code reads like magical incantations from an ancient spellbook. every program is a "spell" written in a "grimoire," so theorhetically, you can write all your code english essay style due to its no newline/indentation requirement.

**write code that looks like this:**

```spellscript
begin the grimoire.
summon the power with essence of 7.
conjure ritual named amplify with value to return value multiplied by value.
enchant power through ritual amplify with power.
inscribe whispers of "the power is amplified: " bound with power.
close the grimoire.
```

**output:** `the power is amplified: 49`


## features
- variables
- dynamic typing
- arrays
- functions (with recursion support)
- conditionals/loops
- string manipulation (split, extract, replace, regex)
- file reading
- type conversion
- user input
- output
- command-line arguments (`scrolls`)


## run it
1. clone thy repo
2. make sure you have python 3.6+
3. create a file called `<filename>.spell`
4. then run `python cli.py your-spell.spell [arguments...]`

extra arguments are available inside the spell as the `scrolls` array.

## overview

### basic syntax (more detailed in docs, please look at that!)

| concept | spellscript | traditional |
|---------|-------------|-------------|
| declare variable | `summon the x with essence of 10` | `x = 10` |
| modify variable | `enchant x with 20` | `x = 20` |
| print | `inscribe x` | `print(x)` |
| input | `inquire whispers of "prompt" into x` | `x = input("prompt")` |
| string | `whispers of "text"` | `"text"` |
| array | `collection holding 1 and 2 and 3` | `[1, 2, 3]` |
| if statement | `if the signs show x equals 5 then` | `if x == 5:` |
| loop | `repeat the incantation 5 times to begin:` | `for i in range(5):` |
| function | `conjure ritual named add with a and b to` | `def add(a, b):` |
| return | `return result` | `return result` |

### operators

| operation | spellscript | traditional |
|-----------|-------------|-------------|
| addition | `a greater by b` | `a + b` |
| subtraction | `a lesser by b` | `a - b` |
| multiplication | `a multiplied by b` | `a * b` |
| division | `a divided by b` | `a / b` |
| modulo | `a residue of b` | `a % b` |
| equals | `a equals b` | `a == b` |
| greater than | `a greater than b` | `a > b` |
| less than | `a less than b` | `a < b` |
| and | `a and b` | `a and b` |
| or | `a or b` | `a or b` |
| not | `not a` | `not a` |

### string operations

| operation | spellscript | traditional |
|-----------|-------------|-------------|
| split | `dissect x by "," into parts` | `parts = x.split(",")` |
| get line | `extract verse 2 from x into line` | `line = x.splitlines()[1]` |
| replace | `transform x replacing "a" with "b" into y` | `y = x.replace("a", "b")` |
| regex | `decipher x with pattern "(\w+)" into match` | `match = re.match(r"(\w+)", x)` |
| read file | `reveal knowledge from "file.txt" into data` | `data = open("file.txt").read()` |

## →→→ documentation ←←←

- resources/documentation.md - feature documentation
- examples/ - example programs (fibonacci, factorial, file reading)

## limitations (totally intentional btw)

- no nested arrays
- no string indexing (use character arrays)
- no break/continue in loops
- no comments
- deeply recursive rituals may exceed python's stack limit
- functions must have at least one parameter
- no null concept

## boring stuff
- idea from [the muffin programming language](https://github.com/CBerJun/Muffin)
- ai was used for debugging some inperpreter issues, which included rituals and conditionals.  
