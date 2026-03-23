#!/usr/bin/env python3
"""emdee — a Lisp environment for literate programming."""

import re
import sys
import argparse
import difflib
from datetime import date
from pathlib import Path


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

class Symbol(str):
    """A Lisp symbol — distinct from a string literal."""


class LispList:
    """A list value that renders as Markdown bullet points."""
    def __init__(self, items):
        self.items = list(items)

    def __repr__(self):
        return '\n'.join(f'- {item}' for item in self.items)


# ---------------------------------------------------------------------------
# Lexer / Parser
# ---------------------------------------------------------------------------

def tokenize(src):
    tokens = []
    i = 0
    n = len(src)
    while i < n:
        c = src[i]
        if c in ' \t\n\r':
            i += 1
        elif c == ';':
            while i < n and src[i] != '\n':
                i += 1
        elif c in '()':
            tokens.append(c)
            i += 1
        elif c == '"':
            j = i + 1
            while j < n and src[j] != '"':
                if src[j] == '\\':
                    j += 1
                j += 1
            if j >= n:
                raise SyntaxError(f'unterminated string literal at position {i}')
            tokens.append(src[i:j + 1])
            i = j + 1
        else:
            j = i
            while j < n and src[j] not in ' \t\n\r()':
                j += 1
            tokens.append(src[i:j])
            i = j
    return tokens


def _parse_one(tokens, pos):
    if pos >= len(tokens):
        raise SyntaxError('unexpected EOF')
    tok = tokens[pos]
    if tok == '(':
        pos += 1
        items = []
        while pos < len(tokens) and tokens[pos] != ')':
            item, pos = _parse_one(tokens, pos)
            items.append(item)
        if pos >= len(tokens):
            raise SyntaxError("missing ')'")
        return items, pos + 1
    if tok == ')':
        raise SyntaxError("unexpected ')'")
    if tok.startswith('"'):
        return tok[1:-1].replace('\\"', '"').replace('\\n', '\n'), pos + 1
    try:
        return int(tok), pos + 1
    except ValueError:
        pass
    try:
        return float(tok), pos + 1
    except ValueError:
        pass
    return Symbol(tok), pos + 1


def parse_all(src):
    tokens = tokenize(src)
    exprs = []
    pos = 0
    while pos < len(tokens):
        expr, pos = _parse_one(tokens, pos)
        exprs.append(expr)
    return exprs


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

class Env:
    def __init__(self, bindings=None, parent=None):
        self.b = {}
        if bindings:
            self.b.update(bindings)
        self.parent = parent

    def get(self, k):
        if k in self.b:
            return self.b[k]
        if self.parent:
            return self.parent.get(k)
        raise NameError(f'undefined: {k!r}')

    def set(self, k, v):
        self.b[k] = v

    def set_existing(self, k, v):
        if k in self.b:
            self.b[k] = v
        elif self.parent:
            self.parent.set_existing(k, v)
        else:
            raise NameError(f'undefined: {k!r}')


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

class Fn:
    def __init__(self, params, body, env, name=None):
        self.params = params
        self.body = body
        self.env = env
        self.name = name

    def __repr__(self):
        return f'#<fn {self.name or "?"}>'


def _call(fn, args):
    if callable(fn):
        return fn(*args)
    if isinstance(fn, Fn):
        if len(args) != len(fn.params):
            raise TypeError(
                f'{fn.name or "lambda"}: expected {len(fn.params)} arg(s), got {len(args)}'
            )
        env = Env(dict(zip(fn.params, args)), fn.env)
        result = None
        for e in fn.body:
            result = ev(e, env)
        return result
    raise TypeError(f'not callable: {fn!r}')


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------

def ev(expr, env):
    while True:
        if isinstance(expr, Symbol):
            return env.get(expr)
        if not isinstance(expr, list) or not expr:
            return expr  # self-evaluating: str literal, int, float, bool, None

        head = expr[0]

        if head == 'quote':
            return expr[1]

        if head == 'if':
            cond = ev(expr[1], env)
            expr = expr[2] if cond else (expr[3] if len(expr) > 3 else None)
            if expr is None:
                return None
            continue  # TCO

        if head == 'cond':
            for clause in expr[1:]:
                test = clause[0]
                if test == Symbol('else') or ev(test, env):
                    result = None
                    for b in clause[1:]:
                        result = ev(b, env)
                    return result
            return None

        if head == 'define':
            target = expr[1]
            if isinstance(target, list):
                name, *params = target
                env.set(Symbol(name), Fn(params, expr[2:], env, name=name))
            else:
                env.set(target, ev(expr[2], env))
            return None

        if head == 'lambda':
            return Fn(expr[1], expr[2:], env)

        if head == 'let':
            new_env = Env({}, env)
            for k, v_expr in expr[1]:
                new_env.set(Symbol(k), ev(v_expr, env))
            result = None
            for b in expr[2:]:
                result = ev(b, new_env)
            return result

        if head == 'begin':
            result = None
            for b in expr[1:]:
                result = ev(b, env)
            return result

        if head == 'set!':
            env.set_existing(expr[1], ev(expr[2], env))
            return None

        # Function call — TCO for user-defined functions
        fn = ev(head, env)
        args = [ev(a, env) for a in expr[1:]]
        if isinstance(fn, Fn):
            if len(args) != len(fn.params):
                raise TypeError(
                    f'{fn.name or "lambda"}: expected {len(fn.params)} arg(s), got {len(args)}'
                )
            env = Env(dict(zip(fn.params, args)), fn.env)
            for b in fn.body[:-1]:
                ev(b, env)
            expr = fn.body[-1]
            continue
        return fn(*args)


# ---------------------------------------------------------------------------
# Built-ins
# ---------------------------------------------------------------------------

def _mul(*args):
    r = 1
    for a in args:
        r *= a
    return r


def _div(a, b):
    if isinstance(a, int) and isinstance(b, int) and a % b == 0:
        return a // b
    return a / b


def _map(f, lst):
    items = lst.items if isinstance(lst, LispList) else lst
    return LispList(_call(f, [x]) for x in items)


def _filter(f, lst):
    items = lst.items if isinstance(lst, LispList) else lst
    return LispList(x for x in items if _call(f, [x]))


def make_env():
    builtins = {
        '+': lambda *a: sum(a),
        '-': lambda a, *r: a - sum(r) if r else -a,
        '*': _mul,
        '/': _div,
        '=': lambda a, b: a == b,
        '<': lambda a, b: a < b,
        '>': lambda a, b: a > b,
        '<=': lambda a, b: a <= b,
        '>=': lambda a, b: a >= b,
        'not': lambda a: not a,
        'cons': lambda a, b: LispList([a] + b.items) if isinstance(b, LispList) else [a] + (b if isinstance(b, list) else [b]),
        'car': lambda a: a.items[0] if isinstance(a, LispList) else a[0],
        'cdr': lambda a: LispList(a.items[1:]) if isinstance(a, LispList) else a[1:],
        'list': lambda *a: LispList(a),
        'null?': lambda a: (len(a.items) == 0 if isinstance(a, LispList) else a == [] or a is None),
        'pair?': lambda a: (len(a.items) > 0 if isinstance(a, LispList) else isinstance(a, list) and len(a) > 0),
        'str': lambda *a: ''.join(str(x) for x in a),
        'string-append': lambda *a: ''.join(str(x) for x in a),
        'number->string': str,
        'string->number': lambda s: int(s) if str(s).lstrip('-').isdigit() else float(s),
        'length': lambda a: len(a.items) if isinstance(a, LispList) else len(a),
        'map': _map,
        'filter': _filter,
        'today': date.today().isoformat(),
        '#t': True,
        '#f': False,
        'true': True,
        'false': False,
    }
    return Env({Symbol(k): v for k, v in builtins.items()})


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render(val):
    if val is None:
        return ''
    if isinstance(val, bool):
        return '#t' if val else '#f'
    if isinstance(val, LispList):
        return str(val)
    return str(val)


# ---------------------------------------------------------------------------
# Markdown processor
# ---------------------------------------------------------------------------

INLINE_RE = re.compile(r'`emdee ([^`]+)`')


def process(source, env):
    lines = source.split('\n')
    out = []
    i = 0
    in_fence = False  # inside a non-emdee fenced block

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()  # strip both ends for detection; emit original line

        if not in_fence and stripped == '```emdee':
            # Collect the emdee block
            code_lines = []
            i += 1
            while i < len(lines) and lines[i].strip() != '```':
                code_lines.append(lines[i])
                i += 1
            out.append('```emdee')
            out.extend(code_lines)
            out.append('```')
            i += 1  # move past closing fence

            # Evaluate
            block_out = eval_block('\n'.join(code_lines), env)

            # Skip the old output zone only if it matches the rendered output
            i = _skip_matching_output(lines, i, block_out)

            # Emit new output
            out.append('')
            if block_out:
                out.append(block_out)

        elif not in_fence and stripped.startswith('```'):
            # Opening a non-emdee fence (with or without language tag) — pass through verbatim
            in_fence = True
            out.append(line)
            i += 1

        elif in_fence and stripped == '```':  # closing fence (strip handles indentation)
            # Closing a non-emdee fence
            in_fence = False
            out.append(line)
            i += 1

        elif in_fence:
            # Inside a fence — emit verbatim, no inline substitution
            out.append(line)
            i += 1

        else:
            # Normal prose — process inline expressions
            out.append(process_inline(line, env))
            i += 1

    result = '\n'.join(out)
    if source.endswith('\n') and not result.endswith('\n'):
        result += '\n'
    return result


def _skip_matching_output(lines, i, expected):
    """Skip the next paragraph after a closing fence only if it matches expected.

    This prevents prose from being consumed: if the content following the fence
    does not exactly equal the freshly-rendered output, it is left in place.
    """
    n = len(lines)
    # Find the start of the next paragraph (skip leading blanks)
    j = i
    while j < n and lines[j].strip() == '':
        j += 1
    # If next non-blank is a fence or heading, nothing to skip
    if j >= n or lines[j].startswith('```') or lines[j].startswith('#'):
        return j
    # Read the candidate paragraph (one contiguous block of non-blank lines)
    k = j
    while k < n and lines[k].strip() != '':
        k += 1
    candidate = '\n'.join(lines[j:k])
    # Only skip it if it matches the rendered output exactly
    if candidate == expected:
        return k
    return i  # mismatch — leave it in place


def eval_block(code, env):
    try:
        exprs = parse_all(code)
    except SyntaxError as e:
        return f'<!-- emdee error: {e} -->'
    parts = []
    for expr in exprs:
        try:
            val = ev(expr, env)
            r = render(val)
            if r:
                parts.append(r)
        except Exception as e:
            parts.append(f'<!-- emdee error: {e} -->')
    return '\n'.join(parts)


def process_inline(line, env):
    def sub(m):
        code = m.group(1).strip()
        try:
            exprs = parse_all(code)
            val = None
            for e in exprs:
                val = ev(e, env)
            return render(val)
        except Exception as ex:
            return f'<!-- emdee error: {ex} -->'
    return INLINE_RE.sub(sub, line)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description='emdee literate programming tool')
    ap.add_argument('file', help='.emdee source file')
    ap.add_argument('--update', action='store_true',
                    help='overwrite .md with rendered output')
    args = ap.parse_args()

    src_path = Path(args.file)
    if not src_path.exists():
        sys.exit(f'emdee: not found: {args.file}')

    md_path = src_path.with_suffix('.md')
    source = src_path.read_text(encoding='utf-8')
    env = make_env()
    rendered = process(source, env)

    if args.update or not md_path.exists():
        md_path.write_text(rendered, encoding='utf-8')
        print(f'{"Updated" if args.update else "Created"}: {md_path}')
    else:
        existing = md_path.read_text(encoding='utf-8')
        if rendered == existing:
            print(f'OK: output matches {md_path}')
        else:
            sys.stderr.writelines(difflib.unified_diff(
                existing.splitlines(keepends=True),
                rendered.splitlines(keepends=True),
                fromfile=str(md_path),
                tofile='<rendered>',
            ))
            sys.exit(f'FAIL: {md_path} does not match rendered output')


if __name__ == '__main__':
    main()
