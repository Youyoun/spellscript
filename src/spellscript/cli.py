import sys
from spellscript import SpellScriptInterpreter

import argparse

parser = argparse.ArgumentParser(description="Spellscript interpreter")
parser.add_argument("filename", type=str, help="the spell to execute")

def main():
    args = parser.parse_args()
    with open(args.filename, 'r') as f:
        text = f.read()
    interp = SpellScriptInterpreter()
    try:
        interp.parse_and_execute(text)
    except Exception as e:
        print(f"the spell has backfired: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
