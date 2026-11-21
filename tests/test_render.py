"""星座渲染测试。"""

import unittest

from constellation.model import (
    CONSTELLATIONS,
    ConstellationError,
    ConstellationProblem,
    generate_problems,
)
from constellation.render import render_chart, render_poster, render_worksheet


class ChartTest(unittest.TestCase):
    def test_svg(self):
        svg = render_chart("北斗七星")
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.endswith("</svg>"))
        self.assertIn('viewBox="0 0 320 320"', svg)

    def test_all_stars(self):
        svg = render_chart("北斗七星")
        for name in ("天枢", "天璇", "天玑", "天权", "玉衡", "开阳", "摇光"):
            self.assertIn(name, svg)

    def test_edges(self):
        svg = render_chart("北斗七星")
        self.assertEqual(svg.count("<line"), 6)

    def test_custom_size(self):
        svg = render_chart("猎户座", 400)
        self.assertIn('viewBox="0 0 400 400"', svg)

    def test_size_too_small(self):
        with self.assertRaises(ConstellationError):
            render_chart("猎户座", 100)

    def test_size_bool(self):
        with self.assertRaises(ConstellationError):
            render_chart("猎户座", True)

    def test_unknown(self):
        with self.assertRaises(ConstellationError):
            render_chart("猎户")

    def test_every_constellation(self):
        for item in CONSTELLATIONS:
            svg = render_chart(item.key)
            self.assertEqual(
                svg.count("<circle"),
                len(item.stars),
                msg=item.key,
            )


class PosterTest(unittest.TestCase):
    def test_skeleton(self):
        page = render_poster()
        self.assertIn("<!DOCTYPE html>", page)
        self.assertTrue(page.rstrip().endswith("</html>"))

    def test_all_figures(self):
        page = render_poster()
        self.assertEqual(page.count("<figure>"), 5)

    def test_all_names(self):
        page = render_poster()
        for item in CONSTELLATIONS:
            self.assertIn(item.key, page)
            self.assertIn(item.english, page)

    def test_custom_title(self):
        page = render_poster("星空海报")
        self.assertIn("星空海报", page)

    def test_escaping(self):
        page = render_poster("A&B")
        self.assertIn("A&amp;B", page)


class WorksheetTest(unittest.TestCase):
    def setUp(self):
        self.items = generate_problems(6, seed=11)

    def test_skeleton(self):
        page = render_worksheet(self.items)
        self.assertIn("<!DOCTYPE html>", page)
        self.assertTrue(page.rstrip().endswith("</html>"))

    def test_cards(self):
        page = render_worksheet(self.items)
        self.assertEqual(page.count('class="card"'), 6)

    def test_no_answers(self):
        self.assertNotIn("参考答案", render_worksheet(self.items))

    def test_answers(self):
        page = render_worksheet(self.items, answers=True)
        self.assertIn("参考答案", page)
        self.assertEqual(page.count("<tr>"), 7)

    def test_answer_values(self):
        page = render_worksheet(self.items, answers=True)
        for item in self.items:
            self.assertIn(item.answer, page)

    def test_custom_title(self):
        page = render_worksheet(self.items, title="二班星座")
        self.assertIn("二班星座", page)

    def test_empty(self):
        with self.assertRaises(ConstellationError):
            render_worksheet([])

    def test_bad_item(self):
        with self.assertRaises(ConstellationError):
            render_worksheet(["北斗七星"])

    def test_prompts(self):
        page = render_worksheet(self.items)
        for item in self.items:
            self.assertIn(item.prompt, page)

    def test_single_item(self):
        page = render_worksheet(
            [ConstellationProblem("北斗七星", "count")], answers=True
        )
        self.assertIn("7", page)


if __name__ == "__main__":
    unittest.main()
