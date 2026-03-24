# emdee roadmap

The milestones below are ordered by dependency. Correctness and language completeness come first; tooling and distribution follow once the foundation is stable.

## Test coverage

Before any significant refactor, the Python backend needs a comprehensive test suite. The Copilot review caught real bugs — arity validation, `LispList` inconsistency, unterminated strings, fence detection — that only surfaced through code review. A test suite catches these automatically and prevents regressions as the codebase evolves.

The goal is 100% coverage of `emdee.py`: the tokenizer, parser, evaluator, built-ins, Markdown processor, and CLI. Tests should be runnable with a single command and enforced in CI on every push.

## Error reporting

Currently, errors in emdee code blocks are embedded as HTML comments in the rendered output. The run succeeds and the check passes — the broken output is committed silently. This is the wrong behaviour. Errors should surface to the terminal, fail the run, and never appear in a rendered `.md` file.

This touches the evaluator, the block renderer, and the CLI exit code.

## Load / module system

Before the implementation can be moved into emdee itself, emdee needs a way to load other `.emdee` files. A `(load "file.emdee")` form — or equivalent — lets the standard library and built-in extensions be written as literate emdee documents and composed at startup.

This is a prerequisite for self-hosting.

## Self-hosting

Move as much of the implementation as possible into emdee itself. The backend becomes a thin layer — file I/O, a minimal Lisp evaluator, and a Markdown processor — while the standard library, built-in forms, and higher-level behaviour are written in `.emdee` files loaded at startup.

This milestone validates that emdee is expressive enough for real work. It also means most of the implementation is readable as literate emdee documents, tested by the emdee tool itself.

## Backend migration

Once the backend is thin and the test suite guards against regressions, migrate from Python to a compiled language — Go is the leading candidate. Go produces a single static binary with no runtime dependency, which is the right distribution story for a CLI tool. Users should be able to install emdee with a single command and run it anywhere.

The emdee-layer code (written in `.emdee` files) is portable across backends by definition.

## Formatting

A canonical formatter for `.emdee` files, in the spirit of `gofmt`. Code blocks are formatted consistently; prose is left untouched. The formatter is authoritative — no style debates, no configuration. It runs as <!-- emdee error: undefined: 'fmt' --> and is enforced in CI alongside the render check.

## Editor and LSP support

A Language Server Protocol implementation for `.emdee` files: diagnostics (syntax errors, undefined symbols), inline evaluation results, go-to-definition, and formatting on save. The formatter milestone is a natural prerequisite.

The goal is first-class support in VS Code, with other editors following via the standard LSP interface.

## Static site

Extend the renderer to produce a deployable static site from a collection of `.emdee` files. The project's own documentation — this roadmap, the README, future guides — should be deployable as the emdee homepage directly from the repository, with no separate build step.

## New features

_Placeholder — ideas to be added._
