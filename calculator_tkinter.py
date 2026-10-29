import re
import tkinter as tk

from engine import CalculatorEngine, CalculatorError

PI = "\u03c0"

FG_COLORS = {
    "#000000": "#FFFFFF",
    "#DC1212": "#FFFFFF",
}
ACTIVE_BG = {
    "#000000": "#171B17",
    "#DC1212": "#E93939",
    "#858282": "#8F8C8C",
}
ACTIVE_FG = {
    "#DC1212": "#FFFFFF",
    "#000000": "#FFFFFF",
}
MODE_ACTIVE_BG = "#1B6B2C"
MODE_INACTIVE_BG = "#000000"


class CalculatorApp:
    def __init__(self, window: tk.Tk) -> None:
        self.window = window
        self.engine = CalculatorEngine()
        self.mode_buttons: dict[str, tk.Button] = {}

        self._configure_window()
        self._build_display()
        self._build_buttons()
        self._bind_keys()
        self._refresh_mode_buttons()

    def _configure_window(self) -> None:
        self.window.title("Scientific Calculator")
        self.window.geometry("500x760")
        self.window.resizable(width=False, height=False)
        self.window.configure(background="#B3AEAE")
        for col in range(6):
            self.window.columnconfigure(col, weight=1)
        for row in range(1, 11):
            self.window.rowconfigure(row, weight=1)

    def _build_display(self) -> None:
        self.result_label = tk.Label(
            master=self.window,
            font=("sans-serif", 14, "bold"),
            height=3,
            background="#B3AEAE",
            wraplength=480,
        )
        self.result_label.grid(row=0, column=0, columnspan=6, pady=(5, 5))

        self.result_entry = tk.Entry(
            master=self.window,
            font=("sans-serif", 20, "bold"),
            border=5,
            justify="right",
        )
        self.result_entry.grid(row=1, column=0, columnspan=6, pady=(5, 10), sticky="ew")
        self.result_entry.focus_set()

    def _build_buttons(self) -> None:
        buttons_features = [
            {"text": "sin", "bg": "#000000", "command": lambda: self.insert_function("sin")},
            {"text": "cos", "bg": "#000000", "command": lambda: self.insert_function("cos")},
            {"text": "tan", "bg": "#000000", "command": lambda: self.insert_function("tan")},
            {"text": "lg10", "bg": "#000000", "command": lambda: self.insert_function("log10")},
            {"text": "ln", "bg": "#000000", "command": lambda: self.insert_function("ln")},
            {"text": "lg2", "bg": "#000000", "command": lambda: self.insert_function("log2")},
            {"text": "sinh", "bg": "#000000", "command": lambda: self.insert_function("sinh")},
            {"text": "cosh", "bg": "#000000", "command": lambda: self.insert_function("cosh")},
            {"text": "tanh", "bg": "#000000", "command": lambda: self.insert_function("tanh")},
            {"text": "x!", "bg": "#000000", "command": self.insert_factorial},
            {"text": "1/x", "bg": "#000000", "command": self.insert_reciprocal},
            {"text": "√", "bg": "#000000", "command": lambda: self.insert_function("√")},
            {"text": "Exp", "bg": "#000000", "command": lambda: self.insert_function("exp")},
            {"text": "Deg", "bg": "#000000", "command": lambda: self.set_angle_mode("DEG")},
            {"text": "Rad", "bg": "#000000", "command": lambda: self.set_angle_mode("RAD")},
            {"text": "2^", "bg": "#000000", "command": lambda: self.insert_prefix("2^(")},
            {"text": "10^", "bg": "#000000", "command": lambda: self.insert_prefix("10^(")},
            {"text": "e^", "bg": "#000000", "command": lambda: self.insert_prefix("e^(")},
            {"text": "(", "bg": "#000000", "command": lambda: self.insert_prefix("(")},
            {"text": ")", "bg": "#000000", "command": lambda: self._insert(")")},
            {"text": "|x|", "bg": "#000000", "command": lambda: self.insert_function("abs")},
            {"text": "x²", "bg": "#000000", "command": lambda: self.wrap_power(2)},
            {"text": "x³", "bg": "#000000", "command": lambda: self.wrap_power(3)},
            {"text": "x^y", "bg": "#000000", "command": lambda: self.insert_operator("^")},
            {"text": PI, "bg": "#000000", "command": lambda: self.insert_constant(PI)},
            {"text": "7", "command": lambda: self.insert_digit("7")},
            {"text": "8", "command": lambda: self.insert_digit("8")},
            {"text": "9", "command": lambda: self.insert_digit("9")},
            {"text": "%", "bg": "#858282", "command": self.insert_percent},
            {"text": "^", "bg": "#858282", "command": lambda: self.insert_operator("^")},
            {"text": "e", "bg": "#000000", "command": lambda: self.insert_constant("e")},
            {"text": "4", "command": lambda: self.insert_digit("4")},
            {"text": "5", "command": lambda: self.insert_digit("5")},
            {"text": "6", "command": lambda: self.insert_digit("6")},
            {"text": "×", "bg": "#858282", "command": lambda: self.insert_operator("×")},
            {"text": "÷", "bg": "#858282", "command": lambda: self.insert_operator("÷")},
            {"text": "AC", "bg": "#DC1212", "command": self.all_clear},
            {"text": "1", "command": lambda: self.insert_digit("1")},
            {"text": "2", "command": lambda: self.insert_digit("2")},
            {"text": "3", "command": lambda: self.insert_digit("3")},
            {"text": "+", "bg": "#858282", "command": lambda: self.insert_operator("+")},
            {"text": "-", "bg": "#858282", "command": lambda: self.insert_operator("-")},
            {"text": "CE", "bg": "#DC1212", "command": self.clear_entry},
            {"text": "+/-", "command": self.toggle_sign},
            {"text": "0", "command": lambda: self.insert_digit("0")},
            {"text": ".", "command": self.insert_dot},
            {"text": "=", "bg": "#858282", "command": self.equals},
        ]

        calc_buttons: list[tk.Button] = []
        plus_button = None
        equal_button = None
        skip_indexes: list[int] = []

        for key_object in buttons_features:
            bg_color = key_object.get("bg")
            button = tk.Button(
                master=self.window,
                text=key_object["text"],
                bg=bg_color,
                fg=FG_COLORS.get(bg_color, "#000000"),
                font=("DejaVu Sans", 18),
                relief="raised",
                bd=5,
                activebackground=ACTIVE_BG.get(bg_color, "#c0c0c0"),
                activeforeground=ACTIVE_FG.get(bg_color, "#000000"),
                padx=15,
                pady=15,
                highlightthickness=0,
                borderwidth=2,
                cursor="hand2",
                command=key_object["command"],
            )
            calc_buttons.append(button)
            if key_object["text"] == "Deg":
                self.mode_buttons["DEG"] = button
            elif key_object["text"] == "Rad":
                self.mode_buttons["RAD"] = button

        for index, button in enumerate(calc_buttons):
            if button["text"] == "+":
                plus_button = button
                skip_indexes.append(index)
            elif button["text"] == "=":
                equal_button = button
                skip_indexes.append(index)

        cols = 6
        for index, button in enumerate(calc_buttons):
            if index in skip_indexes:
                continue
            row = index // cols + 2
            col = index % cols
            button.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)

        plus_button.grid(row=8, column=4, rowspan=2, sticky="nsew", padx=5, pady=5)
        equal_button.grid(row=9, column=5, sticky="nsew", padx=5, pady=5)

    def _bind_keys(self) -> None:
        for sequence in ("<Return>", "<KP_Enter>"):
            self.window.bind(sequence, self._on_equals_key)
            self.result_entry.bind(sequence, self._on_equals_key)
        self.window.bind("<Escape>", lambda _event: self.all_clear())
        self.result_entry.bind("<Key>", self._on_entry_key)

    def _on_equals_key(self, _event: tk.Event) -> str:
        self.equals()
        return "break"

    def _on_entry_key(self, event: tk.Event) -> str | None:
        replacements = {"*": "×", "/": "÷"}
        if event.char in replacements:
            self.insert_operator(replacements[event.char])
            return "break"
        if event.char == "%":
            self.insert_percent()
            return "break"
        return None

    def _current(self) -> str:
        return self.result_entry.get()

    def _set_entry(self, text: str) -> None:
        self.result_entry.delete(0, tk.END)
        self.result_entry.insert(0, text)

    def _insert(self, token: str) -> None:
        self.result_entry.insert(tk.END, token)

    def _needs_implicit_multiply(self, text: str) -> bool:
        if not text:
            return False
        last = text[-1]
        return last.isdigit() or last in f").!%{PI}e"

    def insert_function(self, name: str) -> None:
        token = f"{name}("
        if self._needs_implicit_multiply(self._current()):
            token = f"×{token}"
        self._insert(token)

    def insert_prefix(self, token: str) -> None:
        if self._needs_implicit_multiply(self._current()):
            token = f"×{token}"
        self._insert(token)

    def insert_constant(self, token: str) -> None:
        if self._needs_implicit_multiply(self._current()):
            token = f"×{token}"
        self._insert(token)

    def insert_digit(self, digit: str) -> None:
        text = self._current()
        if text.endswith(PI) or re.search(r"(?<![A-Za-z])e$", text):
            self._insert(f"×{digit}")
            return
        self._insert(digit)

    def insert_operator(self, operator: str) -> None:
        text = self._current()
        if not text:
            if operator == "-":
                self._insert("-")
            return
        if text[-1] in "+-×÷^":
            if operator == "-" and text[-1] in "+×÷^":
                self._insert("-")
                return
            self._set_entry(text[:-1] + operator)
            return
        self._insert(operator)

    def insert_dot(self) -> None:
        text = self._current()
        if not text or text[-1] in "+-×÷^(":
            self._insert("0.")
            return
        last_number = re.split(r"[+\-×÷^()%]", text)[-1]
        if "." in last_number:
            return
        self._insert(".")

    def insert_percent(self) -> None:
        text = self._current()
        if not text or text[-1] in "+-×÷^(%":
            return
        self._insert("%")

    def insert_factorial(self) -> None:
        text = self._current()
        if not text or text[-1] in "+-×÷^(!":
            return
        self._insert("!")

    def insert_reciprocal(self) -> None:
        text = self._current()
        if not text:
            self._insert("1/")
            return
        self._set_entry(f"1/({text})")

    def wrap_power(self, power: int) -> None:
        text = self._current()
        if not text:
            return
        if text[-1] in "+-×÷^(":
            return
        self._set_entry(f"({text})^({power})")

    def toggle_sign(self) -> None:
        text = self._current()
        if not text:
            self._insert("(-")
            return
        if text.startswith("-(") and text.endswith(")") and self._balanced(text):
            self._set_entry(text[2:-1])
            return
        self._set_entry(f"-({text})")

    def _balanced(self, text: str) -> bool:
        depth = 0
        for char in text:
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth < 0:
                    return False
        return depth == 0

    def clear_entry(self) -> None:
        self._set_entry("")

    def all_clear(self) -> None:
        self._set_entry("")
        self.result_label["text"] = ""

    def backspace(self) -> None:
        current = self._current()
        if current:
            self._set_entry(current[:-1])

    def set_angle_mode(self, mode: str) -> None:
        self.engine.set_angle_mode(mode)
        self._refresh_mode_buttons()
        self.result_label["text"] = f"Mode: {mode}"

    def _refresh_mode_buttons(self) -> None:
        for mode, button in self.mode_buttons.items():
            if mode == self.engine.angle_mode:
                button.configure(bg=MODE_ACTIVE_BG, fg="#FFFFFF")
            else:
                button.configure(bg=MODE_INACTIVE_BG, fg="#FFFFFF")

    def equals(self) -> None:
        expression = self._current().strip()
        try:
            result = self.engine.evaluate(expression)
        except CalculatorError as exc:
            self.result_label["text"] = str(exc)
            return
        self.result_label["text"] = f"{expression} = {result}"
        self._set_entry(result)


def main() -> None:
    window = tk.Tk()
    CalculatorApp(window)
    window.mainloop()


if __name__ == "__main__":
    main()
