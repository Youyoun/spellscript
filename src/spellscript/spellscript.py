# spellscript interpreter
# open sourced and documented at: https://github.com/sirbread/spellscript

import operator
import re
import time


class ExecutionContext:
    def __init__(self, source='main', body_statements=None, start_index=0):
        self.source = source
        self.body_statements = body_statements or []
        self.current_index = start_index

    def __repr__(self):
        return f"ExecutionContext(source={self.source}, body_statements={self.body_statements}, current_index={self.current_index})"


class SpellScriptInterpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.tokens = []
        self.current_token_index = 0
        self.context_stack = []

    def get_variable(self, name):
        if name not in self.variables:
            raise NameError(f"unknown entity {name}")
        return self.variables[name]

    def get_list_variable(self, name):
        value = self.get_variable(name)
        if not isinstance(value, list):
            raise TypeError(f"{name} is not a collection")
        return value

    def get_str_variable(self, name):
        value = self.get_variable(name)
        if not isinstance(value, str):
            raise TypeError(f"{name} is not text")
        return value

    def execute_body(self, body_statements):
        context = ExecutionContext(source='body', body_statements=body_statements, start_index=0)
        self.context_stack.append(context)
        result = None
        while context.current_index < len(context.body_statements):
            body_statement = context.body_statements[context.current_index]
            context.current_index += 1
            result = self.execute_statement(body_statement)
            if result is not None:
                break
        self.context_stack.pop()
        return result

    def tokenize(self, spell_text):
        pattern = r'((?:[^\.":"]|"[^"]*")+[\.:])'
        statements = re.findall(pattern, spell_text)
        return [s.strip() for s in statements if s.strip()]

    def parse_and_execute(self, spell_text):
        self.tokens = self.tokenize(spell_text)
        if not self.tokens:
            raise SyntaxError("empty spell")
        first = self.tokens[0].lower()
        last = self.tokens[-1].lower()
        if "begin the grimoire" not in first:
            raise SyntaxError("spells must begin with Begin the grimoire")
        if "close the grimoire" not in last:
            raise SyntaxError("spells must end with Close the grimoire")

        self.current_token_index = 1
        while self.current_token_index < len(self.tokens) - 1:
            statement = self.tokens[self.current_token_index]
            self.current_token_index += 1
            self.execute_statement(statement)

    def remove_filler_words(self, text):
        text = re.sub(r'\bis\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def execute_statement(self, statement):
        statement = statement.strip()
        if statement.endswith('.') or statement.endswith(':'):
            statement = statement[:-1]
        if not statement:
            return
        lower = statement.lower()
        if "if the signs show" in lower:
            return self.handle_conditional(statement)
        if "repeat the incantation" in lower:
            return self.handle_loop(statement)
        if lower.startswith("traverse "):
            return self.handle_traverse(statement)
        words = statement.split()
        if not words:
            return
        cmd = words[0].lower()
        handler = self._dispatch.get(cmd)
        if handler is None:
            raise SyntaxError(f"unknown incantation {cmd}")
        return handler(self, statement, words)

    _dispatch = {}

    def handle_summon(self, statement):
        parts = statement.split()
        if len(parts) < 3 or parts[1].lower() != "the":
            raise SyntaxError("use Summon the <name> [with essence of <value>]")
        name = parts[2]

        if "with essence of" in statement:
            idx = statement.find("with essence of") + len("with essence of")
            val = self.evaluate_expression(statement[idx:].strip())
        else:
            val = None
        self.variables[name] = val

    def handle_enchant(self, statement):
        if " at position " in statement.lower():
            pattern = r'Enchant\s+(\w+)\s+at position\s+(.+?)\s+with\s+(.+)'
            match = re.match(pattern, statement, re.IGNORECASE)
            if not match:
                raise SyntaxError("use Enchant <array> at position <index> with <value>")

            array_name = match.group(1)
            index_expr = match.group(2).strip()
            value_expr = match.group(3).strip()

            array = self.get_list_variable(array_name)
            index = self.evaluate_expression(index_expr)
            if not isinstance(index, int):
                raise TypeError(f"index must be a number, got {type(index).__name__}")

            value = self.evaluate_expression(value_expr)

            if index < 0 or index >= len(array):
                raise IndexError(f"index {index} out of range for collection of length {len(array)}")

            array[index] = value
            return

        pattern = r'Enchant\s+(\w+)\s+(.+)'
        match = re.match(pattern, statement, re.IGNORECASE)
        if not match:
            raise SyntaxError("use Enchant <name> with <value> or through ritual <name> with <args>")
        name = match.group(1)
        rest = match.group(2).strip()

        self.get_variable(name)

        if rest.lower().startswith("through ritual"):
            ritual_call = rest[len("through ritual"):].strip()
            val = self.evaluate_ritual_call(ritual_call)
        elif rest.lower().startswith("with"):
            expr = rest[len("with"):].strip()
            val = self.evaluate_expression(expr)
        else:
            raise SyntaxError("use Enchant <name> with <value> or through ritual <name> with <args>")

        self.variables[name] = val

    def handle_inquire(self, statement):
        pattern = r'Inquire\s+whispers of\s+"([^"]*)"\s+into\s+(\w+)'
        match = re.match(pattern, statement, re.IGNORECASE)
        if not match:
            raise SyntaxError('use Inquire whispers of "prompt" into <name>')

        prompt = match.group(1)
        var_name = match.group(2)
        user_input = input(prompt + " ")
        self.variables[var_name] = user_input

    def handle_append(self, statement):
        pattern = r'Append\s+(.+?)\s+to\s+(\w+)'
        match = re.match(pattern, statement, re.IGNORECASE)
        if not match:
            raise SyntaxError("use Append <value> to <array>")

        value_expr = match.group(1).strip()
        array_name = match.group(2).strip()

        array = self.get_list_variable(array_name)
        value = self.evaluate_expression(value_expr)
        array.append(value)

    def collect_block_from_context(self, end_keyword):
        body_statements = []
        depth = 0

        if end_keyword == "end loop":
            start_patterns = ["repeat the incantation"]
        elif end_keyword == "end traverse":
            start_patterns = ["traverse "]
        elif end_keyword == "end ritual":
            start_patterns = ["conjure ritual named"]
        else:
            start_patterns = []

        if self.context_stack:
            context = self.context_stack[-1]
            tokens = context.body_statements
            get_index = lambda: context.current_index
            set_index = lambda v: setattr(context, 'current_index', v)
            limit = len(tokens)
        else:
            tokens = self.tokens
            get_index = lambda: self.current_token_index
            set_index = lambda v: setattr(self, 'current_token_index', v)
            limit = len(tokens) - 1

        while get_index() < limit:
            token = tokens[get_index()]
            set_index(get_index() + 1)

            token = token.strip()
            if token.endswith('.') or token.endswith(':'):
                token = token[:-1]
            token = token.strip()

            token_lower = token.lower()

            is_start = any(pattern in token_lower for pattern in start_patterns)
            if is_start and "to begin" in token_lower:
                depth += 1
                body_statements.append(token)
            elif token_lower == end_keyword:
                if depth == 0:
                    break
                else:
                    depth -= 1
                    body_statements.append(token)
            elif token:
                body_statements.append(token)

        return body_statements

    def handle_traverse(self, statement):
        pattern_with_index = r'Traverse\s+(\w+)\s+with each\s+(\w+)\s+at\s+(\w+)\s+to begin'
        pattern_simple = r'Traverse\s+(\w+)\s+with each\s+(\w+)\s+to begin'

        match_with_index = re.match(pattern_with_index, statement, re.IGNORECASE)
        match_simple = re.match(pattern_simple, statement, re.IGNORECASE)

        if match_with_index:
            array_name = match_with_index.group(1)
            item_var = match_with_index.group(2)
            index_var = match_with_index.group(3)
            has_index = True
        elif match_simple:
            array_name = match_simple.group(1)
            item_var = match_simple.group(2)
            index_var = None
            has_index = False
        else:
            raise SyntaxError("use Traverse <array> with each <item> to begin: ... end traverse")

        array = self.get_list_variable(array_name)

        body_statements = self.collect_block_from_context("end traverse")

        if not body_statements:
            raise SyntaxError("traverse body is empty")

        saved_item = self.variables.get(item_var)
        saved_index = self.variables.get(index_var) if has_index else None

        for idx, item in enumerate(array):
            self.variables[item_var] = item
            if has_index:
                self.variables[index_var] = idx

            result = self.execute_body(body_statements)
            if result is not None:
                return result

        if saved_item is not None:
            self.variables[item_var] = saved_item
        elif item_var in self.variables:
            del self.variables[item_var]

        if has_index:
            if saved_index is not None:
                self.variables[index_var] = saved_index
            elif index_var in self.variables:
                del self.variables[index_var]

    def split_collection_items(self, items_str):
        items = []
        current_tokens = []
        i = 0
        tokens = items_str.split()

        while i < len(tokens):
            token = tokens[i]
            token_lower = token.lower()

            if token_lower == "and" and i + 1 < len(tokens) and tokens[i + 1].lower() == "through":
                if current_tokens:
                    items.append(" ".join(current_tokens))
                    current_tokens = []
                i += 1
                continue
            elif token_lower == "and" and (not current_tokens or "ritual" not in " ".join(current_tokens).lower()):
                if current_tokens:
                    items.append(" ".join(current_tokens))
                    current_tokens = []
                i += 1
                continue
            else:
                current_tokens.append(token)

            i += 1

        if current_tokens:
            items.append(" ".join(current_tokens))

        return items

    def evaluate_ritual_call(self, ritual_call):
        pattern = r'(\w+)(?: with (.+))?'
        match = re.match(pattern, ritual_call, re.IGNORECASE)
        if not match:
            raise SyntaxError("invalid ritual call syntax")

        name = match.group(1)
        args_str = match.group(2)

        if name not in self.functions:
            raise NameError(f"ritual {name} not found")

        func = self.functions[name]
        params = func["params"]

        if args_str:
            args_raw = [a.strip() for a in args_str.split("and")]
            args = []
            arg_var_names = []

            for arg in args_raw:
                if arg in self.variables:
                    arg_var_names.append(arg)
                    args.append(self.variables[arg])
                else:
                    arg_var_names.append(None)
                    args.append(self.evaluate_expression(arg))
        else:
            args = []
            arg_var_names = []

        if len(args) != len(params):
            raise ValueError(f"ritual {name} expects {len(params)} args, got {len(args)}")

        saved_param_values = {}
        for p in params:
            if p in self.variables:
                saved_param_values[p] = self.variables[p]

        for p, a in zip(params, args):
            self.variables[p] = a

        result = self.execute_body(func["body"])

        for i, (param, var_name) in enumerate(zip(params, arg_var_names)):
            if var_name is not None and param in self.variables:
                self.variables[var_name] = self.variables[param]

        for p in params:
            if p in saved_param_values:
                self.variables[p] = saved_param_values[p]
            else:
                if p in self.variables:
                    del self.variables[p]

        return result

    def handle_inscribe(self, statement):
        msg = statement[len("inscribe "):].strip()
        if msg.startswith('whispers of "') and msg.endswith('"'):
            print(msg[len('whispers of "'):-1])
            return

        try:
            val = self.evaluate_expression(msg)
            if isinstance(val, list):
                print(f"[{', '.join(str(v) for v in val)}]")
            else:
                print(val)
        except (ValueError, NameError):
            print(msg)

    def handle_ponder(self, words):
        if len(words) >= 4 and words[1] == "for" and words[3] == "moments":
            try:
                duration = self.parse_number(words[2])
                time.sleep(duration)
            except ValueError:
                raise SyntaxError("ponder duration must be a number")
        else:
            raise SyntaxError("use Ponder for <seconds> moments")

    def handle_banish(self, words):
        if len(words) < 3 or words[1].lower() != "the":
            raise SyntaxError("use Banish the <name>")
        name = words[2]
        if name in self.variables:
            del self.variables[name]
        else:
            raise NameError(f"cannot banish unknown entity {name}")

    def handle_gaze(self, words):
        if len(words) < 3 or words[1].lower() != "upon":
            raise SyntaxError("use Gaze upon <condition>")
        condition = " ".join(words[2:])
        result = self.evaluate_condition(condition)
        print(f"Gazing reveals: {result}")

    def handle_transmute(self, statement):
        lower = statement.lower()
        if " into " not in lower:
            raise SyntaxError("use Transmute <name> into <type>")

        parts = re.split(r'\s+into\s+', statement, flags=re.IGNORECASE, maxsplit=1)
        if len(parts) != 2:
            raise SyntaxError("use Transmute <name> into <type>")

        var_part = parts[0].strip()
        if var_part.lower().startswith("transmute "):
            var_name = var_part[len("transmute "):].strip()
        else:
            raise SyntaxError("use Transmute <name> into <type>")

        target_type = parts[1].strip().lower()

        if var_name in self.variables:
            value = self.variables[var_name]
        else:
            value = self.evaluate_expression(var_name)

        try:
            if target_type == "number":
                if isinstance(value, str) and 'point' in value.lower():
                    value = self.parse_number(value)
                else:
                    value = float(value) if '.' in str(value) else int(value)
            elif target_type == "text":
                value = str(value)
            elif target_type == "truth":
                value = bool(value)
            else:
                raise ValueError(f"unknown transmutation target {target_type}")
        except Exception as e:
            raise ValueError(f"failed to transmute {var_name}: {e}")

        self.variables[var_name] = value
        return value

    def handle_conjure(self, statement):
        lower = statement.lower()

        if " to begin" in lower:
            pattern = r'Conjure ritual named (\w+) with (.+?) to begin'
            match = re.match(pattern, statement, re.IGNORECASE)
            if not match:
                raise SyntaxError("use Conjure ritual named <name> with <params> to begin: ... end ritual")
            name, params_str = match.groups()
            params = [p.strip() for p in params_str.split("and")]

            body_statements = self.collect_block_from_context("end ritual")

            if not body_statements:
                raise SyntaxError("ritual body is empty")

            self.functions[name] = {
                "params": params,
                "body": body_statements
            }
        else:
            pattern = r'Conjure ritual named (\w+) with (.+?) to (.+)'
            match = re.match(pattern, statement, re.IGNORECASE)
            if not match:
                raise SyntaxError("use Conjure ritual named <name> with <params> to <body>")
            name, params_str, body = match.groups()
            params = [p.strip() for p in params_str.split("and")]
            body = body.strip()
            if body.endswith('.') or body.endswith(':'):
                body = body[:-1].strip()
            self.functions[name] = {
                "params": params,
                "body": [body]
            }

    def handle_return(self, statement):
        parts = statement.split(maxsplit=1)
        if len(parts) < 2:
            raise SyntaxError("use Return <value>")
        value_expr = parts[1].strip()
        return self.evaluate_expression(value_expr)

    def handle_invoke(self, statement):
        pattern = r'Invoke the ritual (\w+)(?: with (.+))?'
        match = re.match(pattern, statement, re.IGNORECASE)
        if not match:
            raise SyntaxError("use Invoke the ritual <name> with <args>")
        name, args_str = match.groups()
        ritual_call = name
        if args_str:
            ritual_call += " with " + args_str
        return self.evaluate_ritual_call(ritual_call)

    def handle_conditional(self, statement):
        lower = statement.lower()
        start = lower.find("if the signs show") + len("if the signs show")
        then_pos = lower.find("then")
        if then_pos == -1:
            raise SyntaxError("conditional must include then")

        cond = statement[start:then_pos].strip()
        cond = self.remove_filler_words(cond)

        otherwise_pos = lower.find(" otherwise ")

        if otherwise_pos != -1:
            then_action = statement[then_pos + len("then"):otherwise_pos].strip()
            else_action = statement[otherwise_pos + len(" otherwise "):].strip()

            if self.evaluate_condition(cond):
                return self.execute_statement(then_action)
            else:
                return self.execute_statement(else_action)
        else:
            then_action = statement[then_pos + len("then"):].strip()
            if self.evaluate_condition(cond):
                return self.execute_statement(then_action)

    def handle_loop(self, statement):
        statement = statement.strip()
        lower = statement.lower()
        match = re.search(r'repeat the incantation (\w+) times', lower)
        if not match:
            raise SyntaxError("use Repeat the incantation <number> to begin <action>")
        count_str = match.group(1)
        try:
            count = int(count_str)
        except ValueError:
            if count_str in self.variables:
                count = int(self.variables[count_str])
            else:
                raise SyntaxError("use Repeat the incantation <number> to begin <action>")
        body_tokens = []
        if "do" in lower:
            do_pos = lower.find("do") + 2
            body_text = statement[do_pos:].strip()
            if body_text:
                body_statements = re.split(r'\.\s+', body_text)
                for s in body_statements:
                    s = s.strip()
                    if s.endswith('.') or s.endswith(':'):
                        s = s[:-1].strip()
                    if s:
                        body_tokens.append(s)

        if not body_tokens:
            body_tokens = self.collect_block_from_context("end loop")

        if not body_tokens:
            raise SyntaxError("loop body is empty")

        for _ in range(count):
            result = self.execute_body(body_tokens)
            if result is not None:
                return result

    def parse_number(self, text):
        text = text.strip()

        if 'point' in text.lower():
            text = re.sub(r'point', '.', text, flags=re.IGNORECASE)

        try:
            num = float(text)
            if num.is_integer():
                return int(num)
            return num
        except ValueError:
            raise ValueError(f"Cannot parse '{text}' as a number")

    def evaluate_condition(self, condition):
        cond_lower = condition.lower()

        or_parts = re.split(r'\s+or\s+', condition, flags=re.IGNORECASE)
        if len(or_parts) > 1:
            for part in or_parts:
                if self.evaluate_condition(part.strip()):
                    return True
            return False

        and_parts = re.split(r'\s+and\s+', condition, flags=re.IGNORECASE)
        if len(and_parts) > 1:
            for part in and_parts:
                if not self.evaluate_condition(part.strip()):
                    return False
            return True

        if cond_lower.startswith("not "):
            inner = condition[4:].strip()
            return not self.evaluate_condition(inner)

        if " equals " in cond_lower:
            parts = re.split(r'\s+equals\s+', condition, flags=re.IGNORECASE, maxsplit=1)
            a, b = parts[0].strip(), parts[1].strip()
            return self.evaluate_expression(a) == self.evaluate_expression(b)

        if " greater than " in cond_lower:
            parts = re.split(r'\s+greater than\s+', condition, flags=re.IGNORECASE, maxsplit=1)
            a, b = parts[0].strip(), parts[1].strip()
            return self.evaluate_expression(a) > self.evaluate_expression(b)
        if " less than " in cond_lower:
            parts = re.split(r'\s+less than\s+', condition, flags=re.IGNORECASE, maxsplit=1)
            a, b = parts[0].strip(), parts[1].strip()
            return self.evaluate_expression(a) < self.evaluate_expression(b)

        if cond_lower == "truth":
            return True
        if cond_lower == "falsehood":
            return False

        if condition.strip() in self.variables:
            return bool(self.variables[condition.strip()])

        return False

    def _evaluate_arithmetic(self, expr, expr_lower, keyword, op):
        if keyword not in expr_lower:
            return None
        parts = re.split(r'\s+' + keyword + r'\s+', expr, flags=re.IGNORECASE, maxsplit=1)
        if len(parts) != 2:
            return None
        a = self.evaluate_expression(parts[0].strip())
        b = self.evaluate_expression(parts[1].strip())
        if not isinstance(a, (int, float)):
            raise TypeError(f"Expected number, got {type(a).__name__}: {a}")
        if not isinstance(b, (int, float)):
            raise TypeError(f"Expected number, got {type(b).__name__}: {b}")
        return op(a, b)

    _ARITHMETIC_OPS = [
        ("multiplied by", operator.mul),
        ("divided by", None),
        ("greater by", operator.add),
        ("lesser by", operator.sub),
    ]

    def evaluate_expression(self, expr):
        expr = expr.strip()
        expr_lower = expr.lower()

        if "collection holding" in expr_lower:
            pattern = r'collection holding (.+)'
            match = re.search(pattern, expr, re.IGNORECASE)
            if match:
                items_str = match.group(1).strip()
                items = self.split_collection_items(items_str)
                return [self.evaluate_expression(item.strip()) for item in items]

        if " bound with " in expr_lower:
            parts = re.split(r'\s+bound with\s+', expr, flags=re.IGNORECASE)
            return "".join(str(self.evaluate_expression(part.strip())) for part in parts)

        if " at position " in expr_lower:
            pattern = r'(\w+)\s+at position\s+(.+)'
            match = re.match(pattern, expr, re.IGNORECASE)
            if match:
                array_name = match.group(1).strip()
                index_expr = match.group(2).strip()

                array = self.get_list_variable(array_name)

                index = self.evaluate_expression(index_expr)
                if not isinstance(index, int):
                    raise TypeError(f"index must be a number, got {type(index).__name__}")

                if index < 0 or index >= len(array):
                    raise IndexError(f"index {index} out of range for collection of length {len(array)}")

                return array[index]

        if expr_lower.startswith("length of "):
            array_name = expr[len("length of "):].strip()
            array = self.get_list_variable(array_name)
            return len(array)

        if "through ritual" in expr_lower:
            pattern = r'through ritual\s+(\w+)(?:\s+with\s+(.+?))?(?=\s+and\s+through|$)'
            match = re.search(pattern, expr, re.IGNORECASE)
            if match:
                name = match.group(1)
                args = match.group(2).strip() if match.group(2) else None
                ritual_call = name
                if args:
                    ritual_call += " with " + args
                return self.evaluate_ritual_call(ritual_call)

        if "invoke the ritual" in expr_lower:
            pattern = r'invoke the ritual (\w+)(?: with (.+))?'
            match = re.search(pattern, expr, re.IGNORECASE)
            if match:
                invoke_start = match.start()
                invoke_end = match.end()

                name = match.group(1)
                args_str = match.group(2)
                ritual_call = name
                if args_str:
                    ritual_call += " with " + args_str
                result = self.evaluate_ritual_call(ritual_call)

                remaining = expr[:invoke_start] + str(result) + expr[invoke_end:]
                remaining = remaining.strip()

                if remaining and remaining != str(result):
                    return self.evaluate_expression(remaining)

                return result

        # Handle division separately for zero-check and integer coercion
        if "divided by" in expr_lower:
            parts = re.split(r'\s+divided by\s+', expr, flags=re.IGNORECASE, maxsplit=1)
            if len(parts) == 2:
                a = self.evaluate_expression(parts[0].strip())
                b = self.evaluate_expression(parts[1].strip())
                if not isinstance(a, (int, float)):
                    raise TypeError(f"Expected number, got {type(a).__name__}: {a}")
                if not isinstance(b, (int, float)):
                    raise TypeError(f"Expected number, got {type(b).__name__}: {b}")
                if b == 0:
                    raise ZeroDivisionError("Cannot divide by zero")
                result = a / b
                if isinstance(a, int) and isinstance(b, int) and result.is_integer():
                    return int(result)
                return result

        for keyword, op in self._ARITHMETIC_OPS:
            if op is None:
                continue
            result = self._evaluate_arithmetic(expr, expr_lower, keyword, op)
            if result is not None:
                return result

        if expr in self.variables:
            return self.variables[expr]

        try:
            return self.parse_number(expr)
        except ValueError:
            pass

        if expr_lower == "truth":
            return True
        if expr_lower == "falsehood":
            return False

        if expr.startswith('whispers of "') and expr.endswith('"'):
            return expr[len('whispers of "'):-1]

        return expr

    def handle_reveal(self, statement):
        pattern = r'Reveal knowledge from "([^"]+)" into (\w+)'
        match = re.match(pattern, statement, re.IGNORECASE)
        if not match:
            raise SyntaxError('use Reveal knowledge from "path/to/file" into <variable>')

        filepath = match.group(1)
        var_name = match.group(2)

        try:
            with open(filepath, 'r') as file:
                content = file.read()
            self.variables[var_name] = content
        except FileNotFoundError:
            raise FileNotFoundError(f"The tome at '{filepath}' could not be found")
        except PermissionError:
            raise PermissionError(f"The tome at '{filepath}' is sealed with powerful wards")
        except Exception as e:
            raise RuntimeError(f"Failed to extract knowledge from '{filepath}': {e}")

    def handle_dissect(self, statement):
        pattern = r'Dissect (\w+) by "([^"]*)" into (\w+)'
        match = re.match(pattern, statement, re.IGNORECASE)
        if not match:
            raise SyntaxError('use Dissect <variable> by "<delimiter>" into <result_variable>')

        source_var = match.group(1)
        delimiter = match.group(2)
        result_var = match.group(3)

        source_text = self.get_str_variable(source_var)
        parts = source_text.split(delimiter)
        self.variables[result_var] = parts

    def handle_extract(self, statement):
        pattern = r'Extract verse (\d+) from (\w+) into (\w+)'
        match = re.match(pattern, statement, re.IGNORECASE)
        if not match:
            raise SyntaxError('use Extract verse <line_number> from <variable> into <result_variable>')

        line_num = int(match.group(1)) - 1  # Convert to 0-indexed
        source_var = match.group(2)
        result_var = match.group(3)

        source_text = self.get_str_variable(source_var)
        lines = source_text.splitlines()
        if line_num < 0 or line_num >= len(lines):
            raise IndexError(f"verse {line_num + 1} does not exist in text (has {len(lines)} verses)")

        self.variables[result_var] = lines[line_num]

    def handle_transform(self, statement):
        pattern = r'Transform (\w+) replacing "([^"]*)" with "([^"]*)" into (\w+)'
        match = re.match(pattern, statement, re.IGNORECASE)
        if not match:
            raise SyntaxError('use Transform <variable> replacing "<old>" with "<new>" into <result_variable>')

        source_var = match.group(1)
        old_text = match.group(2)
        new_text = match.group(3)
        result_var = match.group(4)

        source_text = self.get_str_variable(source_var)
        result = source_text.replace(old_text, new_text)
        self.variables[result_var] = result

    def handle_decipher(self, statement):
        pattern = r'Decipher (\w+) with pattern "([^"]*)" into (.+)'
        match = re.match(pattern, statement, re.IGNORECASE)
        if not match:
            raise SyntaxError('use Decipher <variable> with pattern "<regex>" into <result1> [and <result2>...]')

        source_var = match.group(1)
        regex_pattern = match.group(2)
        result_vars_str = match.group(3)
        result_vars = [v.strip() for v in result_vars_str.split(" and ")]

        source_text = self.get_str_variable(source_var)

        regex_match = re.match(regex_pattern, source_text)
        if not regex_match:
            raise ValueError(f"Pattern did not match the text in {source_var}")

        groups = regex_match.groups()
        if not groups:
            raise ValueError(f"Pattern did not capture any groups in {source_var}")

        if len(groups) < len(result_vars):
            raise ValueError(f"Pattern captured {len(groups)} groups but {len(result_vars)} result variables were specified")

        for var, value in zip(result_vars, groups):
            self.variables[var] = value


def _stmt_handler(fn):
    return lambda self, statement, words: fn(self, statement)

def _words_handler(fn):
    return lambda self, statement, words: fn(self, words)

SpellScriptInterpreter._dispatch = {
    "summon": _stmt_handler(SpellScriptInterpreter.handle_summon),
    "enchant": _stmt_handler(SpellScriptInterpreter.handle_enchant),
    "inscribe": _stmt_handler(SpellScriptInterpreter.handle_inscribe),
    "inquire": _stmt_handler(SpellScriptInterpreter.handle_inquire),
    "append": _stmt_handler(SpellScriptInterpreter.handle_append),
    "ponder": _words_handler(SpellScriptInterpreter.handle_ponder),
    "banish": _words_handler(SpellScriptInterpreter.handle_banish),
    "gaze": _words_handler(SpellScriptInterpreter.handle_gaze),
    "transmute": _stmt_handler(SpellScriptInterpreter.handle_transmute),
    "conjure": _stmt_handler(SpellScriptInterpreter.handle_conjure),
    "invoke": _stmt_handler(SpellScriptInterpreter.handle_invoke),
    "return": _stmt_handler(SpellScriptInterpreter.handle_return),
    "reveal": _stmt_handler(SpellScriptInterpreter.handle_reveal),
    "dissect": _stmt_handler(SpellScriptInterpreter.handle_dissect),
    "extract": _stmt_handler(SpellScriptInterpreter.handle_extract),
    "transform": _stmt_handler(SpellScriptInterpreter.handle_transform),
    "decipher": _stmt_handler(SpellScriptInterpreter.handle_decipher),
}
