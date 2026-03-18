# emdee

A lisp for literate programming — where your documentation, code, and tests are the same file.

Stop writing docs, logic, and tests in three separate places. Write them all at once in a single `.emdee` file.

## The idea

Every valid Markdown file is a valid emdee file. Rename any `.md` to `.emdee` and it runs as-is. From there, you can add computation incrementally — embed expressions in your prose, add code blocks that render into the document, and assert what the output should look like.

The result of running an emdee file is a rendered Markdown document. Code blocks execute and their output is woven back into the doc. This makes emdee well-suited for:

- **Self-testing documentation** — assert that your examples produce the output you claim
- **README-driven development** — write the interface in the README first, then make it pass
- **Docs generation** — use the built-in language to compose and transform Markdown programmatically

## Usage

```sh
emdee render file.emdee
emdee test file.emdee
```

## Syntax

### Code blocks

Fenced code blocks tagged `emdee` are executed. Their output is rendered into the document in place of the block.

```emdee
(list "eggs" "milk" "bananas")
```

- eggs
- milk
- bananas

### Inline expressions

```emdee
(define source-file "README.emdee")
(define date today)
```

Use backticks to embed expressions directly in prose like so:

```plaintext
This document was generated from `emdee source-file` on `emdee date`.
```

This document was generated from README.emdee on 2025-03-17.

### Testing

Testing in emdee is a bit different. `emdee test [FILE]` compares the rendered file to the result on disk which represents your expectation of results. This file itself is a rendered result that has been used to test the development version of emdee!
