# TinyLang 1.0.0 "Atom"

TinyLang is a lightweight, C-styled programming language that compiles directly into clean Python code using the Lark parsing library. Designed as an extensible and structured alternative to regular expression-based tokenizers, TinyLang utilizes an Abstract Syntax Tree (AST) to handle complex, nested language constructs.

## Features

* **C-Style Syntax Operators:** Full support for increment and decrement operations (`++`, `--`) as well as compound assignments (`+=`, `-=`, `*=`, `/=`).
* **Adaptive Command Line Interface:** Native support for executing source files via single arguments, double-click execution, or running raw source code strings directly from the terminal.
* **Intelligent Type Interception:** The built-in `input()` runtime automatically determines and casts numerical input to integers, preventing type errors during arithmetic evaluations (`mod`, `div`).
* **I/O and Module Support:** Integrated runtime functions for robust file handling and file inclusion directives via the `use` keyword.

## Installation and Requirements

To run TinyLang from the source code, ensure you have Python 3.8+ installed along with the Lark parser:

```bash
pip install lark

```

## Usage

TinyLang offers three primary execution modes via the command line:

### 1. Execute a Source File

Pass the relative or absolute path of a `.tl` script to run it:

```bash
tinylang script.tl

```

### 2. Run Raw Code Directly

Execute short snippets or one-liners from the terminal using the `--code` flag:

```bash
tinylang --code "a = 10; while (a < 100): { print(a); a++ }"

```

### 3. Display Help Interface

Access the built-in command line documentation:

```bash
tinylang --help

```

## Language Syntax Overview

Below is a brief demonstration of loops, inline increments, and block scopes in TinyLang:

```text
// Initialize counter
counter = 0;

// Execute standard while loop
while (counter < 5): {
    print("Current index:", counter);
    counter++;
}

```

## Architecture

The compilation pipeline operates in three distinct phases:

1. **Parsing:** The Lark LALR(1) parser processes the source stream against the grammar defined in `grammar/tinylang.lark`.
2. **AST Transformation:** The `TinyLangToPythonCompiler` transformer traverses the node tree and maps the structures to their equivalent Python syntax.
3. **Execution:** The generated Python payload is safely evaluated in an isolated runtime environment using a managed subprocess.

## License

This project is open-source software licensed under the terms of the MIT License. For more details, see the accompanying LICENSE file.
