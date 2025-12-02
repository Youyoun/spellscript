import sys
from spellscript import SpellScriptInterpreter

def main():
    if len(sys.argv) < 2:
        print("usage: python spellscript.py <filename>.spell")
        sys.exit(1)
    with open(sys.argv[1], 'r') as f:
        text = f.read()
    interp = SpellScriptInterpreter()
    try:
        interp.parse_and_execute(text)
    except Exception as e:
        print(f"the spell has backfired: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()