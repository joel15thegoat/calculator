# Scientific Calculator & Grapher

A Tkinter-based scientific calculator with plotting support.

## Features

- Scalar evaluation of mathematical expressions
- Degree-based trigonometric functions (`sin`, `cos`, `tan`, and inverses)
- Implicit multiplication support (`2x`, `3pi`, `2sin(30)`, `3(4+5)`)
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

## Running the App

From the project root, run:

```powershell
python "calculator v3.py"
```

This opens the calculator window where you can type or click buttons to build expressions.

## Example Expressions

- `2+2`
- `5^2`
- `sin(30)` → returns `0.5`
- `cos(60)` → returns `0.5`
- `tan(45)` → returns `1`
- `log(100)` → returns `2`
- `ln(2.71828)` → returns `1`
- `36x` → treated as `36*x` for plotting
- `2x+3` → plot expression containing `x`

## Graphing Expressions

To plot a function, enter an expression with the variable `x`, and press `Graph`.

Examples:

- `x^2`
- `2x+5`
- `sin(x)`
- `3x^3 - x`

A prompt appears asking whether to open the graph in a new window or reuse the current window.

## Notes

- All trigonometry uses degrees, not radians.
- `log` is base 10 by default.
- `ln` is the natural logarithm.
- The expression parser converts `^` to `**` internally.

## Contributing

1. Fork the repository
2. Clone your fork
3. Edit `calculator v3.py` or improve the README
4. Commit and push your changes
5. Open a pull request

## License

This project is released under the MIT License. Feel free to use and modify it.
