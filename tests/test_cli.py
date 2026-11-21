"""命令行行为测试。"""

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from constellation.cli import main


def run(args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(args)
    return code, out.getvalue(), err.getvalue()


class CliTest(unittest.TestCase):
    def test_help(self):
        with self.assertRaises(SystemExit) as ctx:
            main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_list(self):
        code, out, _ = run(["list"])
        self.assertEqual(code, 0)
        self.assertEqual(len(out.strip().splitlines()), 5)
        self.assertIn("北斗七星", out)

    def test_info(self):
        code, out, _ = run(["info", "北斗七星"])
        self.assertEqual(code, 0)
        self.assertIn("Big Dipper", out)
        self.assertIn("星数：7", out)
        self.assertIn("天枢", out)

    def test_info_unknown(self):
        code, _, err = run(["info", "猎户"])
        self.assertEqual(code, 2)
        self.assertIn("未知星座", err)

    def test_chart_stdout(self):
        code, out, _ = run(["chart", "猎户座"])
        self.assertEqual(code, 0)
        self.assertIn("<svg", out)
        self.assertIn("参宿四", out)

    def test_chart_size(self):
        code, out, _ = run(["chart", "猎户座", "--size", "400"])
        self.assertEqual(code, 0)
        self.assertIn('viewBox="0 0 400 400"', out)

    def test_chart_bad_size(self):
        code, _, err = run(["chart", "猎户座", "--size", "10"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_chart_to_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "chart.svg"
            code, out, _ = run(["chart", "猎户座", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())
            self.assertIn("已写入", out)

    def test_poster_stdout(self):
        code, out, _ = run(["poster"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count("<figure>"), 5)

    def test_poster_to_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "poster.html"
            code, _, _ = run(["poster", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())

    def test_sheet_stdout(self):
        code, out, _ = run(["sheet", "--count", "3", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count('class="card"'), 3)

    def test_sheet_answers(self):
        code, out, _ = run(["sheet", "--count", "3", "--seed", "2", "--answers"])
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)

    def test_sheet_single_kind(self):
        code, out, _ = run(["sheet", "--count", "5", "--kinds", "season", "--seed", "3"])
        self.assertEqual(code, 0)
        self.assertIn("季节", out)

    def test_sheet_bad_kind(self):
        code, _, err = run(["sheet", "--kinds", "guess"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_sheet_empty_kinds(self):
        code, _, err = run(["sheet", "--kinds", " , "])
        self.assertEqual(code, 2)
        self.assertIn("题型", err)

    def test_sheet_too_many(self):
        code, _, err = run(["sheet", "--count", "9999"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_sheet_to_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "sheet.html"
            code, _, _ = run(["sheet", "--count", "4", "--seed", "5", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertEqual(target.read_text(encoding="utf-8").count('class="card"'), 4)

    def test_nested_output(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "a" / "poster.html"
            code, _, _ = run(["poster", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())


if __name__ == "__main__":
    unittest.main()
