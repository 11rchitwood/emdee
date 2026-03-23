# emdee

A Lisp environment for literate programming — where your code, tests, and documentation coexist in a single file.

The primary goal is co-location: stop maintaining code in one place, tests in another, and docs in a third. Write them all together in a single `.emdee` file. The rendered Markdown document is a natural consequence of running that file, not the end goal in itself.

## The idea

Every valid Markdown file is a valid emdee file. Rename any `.md` to `.emdee` and it runs as-is. From there, you can add computation incrementally — embed expressions in your prose, add code blocks that execute inline, and commit the rendered output as your expected baseline.

The `.emdee` file is always the source of truth. Running it produces a `.md` file. This makes emdee well-suited for:

- **README-driven development** — write the interface in the README first, then make it pass
- **Self-testing documentation** — the rendered output is the test; if it changes unexpectedly, the test fails
- **Programmatic docs** — use the built-in Lisp to compose and transform Markdown from code

## Usage

```sh
emdee file.emdee          # run and assert output matches file.md
emdee file.emdee --update # run and overwrite file.md with the new output
```

The first time you run a file, `file.md` doesn't exist yet — emdee renders it. On every subsequent run, emdee compares the output to the committed `file.md`. If they differ, the run fails. To intentionally update the baseline:

```sh
emdee file.emdee --update
git diff file.md          # review what changed
git add file.md && git commit -m "update expected output"
```

The committed `file.md` becomes the new baseline. This keeps diffs visible and intentional in version control.

## The language

emdee's built-in language is a simple Lisp. It has first-class functions, closures, and a standard library of built-in forms for arithmetic, string manipulation, and Markdown composition. It does not expose user-facing macros — the built-in forms cover what you need for documentation and light computation. For heavy logic, emdee is designed to host other language runtimes.

## Syntax

### Code blocks

Fenced code blocks tagged `emdee` are executed. Their output is rendered into the document in place of the block. This is the core of co-location: prose describes what the code does, the code block proves it, and `emdee` verifies the proof on every run.

The `double` function multiplies its argument by 2:

```emdee
(define (double n) (* n 2))

(double 21)
```

42

### Inline expressions

Expressions can be embedded directly in prose using backticks prefixed with `emdee`. The expression is evaluated and its value substituted inline.

```emdee
(define source-file "README.emdee")
(define date today)
```

```plaintext
This document was generated from `emdee source-file` on `emdee date`.
```

This document was generated from README.emdee on 2026-03-23.

### List rendering

```emdee
(list "eggs" "milk" "bananas")
```

- eggs
- milk
- bananas

### Higher-order functions

State accumulates across blocks — `double` defined above is still in scope. `map` applies any function to a list:

```emdee
(map double (list 1 2 3 4 5))
```

- 2
- 4
- 6
- 8
- 10
