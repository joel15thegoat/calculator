"""Scientific Calculator & Grapher."""

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
        r'(\d)(?=\s*(?:x\b|pi\b|e\b(?![+\-]?\d)|sin\b|cos\b|tan\b|asin\b|acos\b|atan\b|log\b|ln\b|sqrt\b|abs\b|\())',
        r'\1*',
        expr,
    )
    expr = re.sub(
        r'((?:x|pi|e)\b|(?<![\d.])e(?=\d)|\))\s*(?=(?:\d|x\b|pi\b|(?:e\b(?![+\-]?\d))|sin\b|cos\b|tan\b|asin\b|acos\b|atan\b|log\b|ln\b|sqrt\b|abs\b|\())',
        r'\1*',
        expr,
    )
    return expr

def format_result(value):
    """Format numeric calculator results to reduce floating-point noise."""
    if isinstance(value, float):
        if math.isfinite(value):
            rounded = round(value, 12)
            formatted = format(rounded, '.12g')
            if '.' in formatted:
                formatted = formatted.rstrip('0').rstrip('.')
            return formatted
        return str(value)
    return str(value)

def has_invalid_scientific_notation(expr):
    """Return True when the expression contains malformed scientific notation."""
    # Catch incomplete exponent notation like e+ or e- with no digits.
    if re.search(r'e[+\-](?!\d)', expr, re.IGNORECASE):
        return True
    # Catch invalid exponent formats such as 1ee3, 1e3e4, or 1e3.4.
    if re.search(r'\d+(?:\.\d*)?e[+\-]?(?!\d)', expr, re.IGNORECASE):
        return True
    if re.search(r'\d+(?:\.\d*)?e[+\-]?\d+(?=[A-Za-z_\.])', expr, re.IGNORECASE):
        return True
    return False


def append_power(power):
    """Append a power operator to the calculator input."""
    click(f'^{power}')

def insert_sqrt_3():
    """Insert the square root of 3 into the calculator input."""
    click('sqrt(3)')

def insert_sqrt_value():
    """Prompt the user for a root degree and value, then insert the root expression."""
    degree = simpledialog.askinteger(
        "Root Degree",
        "Enter the root degree (e.g. 2 for square root, 5 for fifth root):",
        parent=root,
        minvalue=2,
    )
    if degree is None:
        return
    value = simpledialog.askstring("Root Value", "Enter a value to take the root of:", parent=root)
    if value is None or value.strip() == "":
        return
    entry.insert(tk.END, f'pow({value.strip()}, 1/{degree})')

def simplify_square_root(n):
    """Return a simplified surd string for integer n or None if not possible."""
    if n < 0 or int(n) != n:
        return None
    n = int(n)
    outside = 1
    inside = n
    p = 2
    while p * p <= inside:
        while inside % (p * p) == 0:
            inside //= p * p
            outside *= p
        p += 1
    if inside == 1:
        return str(outside)
    if outside == 1:
        return f'sqrt({inside})'
    return f'{outside}*sqrt({inside})'

def surd_form():
    """Convert the current expression to a surd form string if possible."""
    expr = normalize_expression(entry.get()).strip()
    if not expr:
        messagebox.showwarning("Surd Not Possible", "Enter an expression before attempting surd conversion.")
        return
    if re.search(r'\bx\b', expr):
        messagebox.showwarning("Surd Not Possible", "Cannot convert expressions with 'x' into surd form.")
        return
    if expr.count('(') != expr.count(')'):
        messagebox.showwarning("Surd Not Possible", "Parentheses are not balanced.")
        return
    try:
        if has_invalid_scientific_notation(expr):
            messagebox.showwarning("Surd Not Possible", "Malformed scientific notation detected. Check any 'e' exponent usage.")
            return
        result = eval(expr, SAFE_GLOBALS, SAFE_MATH_ENV)
    except Exception:
        messagebox.showwarning("Surd Not Possible", "Could not evaluate the current expression.")
        return
    if isinstance(result, float) and not math.isfinite(result):
        messagebox.showwarning("Surd Not Possible", "Cannot convert this value into surd form.")
        return
    if isinstance(result, (int, float)):
        square_candidate = result * result
        nearest = round(square_candidate)
        if math.isclose(square_candidate, nearest, rel_tol=1e-12, abs_tol=1e-12) and nearest >= 0:
            surd = simplify_square_root(nearest)
            if surd is not None:
                entry.delete(0, tk.END)
                entry.insert(0, surd)
                return
    messagebox.showwarning("Surd Not Possible", "Cannot represent the current expression in surd form.")

def calculate():
    """Evaluate the current expression from the calculator display."""
    try:
        expr = normalize_expression(entry.get()).strip()
        if not expr:
            messagebox.showwarning("Input Error", "Enter an expression before pressing '='.")
            return
        if re.search(r'[+\-*/^%]$', expr) or expr.endswith('('):
            messagebox.showwarning("Input Error", "Complete the expression before pressing '='.")
            return
        if expr.count('(') != expr.count(')'):
            messagebox.showwarning("Input Error", "Parentheses are not balanced.")
            return
        if has_invalid_scientific_notation(expr):
            messagebox.showwarning("Input Error", "Malformed scientific notation detected. Check any 'e' exponent usage.")
            return
        # Detect standalone variable 'x' and prevent scalar evaluation.
        if re.search(r'\bx\b', expr):
            messagebox.showwarning("Input Error", "Please use the 'Graph' button to plot expressions containing 'x'.")
            return
        # Evaluate with a restricted math environment.
        result = eval(expr, SAFE_GLOBALS, SAFE_MATH_ENV)
        entry.delete(0, tk.END)
        entry.insert(0, format_result(result))
    except Exception as e:
        entry.delete(0, tk.END)
        entry.insert(0, "Error")
        messagebox.showerror("Evaluation Error", f"Could not evaluate expression.\nDetails: {e}")

def scientific(func):
    """Handle calculator scientific mode buttons like sin, cos, tan, log, and sqrt."""
    try:
        expr = normalize_expression(entry.get()).strip()
        if not expr:
            messagebox.showwarning("Input Error", "Enter a value before using a scientific function.")
            return
        if re.search(r'\bx\b', expr):
            messagebox.showwarning("Input Error", "Use the 'Graph' button for expressions containing 'x'.")
            return
        if re.search(r'[+\-*/^%]$', expr) or expr.endswith('('):
            messagebox.showwarning("Input Error", "Complete the expression before applying the scientific function.")
            return
        if expr.count('(') != expr.count(')'):
            messagebox.showwarning("Input Error", "Parentheses are not balanced.")
            return
        if has_invalid_scientific_notation(expr):
            messagebox.showwarning("Input Error", "Malformed scientific notation detected. Check any 'e' exponent usage.")
            return
        if re.fullmatch(r'(sin|cos|tan|log|ln|sqrt|abs|asin|acos|atan|pi|e)', expr):
            messagebox.showwarning("Input Error", "Enter a numeric value or expression before using this function.")
            return
        resolved_value = eval(expr, SAFE_GLOBALS, SAFE_MATH_ENV)
        value = float(resolved_value)

        entry.delete(0, tk.END)
        if func == "sqrt":
            entry.insert(0, format_result(math.sqrt(value)))
        elif func == "log":
            if value <= 0:
                messagebox.showwarning("Math Domain Error", "Logarithm input must be greater than zero.")
                return
            base_input = simpledialog.askstring("Log Base", "Enter base (e.g., 2, 10, or 'e'). Leave blank for 10:", parent=root)
            if base_input is None:
                entry.insert(0, str(value))
                return
            base_input = base_input.strip().lower()
            try:
                base = 10.0 if base_input == "" else (math.e if base_input == "e" else float(base_input))
            except ValueError:
                messagebox.showwarning("Input Error", "Invalid log base entered.")
                return
            if base <= 0 or base == 1:
                messagebox.showwarning("Math Domain Error", "Log base must be positive and not equal to 1.")
                return
            entry.insert(0, format_result(math.log(value, base)))
        elif func == "sin":
            entry.insert(0, format_result(math.sin(math.radians(value))))
        elif func == "cos":
            entry.insert(0, format_result(math.cos(math.radians(value))))
        elif func == "tan":
            entry.insert(0, format_result(math.tan(math.radians(value))))
        elif func == "sin⁻¹":
            if value < -1 or value > 1:
                messagebox.showwarning("Math Domain Error", "Input for arcsin must be between -1 and 1.")
                return
            entry.insert(0, format_result(math.degrees(math.asin(value))))
        elif func == "cos⁻¹":
            if value < -1 or value > 1:
                messagebox.showwarning("Math Domain Error", "Input for arccos must be between -1 and 1.")
                return
            entry.insert(0, format_result(math.degrees(math.acos(value))))
        elif func == "tan⁻¹":
            entry.insert(0, format_result(math.degrees(math.atan(value))))
        elif func == "abs":
            entry.insert(0, format_result(abs(value)))
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
            fig = plt.figure()
        else:
            fig = plt.figure("Graph View")
            fig.clf()

        ax = fig.add_subplot(111)
        line, = ax.plot(x_vals, y_vals, label=f"y = {raw_expr}", color='#1f77b4', lw=2, picker=8)
        ax.axhline(0, color='black', linewidth=1, linestyle='--')
        ax.axvline(0, color='black', linewidth=1, linestyle='--')

        for r in roots:
            ax.plot(r, 0, 'ro')
            ax.text(r, 0.4, f"({r}, 0)", color='red', weight='bold', fontsize=9, ha='center')

        ax.set_title(f"Graph of y = {raw_expr}")
        ax.set_xlabel("X Axis")
        ax.set_ylabel("Y Axis")
        ax.grid(True, which='both', linestyle=':', alpha=0.6)
        ax.legend()
        ax.set_xlim(-10, 10)

        valid_y = y_vals[valid]
        if len(valid_y) > 0:
            p05, p95 = np.percentile(valid_y, [5, 95])
            mar = (p95 - p05) * 0.1 if p95 != p05 else 1.0
            ax.set_ylim(max(p05 - mar, -20), min(p95 + mar, 20))

        annot = ax.annotate(
            "",
            xy=(0, 0),
            xytext=(15, 15),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w", alpha=0.9),
            arrowprops=dict(arrowstyle="->"),
        )
        annot.set_visible(False)

        def on_motion(event):
            if event.inaxes != ax:
                return
            contains, info = line.contains(event)
            if contains:
                x_data, y_data = line.get_data()
                ind = info["ind"][0]
                x_pt, y_pt = x_data[ind], y_data[ind]
                annot.xy = (x_pt, y_pt)
                annot.set_text(f"x={x_pt:.2f}\ny={y_pt:.2f}")
                annot.set_visible(True)
                line.set_linewidth(4)
                line.set_color('#d62728')
                fig.canvas.draw_idle()
            else:
                if annot.get_visible():
                    annot.set_visible(False)
                line.set_linewidth(2)
                line.set_color('#1f77b4')
                fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", on_motion)
        plt.show()

    except Exception as e:
        messagebox.showerror("Math/Syntax Error", f"Could not evaluate expression.\nCheck for missing signs.\n\nDetails: {e}")
buttons = [
    'C', '⌫', '(', ')', 'Graph', 'sqrt',
    '7', '8', '9', '/', 'log', '^2',
    '4', '5', '6', '*', '^3', 'root',
    '1', '2', '3', '-', 'tan', '√3',
    '0', '.', '=', '+', 'sin', 'cos',
    'π', 'e', 'abs', 'surd', 'x', 'sin⁻¹',
    'cos⁻¹', 'tan⁻¹'
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
    elif button == "^2":
        act= lambda: append_power(2)
    elif button == "^3":
        act= lambda: append_power(3)
    elif button == "√3":
        act= insert_sqrt_3
    elif button == "root":
        act= insert_sqrt_value
    elif button == "surd":
        act= surd_form
    elif button == "Graph":
        act= plot_and_find_roots
    elif button== "π":
        act= lambda: click('pi')
    elif button == "e":
        act= lambda: click('e')
    else:
        act= lambda x=button: click(x)

    b = tk.Button(root, text=button, width=4, height=2, font=("Arial", 16), command=act)
    b.grid(row=row_val, column=col_val)
    
    col_val += 1
    if col_val > 5:
        col_val = 0
        row_val += 1

root.mainloop()
