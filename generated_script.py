import ast
import operator
import os
import sys
from typing import Union, List, Tuple

class SafeCalculatorEngine:
    """Safe arithmetic evaluation engine using AST parsing."""

    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def evaluate(self, expression: str) -> Union[int, float, str]:
        sanitized = expression.replace("×", "*").replace("÷", "/").replace("^", "**")
        try:
            node = ast.parse(sanitized, mode="eval").body
            result = self._eval_node(node)
            if isinstance(result, float) and result.is_integer():
                return int(result)
            if isinstance(result, float):
                return round(result, 8)
            return result
        except ZeroDivisionError:
            return "Error: Div by 0"
        except Exception:
            return "Error"

    def _eval_node(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Invalid literal")
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op_type = type(node.op)
            if op_type in self.OPERATORS:
                return self.OPERATORS[op_type](left, right)
            raise ValueError(f"Unsupported binary operator: {op_type}")
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            op_type = type(node.op)
            if op_type in self.OPERATORS:
                return self.OPERATORS[op_type](operand)
            raise ValueError(f"Unsupported unary operator: {op_type}")
        else:
            raise ValueError("Unsupported expression element")


class InteractiveCalculator:
    """Stateful calculator model supporting interactive actions."""

    BUTTON_LAYOUT = [
        ["C", "DEL", "%", "/"],
        ["7", "8", "9", "*"],
        ["4", "5", "6", "-"],
        ["1", "2", "3", "+"],
        ["±", "0", ".", "="]
    ]

    def __init__(self):
        self.engine = SafeCalculatorEngine()
        self.expression = ""
        self.display_value = "0"
        self.history = []
        self.last_pressed = ""
        self.should_reset_display = False

    def press(self, key: str):
        self.last_pressed = key

        if key == "C":
            self.expression = ""
            self.display_value = "0"
            self.should_reset_display = False

        elif key == "DEL":
            if self.display_value not in ("0", "Error", "Error: Div by 0"):
                self.display_value = self.display_value[:-1] or "0"
                if self.expression:
                    self.expression = self.expression[:-1]

        elif key == "±":
            if self.display_value not in ("0", "Error", "Error: Div by 0"):
                if self.display_value.startswith("-"):
                    self.display_value = self.display_value[1:]
                else:
                    self.display_value = "-" + self.display_value

        elif key in ("+", "-", "*", "/", "%"):
            if self.display_value.startswith("Error"):
                return
            if self.expression and self.expression[-1] in "+-*/%":
                self.expression = self.expression[:-1] + key
            else:
                self.expression = (self.expression or self.display_value) + key
            self.should_reset_display = True

        elif key == "=":
            if not self.expression and self.display_value:
                return
            eval_target = self.expression or self.display_value
            result = self.engine.evaluate(eval_target)
            self.history.append((eval_target, str(result)))
            if len(self.history) > 3:
                self.history.pop(0)
            self.display_value = str(result)
            self.expression = ""
            self.should_reset_display = True

        else:
            if self.should_reset_display or self.display_value == "0":
                self.display_value = key
                self.should_reset_display = False
            else:
                self.display_value += key
            self.expression += key

    def render_tui(self) -> str:
        w = 32
        lines = []
        lines.append("┌" + "─" * w + "┐")
        title = " CALC-PRO // INTERACTIVE "
        lines.append(f"│{title:^{w}}│")
        lines.append("├" + "─" * w + "┤")

        # History display
        if self.history:
            last_expr, last_res = self.history[-1]
            hist_str = f"{last_expr} = {last_res}"
            if len(hist_str) > w - 4:
                hist_str = "..." + hist_str[-(w - 7):]
            lines.append(f"│  {hist_str:<{w-4}}  │")
        else:
            lines.append(f"│  {'Ready':<{w-4}}  │")

        # Main LCD screen
        expr_preview = self.expression if self.expression else ""
        if len(expr_preview) > w - 4:
            expr_preview = "..." + expr_preview[-(w - 7):]
        lines.append(f"│  {expr_preview:>{w-4}}  │")

        disp = self.display_value
        if len(disp) > w - 4:
            disp = disp[:w - 4]
        lines.append(f"│  {disp:>{w-4}}  │")
        lines.append("├" + "─" * w + "┤")

        # Interactive Button Grid
        for row in self.BUTTON_LAYOUT:
            row_tokens = []
            for btn in row:
                if btn == self.last_pressed:
                    token = f"▶{btn}◀"
                else:
                    token = f"[{btn}]"
                row_tokens.append(f"{token:^7}")
            row_str = "".join(row_tokens)
            lines.append(f"│ {row_str:<{w-2}} │")

        lines.append("└" + "─" * w + "┘")
        return "\n".join(lines)


def export_interactive_html(filename: str = "interactive_calculator.html"):
    """Generates a standalone, responsive, modern glassmorphic web calculator."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Interactive Modern Calculator</title>
<style>
  :root {
    --bg-grad-1: #0f172a;
    --bg-grad-2: #1e293b;
    --card-bg: rgba(30, 41, 59, 0.7);
    --card-border: rgba(255, 255, 255, 0.1);
    --btn-bg: rgba(255, 255, 255, 0.05);
    --btn-hover: rgba(255, 255, 255, 0.15);
    --accent: #38bdf8;
    --accent-hover: #0284c7;
    --op-color: #f59e0b;
    --danger: #ef4444;
    --text: #f8fafc;
    --text-muted: #94a3b8;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
  body {
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    background: radial-gradient(circle at top right, var(--bg-grad-2), var(--bg-grad-1));
    color: var(--text);
  }
  .calculator-card {
    width: 360px;
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    backdrop-filter: blur(20px);
    border-radius: 28px;
    padding: 24px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  }
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }
  .logo { font-size: 0.85rem; letter-spacing: 2px; text-transform: uppercase; color: var(--accent); font-weight: 700; }
  .history-badge { font-size: 0.75rem; color: var(--text-muted); }
  .screen {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid var(--card-border);
    border-radius: 18px;
    padding: 16px 20px;
    margin-bottom: 24px;
    text-align: right;
    min-height: 96px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  .screen-history { font-size: 0.9rem; color: var(--text-muted); min-height: 1.2rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .screen-main { font-size: 2.2rem; font-weight: 600; overflow-x: auto; scrollbar-width: none; }
  .keypad {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
  }
  button {
    height: 60px;
    border-radius: 16px;
    border: 1px solid var(--card-border);
    background: var(--btn-bg);
    color: var(--text);
    font-size: 1.25rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease-out;
  }
  button:hover { background: var(--btn-hover); transform: translateY(-2px); }
  button:active { transform: scale(0.95); }
  button.op { color: var(--op-color); }
  button.danger { color: var(--danger); }
  button.equals {
    grid-column: span 2;
    background: var(--accent);
    color: #0f172a;
    font-weight: 700;
    border: none;
  }
  button.equals:hover { background: var(--accent-hover); color: #fff; }
</style>
</head>
<body>
<div class="calculator-card">
  <div class="header">
    <div class="logo">Interactive Calc</div>
    <div class="history-badge" id="history">Ready</div>
  </div>
  <div class="screen">
    <div class="screen-history" id="subDisplay"></div>
    <div class="screen-main" id="mainDisplay">0</div>
  </div>
  <div class="keypad">
    <button class="danger" onclick="handleKey('C')">C</button>
    <button onclick="handleKey('DEL')">⌫</button>
    <button class="op" onclick="handleKey('%')">%</button>
    <button class="op" onclick="handleKey('/')">÷</button>

    <button onclick="handleKey('7')">7</button>
    <button onclick="handleKey('8')">8</button>
    <button onclick="handleKey('9')">9</button>
    <button class="op" onclick="handleKey('*')">×</button>

    <button onclick="handleKey('4')">4</button>
    <button onclick="handleKey('5')">5</button>
    <button onclick="handleKey('6')">6</button>
    <button class="op" onclick="handleKey('-')">−</button>

    <button onclick="handleKey('1')">1</button>
    <button onclick="handleKey('2')">2</button>
    <button onclick="handleKey('3')">3</button>
    <button class="op" onclick="handleKey('+')">+</button>

    <button onclick="handleKey('0')">0</button>
    <button onclick="handleKey('.')">.</button>
    <button class="equals" onclick="handleKey('=')">=</button>
  </div>
</div>
<script>
  let expr = '';
  let display = '0';
  let shouldReset = false;

  function update() {
    document.getElementById('mainDisplay').textContent = display;
    document.getElementById('subDisplay').textContent = expr;
  }

  function handleKey(k) {
    if (k === 'C') {
      expr = '';
      display = '0';
      shouldReset = false;
    } else if (k === 'DEL') {
      display = display.length > 1 ? display.slice(0, -1) : '0';
      expr = expr.slice(0, -1);
    } else if (['+', '-', '*', '/', '%'].includes(k)) {
      if (['+', '-', '*', '/', '%'].includes(expr.slice(-1))) {
        expr = expr.slice(0, -1) + k;
      } else {
        expr = (expr || display) + k;
      }
      shouldReset = true;
    } else if (k === '=') {
      try {
        const clean = (expr || display).replace(/×/g, '*').replace(/÷/g, '/');
        const res = Function(`'use strict'; return (${clean})`)();
        document.getElementById('history').textContent = `${clean} = ${res}`;
        display = Number.isFinite(res) ? String(res) : 'Error';
        expr = '';
        shouldReset = true;
      } catch {
        display = 'Error';
      }
    } else {
      if (shouldReset || display === '0') {
        display = k;
        shouldReset = false;
      } else {
        display += k;
      }
      expr += k;
    }
    update();
  }

  window.addEventListener('keydown', (e) => {
    if (/[0-9]/.test(e.key)) handleKey(e.key);
    if (['+', '-', '*', '/'].includes(e.key)) handleKey(e.key);
    if (e.key === 'Enter' || e.key === '=') handleKey('=');
    if (e.key === 'Backspace') handleKey('DEL');
    if (e.key === 'Escape') handleKey('C');
  });
</script>
</body>
</html>
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    return filename


def run_interactive_simulation():
    """Runs a complete test and visual demonstration of interactive steps."""
    calc = InteractiveCalculator()

    scenarios = [
        ("Multi-digit arithmetic: 125 + 75 =", ["1", "2", "5", "+", "7", "5", "="]),
        ("Sequential multiplication: * 4 =", ["*", "4", "="]),
        ("Decimal calculation: 50.5 - 20.25 =", ["C", "5", "0", ".", "5", "-", "2", "0", ".", "2", "5", "="]),
        ("Zero division protection: 99 / 0 =", ["C", "9", "9", "/", "0", "="]),
        ("Backspace correction: 124 -> DEL -> 5 + 10 =", ["C", "1", "2", "4", "DEL", "5", "+", "1", "0", "="])
    ]

    print("=" * 60)
    print("   CALCULATOR: INTERACTIVE TERMINAL & ENGINE DEMONSTRATION")
    print("=" * 60 + "\n")

    for title, key_sequence in scenarios:
        print(f"▶ SCENARIO: {title}")
        print(f"  Key sequence: {' '.join(key_sequence)}")
        for key in key_sequence:
            calc.press(key)
        print(calc.render_tui())
        print()

    # Generate the modern interactive HTML calculator file
    exported_file = export_interactive_html("interactive_calculator.html")
    print(f"✔ Interactive HTML Application successfully generated at: '{exported_file}'")
    print("  You can open this file in any web browser to use the graphical interactive calculator.")


if __name__ == "__main__":
    run_interactive_simulation()