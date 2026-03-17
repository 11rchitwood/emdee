# emdee

An environment for literate programming — where your documentation, code, and tests are the same file.

Stop writing docs, logic, and tests in three separate places.
Write them all at once in a single `.emdee` file.

## The idea

Every valid Markdown file is a valid emdee file. Rename any `.md` to `.emdee` and it runs as-is. From there, you can add computation incrementally — embed expressions in your prose, add code blocks that render into the document, and assert what the output should look like.

The result of running an emdee file is a rendered Markdown document. Code blocks execute and their output is woven back into the doc. This makes emdee well-suited for:

- **Self-testing documentation** — assert that your examples produce the output you claim
- **README-driven development** — write the interface in the README first, then make it pass
- **Docs generation** — use the built-in language to compose and transform Markdown programmatically

## Usage

```sh
emdee run file.emdee        # run and render
emdee test file.emdee       # run and check all assertions
emdee watch file.emdee      # re-run on save
```

## Syntax

### Code blocks

Fenced code blocks tagged `emdee` are executed. Their output is rendered into the document in place of the block.

````markdown
```emdee
heading 1 "Getting Started"
paragraph "Install emdee and you're ready to go."
```
````

### Inline expressions

Use `{{ }}` to embed expressions directly in prose:

```markdown
This document was generated from {{ source-file }} on {{ date }}.
```

### Assertions

Use `!>` after an expression to assert the rendered Markdown output:

````markdown
```emdee
bold "hello"
!> **hello**
```
````

If an assertion fails, `emdee test` exits non-zero and reports the diff.

## The built-in language

emdee ships with a small DSL designed for manipulating Markdown. It operates on Markdown nodes — headings, paragraphs, lists, tables, links — rather than raw strings.

```emdee
heading 2 "Features"
list [
  "Self-testing docs"
  "Inline expressions"
  "README-driven development"
]
```

The language is intentionally minimal. Its job is to compose and transform documents, not to be a general-purpose scripting language.

## Adapters

The built-in language covers the core use case. Adapters for other languages are planned, so you'll be able to embed Python, JavaScript, or other runtimes as code block executors.

## License

[MIT](LICENSE)
