<h1 align="center">Scientific Calculator — Python Tkinter</h1>

<p align="center">
<img src="https://img.shields.io/badge/Language-Python-blue" />
<img src="https://img.shields.io/badge/Interface-GUI-orange" />
<img src="https://img.shields.io/badge/Built%20With-Tkinter-brightgreen" />
<img src="https://img.shields.io/badge/License-MIT-yellow" />
</p>

## Table of contents

- [What is Tkinter?](#what-is-tkinter)
- [Description](#description)
- [Installation](#installation)
- [Requirements](#requirements)
- [Features](#features)
- [How it works](#how-it-works)
- [Project structure](#project-structure)
- [Screenshots](#screenshots)
- [License](#license)

## What is Tkinter?

[Tkinter](https://docs.python.org/3/library/tkinter.html) is the standard GUI library for Python. It ships with most Python installations and is used here for buttons, labels, and the expression entry field.

## Description

A desktop scientific calculator built with Python and Tkinter. The interface builds an expression; a separate engine normalizes symbols, validates the expression with Python’s AST, and evaluates it using a math-only namespace (not unrestricted `eval`).

Trigonometry supports **degrees** and **radians**. `%` is **percent** (`50%` = `0.5`). Absolute value uses `abs(` (the `|x|` button), which is unambiguous for expression evaluation.

## Installation

1. Clone this repository:

```
git clone https://github.com/shiva-rsl/Python_Tkinter_Calculator.git
```

2. Open the project folder:

```
cd Python_Tkinter_Calculator
```

3. Run the calculator:

```
python calculator_tkinter.py
```

## Requirements

- Python 3.10+
- Tkinter (included with most Python installs)

On Debian/Ubuntu, if Tkinter is missing:

```
sudo apt install python3-tk
```

## Features

- Arithmetic: `+`, `-`, `×`, `÷`, `^`, parentheses
- Percent: `50%` → `0.5`
- Trigonometry: `sin`, `cos`, `tan` with Deg / Rad mode
- Hyperbolic: `sinh`, `cosh`, `tanh`
- Logs: `log10`, `log2`, `ln`
- `√`, `exp`, `n!`, `1/x`, `x²`, `x³`, `x^y`
- Constants `π` and `e`, with implicit multiplication (`2π`, `2(3+4)`)
- Absolute value via `|x|` → `abs(`
- `CE` clears the current entry; `AC` clears the entry and the history line
- Keyboard: type in the field, `Enter` calculates, `Esc` is all-clear; `*` and `/` become `×` and `÷`
- Errors show in the status label instead of crashing (division by zero, domain errors, unmatched parentheses)

## How it works

1. Buttons insert tokens into the entry field.
2. `engine.py` maps display symbols (`×`, `÷`, `^`, `π`, `√`, `ln`, `%`, `!`) to Python.
3. The AST is checked so only math names and operators are allowed.
4. `sin` / `cos` / `tan` use degree or radian mode; hyperbolic functions always use radians.

Run the engine tests:

```
python -m unittest test_engine.py
```

## Project structure

```
calculator_tkinter.py   # Tkinter UI
engine.py               # Expression parsing and evaluation
test_engine.py          # Unit tests for the engine
LICENSE                 # MIT
```

## Screenshots

Light-themed scientific calculator GUI:

<img src="Screenshots/calc.png" width="300" alt="Scientific calculator screenshot">

Add `Screenshots/calc.png` after you capture the running app (the window is 500×760).

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
