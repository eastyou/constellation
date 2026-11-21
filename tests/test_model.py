"""星座模型测试。"""

import unittest

from constellation.model import (
    CONSTELLATIONS,
    KINDS,
    Constellation,
    ConstellationError,
    ConstellationProblem,
    constellations,
    edge_count,
    find_by_star,
    generate_problems,
    get,
    season,
    star_count,
    star_names,
)


class ConstellationTest(unittest.TestCase):
    """逐一验证每个星座的基础信息。"""


def _make_constellation_test(item):
    def test(self):
        self.assertEqual(star_count(item.key), len(item.stars))
        self.assertEqual(edge_count(item.key), len(item.edges))
        self.assertEqual(season(item.key), item.season)
        names = star_names(item.key)
        self.assertEqual(len(names), len(set(names)))
        self.assertGreaterEqual(len(item.stars), 5)
        self.assertGreaterEqual(len(item.edges), 4)
        for _, x, y in item.stars:
            self.assertGreaterEqual(x, 0)
            self.assertLessEqual(x, 100)
            self.assertGreaterEqual(y, 0)
            self.assertLessEqual(y, 100)
        for a, b in item.edges:
            self.assertLess(a, len(item.stars))
            self.assertLess(b, len(item.stars))

    test.__doc__ = item.key
    return test


for _index, _item in enumerate(CONSTELLATIONS):
    setattr(ConstellationTest, "test_%02d" % _index, _make_constellation_test(_item))


class StarTest(unittest.TestCase):
    """逐一验证每颗星的归属。"""


def _make_star_test(item, name):
    def test(self):
        self.assertEqual(find_by_star(name).key, item.key)
        problem = ConstellationProblem(item.key, "star", name)
        self.assertIn(name, problem.prompt)
        self.assertEqual(problem.answer, item.key)

    test.__doc__ = name
    return test


_index = 0
for _item in CONSTELLATIONS:
    for _name in star_names(_item.key):
        setattr(StarTest, "test_%02d" % _index, _make_star_test(_item, _name))
        _index += 1


class InfoTest(unittest.TestCase):
    def test_list(self):
        self.assertEqual(len(constellations()), 5)

    def test_get(self):
        self.assertEqual(get("北斗七星").english, "Big Dipper")

    def test_unknown(self):
        with self.assertRaises(ConstellationError):
            get("猎户")

    def test_bad_key(self):
        with self.assertRaises(ConstellationError):
            get(3)  # type: ignore[arg-type]

    def test_star_count_dipper(self):
        self.assertEqual(star_count("北斗七星"), 7)

    def test_edge_count_dipper(self):
        self.assertEqual(edge_count("北斗七星"), 6)

    def test_star_names_order(self):
        self.assertEqual(star_names("猎户座")[0], "参宿四")

    def test_unknown_star(self):
        with self.assertRaises(ConstellationError):
            find_by_star("北极星")

    def test_empty_star(self):
        with self.assertRaises(ConstellationError):
            find_by_star("  ")

    def test_seasons(self):
        self.assertEqual(season("猎户座"), "冬季")
        self.assertEqual(season("天鹅座"), "夏季")


class ValidationTest(unittest.TestCase):
    def test_too_few_stars(self):
        with self.assertRaises(ConstellationError):
            Constellation("测试", "Test", "春季", (("甲", 10, 10),), ((0, 0),))

    def test_bad_coordinate(self):
        with self.assertRaises(ConstellationError):
            Constellation(
                "测试", "Test", "春季",
                (("甲", -1, 10), ("乙", 20, 20)),
                ((0, 1),),
            )

    def test_bad_edge_index(self):
        with self.assertRaises(ConstellationError):
            Constellation(
                "测试", "Test", "春季",
                (("甲", 10, 10), ("乙", 20, 20)),
                ((0, 2),),
            )

    def test_self_edge(self):
        with self.assertRaises(ConstellationError):
            Constellation(
                "测试", "Test", "春季",
                (("甲", 10, 10), ("乙", 20, 20)),
                ((1, 1),),
            )

    def test_duplicate_edge(self):
        with self.assertRaises(ConstellationError):
            Constellation(
                "测试", "Test", "春季",
                (("甲", 10, 10), ("乙", 20, 20)),
                ((0, 1), (1, 0)),
            )

    def test_blank_star_name(self):
        with self.assertRaises(ConstellationError):
            Constellation(
                "测试", "Test", "春季",
                ((" ", 10, 10), ("乙", 20, 20)),
                ((0, 1),),
            )


class ProblemTest(unittest.TestCase):
    def test_count_problem(self):
        problem = ConstellationProblem("北斗七星", "count")
        self.assertEqual(problem.answer, "7")
        self.assertIn("北斗七星", problem.prompt)

    def test_season_problem(self):
        problem = ConstellationProblem("猎户座", "season")
        self.assertEqual(problem.answer, "冬季")

    def test_star_problem(self):
        problem = ConstellationProblem("北斗七星", "star", "天枢")
        self.assertEqual(problem.answer, "北斗七星")
        self.assertIn("天枢", problem.prompt)

    def test_star_wrong_constellation(self):
        with self.assertRaises(ConstellationError):
            ConstellationProblem("北斗七星", "star", "参宿四")

    def test_unknown_star_problem(self):
        with self.assertRaises(ConstellationError):
            ConstellationProblem("北斗七星", "star", "北极星")

    def test_bad_kind(self):
        with self.assertRaises(ConstellationError):
            ConstellationProblem("北斗七星", "guess")

    def test_unknown_constellation(self):
        with self.assertRaises(ConstellationError):
            ConstellationProblem("猎户", "count")

    def test_frozen(self):
        problem = ConstellationProblem("北斗七星", "count")
        with self.assertRaises(AttributeError):
            problem.kind = "season"  # type: ignore[misc]


class GenerateTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(generate_problems(10, seed=1)), 10)

    def test_unique(self):
        items = generate_problems(20, seed=2)
        keys = [(item.key, item.kind, item.star) for item in items]
        self.assertEqual(len(keys), len(set(keys)))

    def test_single_kind(self):
        items = generate_problems(5, ["season"], seed=3)
        self.assertTrue(all(item.kind == "season" for item in items))

    def test_star_kind(self):
        items = generate_problems(8, ["star"], seed=4)
        self.assertTrue(all(item.kind == "star" and item.star for item in items))

    def test_seed_reproducible(self):
        self.assertEqual(generate_problems(8, seed=5), generate_problems(8, seed=5))

    def test_zero(self):
        with self.assertRaises(ConstellationError):
            generate_problems(0)

    def test_bool(self):
        with self.assertRaises(ConstellationError):
            generate_problems(True)

    def test_empty_kinds(self):
        with self.assertRaises(ConstellationError):
            generate_problems(3, [])

    def test_bad_kind(self):
        with self.assertRaises(ConstellationError):
            generate_problems(3, ["guess"])

    def test_too_many(self):
        with self.assertRaises(ConstellationError):
            generate_problems(9999)

    def test_kind_list(self):
        self.assertEqual(list(KINDS), ["count", "season", "star"])


if __name__ == "__main__":
    unittest.main()
