import unittest

from engine import CalculatorEngine, CalculatorError

class CalculatorEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = CalculatorEngine()

    def eval_eq(self, expression: str, expected: str) -> None:
        self.assertEqual(self.engine.evaluate(expression), expected)

    def test_precedence(self) -> None:
        self.eval_eq("1+2×3", "7")
        self.eval_eq("(1+2)×3", "9")

    def test_power_and_division(self) -> None:
        self.eval_eq("2^3", "8")
        self.eval_eq("9÷3", "3")

    def test_trig_degrees(self) -> None:
        self.engine.set_angle_mode("DEG")
        self.eval_eq("sin(30)", "0.5")
        self.eval_eq("cos(60)", "0.5")

    def test_trig_radians(self) -> None:
        self.engine.set_angle_mode("RAD")
        self.eval_eq("sin(π÷2)", "1")

    def test_logs_and_constants(self) -> None:
        self.eval_eq("log10(100)", "2")
        self.eval_eq("log2(8)", "3")
        self.eval_eq("ln(e)", "1")

    def test_sqrt_factorial_percent_abs(self) -> None:
        self.eval_eq("√(16)", "4")
        self.eval_eq("5!", "120")
        self.eval_eq("(2+3)!", "120")
        self.eval_eq("50%", "0.5")
        self.eval_eq("10+50%", "10.5")
        self.eval_eq("abs(-12)", "12")

    def test_implicit_multiplication(self) -> None:
        self.eval_eq("2π", "6.28318530718")
        self.eval_eq("2(3+4)", "14")

    def test_errors(self) -> None:
        with self.assertRaises(CalculatorError):
            self.engine.evaluate("1÷0")
        with self.assertRaises(CalculatorError):
            self.engine.evaluate("√(-1)")
        with self.assertRaises(CalculatorError):
            self.engine.evaluate("")
        with self.assertRaises(CalculatorError):
            self.engine.evaluate("sin(30")
        self.engine.set_angle_mode("DEG")
        with self.assertRaises(CalculatorError):
            self.engine.evaluate("tan(90)")

    def test_rejects_python_injection(self) -> None:
        with self.assertRaises(CalculatorError):
            self.engine.evaluate("__import__('os').system('echo pwned')")

    def test_format_result_small_integer(self) -> None:
        self.assertEqual(self.engine.format_result(1024), "1024")

    def test_format_result_large_integer(self) -> None:
        self.assertEqual(
            self.engine.format_result(2**1000),
            "1.071508607186e+301",
        )

    def test_format_result_negative_large_integer(self) -> None:
        self.assertEqual(
            self.engine.format_result(-(2**1000)),
            "-1.071508607186e+301",
        )
if __name__ == "__main__":
    unittest.main()
