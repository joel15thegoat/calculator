# Scientific Calculator & Grapher

A Tkinter-based scientific calculator with plotting support.

## Features

- Scalar evaluation of mathematical expressions
- Degree-based trigonometric functions (`sin`, `cos`, `tan`, and inverses)
- Implicit multiplication support (`2x`, `3pi`, `2sin(30)`)
- Graph plotting for expressions containing `x`
- Option to open a new plot window or reuse the current one
- Safe evaluation sandbox for calculator and plot expressions

## Requirements

- Python 3.10+
- `numpy`
- `matplotlib`

## Installation

```powershell
python -m pip install numpy matplotlib
```

## Usage

Run the calculator script:

```powershell
python "calculator v3.py"
```

Use the on-screen buttons to enter expressions. For plotting, include the variable `x` and press `Graph`.

## Notes

- The app uses degrees for all trigonometric functions.
- `log` evaluates as base 10 by default, with `ln` as natural logarithm.
- Use `^` for exponentiation (it is converted internally to `**`).
