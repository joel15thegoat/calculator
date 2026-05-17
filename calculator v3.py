"""Scientific Calculator & Grapher.

This Tkinter application provides a scientific calculator UI, safe
expression evaluation for scalar calculations, and algebraic function
plotting with optional new or shared Matplotlib windows.

The calculator uses degree-based trigonometry throughout for consistency.
"""

import tkinter as tk
from tkinter import simpledialog, messagebox
import math
import re
import numpy as np
import matplotlib.pyplot as plt

root = tk.Tk()
root.title("Scientific Calculator & Grapher (Safer & Standardized)")

# Entry widget
entry = tk.Entry(root, width=25, font=("Adorn", 18), borderwidth=5, relief="ridge")
entry.grid(row=0, column=0, columnspan=5)

# Safe eval environments
SAFE_GLOBALS = {"__builtins__": None}
SAFE_MATH_ENV = {
    'sin': lambda x: math.sin(math.radians(x)),
    'cos': lambda x: math.cos(math.radians(x)),
    'tan': lambda x: math.tan(math.radians(x)),
    'asin': lambda y: math.degrees(math.asin(y)),
    'acos': lambda y: math.degrees(math.acos(y)),
    'atan': lambda y: math.degrees(math.atan(y)),
    'sqrt': math.sqrt, 'log': math.log10, 'log10': math.log10, 'ln': math.log,
    'abs': abs, 'pi': math.pi, 'e': math.e, 'pow': pow
}

# NumPy environment for plotting (uses degrees for trig functions)

PLOT_ENV = {
    'sin': lambda x: np.sin(np.radians(x)), 'cos': lambda x: np.cos(np.radians(x)), 'tan': lambda x: np.tan(np.radians(x)),
    'asin': lambda y: np.degrees(np.arcsin(y)), 'acos': lambda y: np.degrees(np.arccos(y)), 'atan': lambda y: np.degrees(np.arctan(y)),
    'sqrt': np.sqrt, 'log': np.log10, 'log10': np.log10, 'ln': np.log,
    'abs': np.abs, 'pi': np.pi, 'e': np.e
}

# Plot eval globals: keep sandboxed plotting safe with no builtins access
SafPlotGlob = {"__builtins__": {}}

# Functions
def click(value):
    """Insert the pressed button value into the calculator input."""
    entry.insert(tk.END, value)

def clear():
    """Clear the calculator input field."""
    entry.delete(0, tk.END)

def backspace():
    """Remove the last character from the calculator input field."""
    current_text = entry.get()
    entry.delete(0, tk.END)
    entry.insert(0, current_text[:-1])

def normalize_expression(expr):
    """Normalize an expression before evaluation.

    Converts '^' to '**' for exponentiation and inserts implicit
    multiplication operators where needed.
    """
    expr = expr.replace('^', '**')
    # Insert '*' between a number and a following value or function.
    expr = re.sub(
        r'(\d)(?=\s*(?:x\b|pi\b|e\b|sin\b|cos\b|tan\b|asin\b|acos\b|atan\b|log\b|ln\b|sqrt\b|abs\b|\())',
        r'\1*',
        expr,
    )
    expr = re.sub(
        r'((?:x|pi|e)\b|\))\s*(?=(?:x\b|pi\b|e\b|sin\b|cos\b|tan\b|asin\b|acos\b|atan\b|log\b|ln\b|sqrt\b|abs\b|\())',
        r'\1*',
        expr,
    )
    return expr

def calculate():
    """Evaluate the current expression from the calculator display."""
    try:
        expr = normalize_expression(entry.get())
        # Detect standalone variable 'x' and prevent scalar evaluation.
        if re.search(r'\bx\b', expr):
            messagebox.showwarning("Input Error", "Please use the 'Graph' button to plot expressions containing 'x'.")
            return
        # Evaluate with a restricted math environment.
        result = eval(expr, SAFE_GLOBALS, SAFE_MATH_ENV)
        entry.delete(0, tk.END)
        entry.insert(0, str(result))
    except Exception as e:
        entry.delete(0, tk.END)
        entry.insert(0, "Error")
        messagebox.showerror("Evaluation Error", f"Could not evaluate expression.\nDetails: {e}")

def scientific(func):
    """Handle calculator scientific mode buttons like sin, cos, tan, log, and sqrt."""
    try:
        expr = normalize_expression(entry.get())
        resolved_value = eval(expr, SAFE_GLOBALS, SAFE_MATH_ENV)
        value = float(resolved_value)

        entry.delete(0, tk.END)
        if func == "sqrt":
            entry.insert(0, math.sqrt(value))
        elif func == "log":
            base_input = simpledialog.askstring("Log Base", "Enter base (e.g., 2, 10, or 'e'). Leave blank for 10:", parent=root)
            if base_input is None:
                entry.insert(0, str(value))
                return
            base_input = base_input.strip().lower()
            base = 10.0 if base_input == "" else (math.e if base_input == "e" else float(base_input))
            entry.insert(0, math.log(value, base))
        elif func == "sin":
            entry.insert(0, math.sin(math.radians(value)))
        elif func == "cos":
            entry.insert(0, math.cos(math.radians(value)))
        elif func == "tan":
            entry.insert(0, math.tan(math.radians(value)))
        elif func == "sin⁻¹":
            entry.insert(0, math.degrees(math.asin(value)))
        elif func == "cos⁻¹":
            entry.insert(0, math.degrees(math.acos(value)))
        elif func == "tan⁻¹":
            entry.insert(0, math.degrees(math.atan(value)))
        elif func == "abs":
            entry.insert(0, abs(value))
    except Exception as e:
        entry.delete(0, tk.END)
        entry.insert(0, "Error")
        messagebox.showerror("Evaluation Error", f"Could not perform operation.\nDetails: {e}")

def plot_and_find_roots():
    """Plot an algebraic expression containing 'x' and highlight real roots."""
    raw_expr = entry.get()
    normalized_raw = normalize_expression(raw_expr)
    if not re.search(r'\bx\b', normalized_raw):
        messagebox.showwarning("Input Error", "Please include the variable 'x' in your algebraic expression to plot.")
        return

    # Normalize UI inverse-trig input to NumPy function names for plotting.
    expr = normalized_raw
    expr = expr.replace('sin⁻¹', 'asin').replace('cos⁻¹', 'acos').replace('tan⁻¹', 'atan')

    eval_env = dict(PLOT_ENV)
    try:
        x_vals = np.linspace(-10, 10, 2000)
        eval_env['x'] = x_vals

        y_vals = eval(expr, SafPlotGlob, eval_env)

        # Filter finite (real) values
        valid = np.isfinite(y_vals)

        roots = []
        for i in range(len(x_vals) - 1):
            if valid[i] and valid[i+1]:
                p1, p2 = y_vals[i], y_vals[i+1]
                if p1 * p2 < 0:
                    root_approx = x_vals[i] - p1 * (x_vals[i+1] - x_vals[i]) / (p2 - p1)
                    roots.append(round(root_approx, 3))
                elif p1 == 0:
                    if not roots or abs(roots[-1] - x_vals[i]) > 0.05:
                        roots.append(round(x_vals[i], 3))
        if valid[-1] and y_vals[-1] == 0:
            if not roots or abs(roots[-1] - x_vals[-1]) > 0.05:
                roots.append(round(x_vals[-1], 3))

        if roots:
            messagebox.showinfo("Real Roots Found", f"Real roots found in range [-10, 10]:\nx = {', '.join(map(str, roots))}")
        else:
            messagebox.showinfo("Real Roots Found", "No real roots detected within the range [-10, 10].")

        new_window = messagebox.askyesno(
            "Plot Window",
            "Open the graph in a new window?\nChoose No to reuse the current plot window."
        )
        if new_window:
            plt.figure()
        else:
            plt.figure("Graph View")
            plt.clf()

        plt.plot(x_vals, y_vals, label=f"y = {raw_expr}", color='#1f77b4', lw=2)
        plt.axhline(0, color='black', linewidth=1, linestyle='--')
        plt.axvline(0, color='black', linewidth=1, linestyle='--')

        for r in roots:
            plt.plot(r, 0, 'ro')
            plt.text(r, 0.4, f"({r}, 0)", color='red', weight='bold', fontsize=9, ha='center')

        plt.title(f"Graph of y = {raw_expr}")
        plt.xlabel("X Axis")
        plt.ylabel("Y Axis")
        plt.grid(True, which='both', linestyle=':', alpha=0.6)
        plt.legend()
        plt.xlim(-10, 10)

        valid_y = y_vals[valid]
        if len(valid_y) > 0:
            p05, p95 = np.percentile(valid_y, [5, 95])
            mar = (p95 - p05) * 0.1 if p95 != p05 else 1.0
            plt.ylim(max(p05 - mar, -20), min(p95 + mar, 20))

        plt.show()

    except Exception as e:
        messagebox.showerror("Math/Syntax Error", f"Could not evaluate expression.\nCheck for missing signs (e.g. use '2*x' instead of '2x').\n\nDetails: {e}")

# Buttons
buttons = [
    '7', '8', '9', '/', 'sqrt',
    '4', '5', '6', '*', 'log',
    '1', '2', '3', '-', 'sin',
    '0', '.', '=', '+', 'cos',
    'C', '⌫', '(', ')', 'tan',
    '^', 'π', 'e', 'abs', '%',
    'x', 'sin⁻¹', 'cos⁻¹', 'tan⁻¹', 'Graph'
]

row_val = 1
col_val = 0

for button in buttons:
    if button == "=":
        act= calculate
    elif button == "C":
        act = clear
    elif button == "⌫":
        act= backspace
    elif button in ["sqrt", "log", "sin", "cos", "tan", "sin⁻¹", "cos⁻¹", "tan⁻¹", "abs"]:
        act= lambda x=button: scientific(x)
    elif button == "Graph":
        act= plot_and_find_roots
    elif button== "π":
        act= lambda: click('pi')
    elif button == "e":
        act= lambda: click('e')
    else:
        act= lambda x=button: click(x)

    b = tk.Button(root, text=button, width=5, height=2, font=("Arial", 16), command=act)
    b.grid(row=row_val, column=col_val)
    
    col_val += 1
    if col_val > 4:
        col_val = 0
        row_val += 1

root.mainloop()
