"""星座的数据模型。"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

Point = Tuple[float, float]


@dataclass(frozen=True)
class Constellation:
    """一个星座的星点与连线。"""

    key: str
    english: str
    season: str
    stars: Tuple[Tuple[str, float, float], ...]
    edges: Tuple[Tuple[int, int], ...]

    def __post_init__(self) -> None:
        if not self.stars:
            raise ConstellationError("%s 至少需要一颗星" % self.key)
        if len(self.stars) < 2:
            raise ConstellationError("%s 至少需要两颗星" % self.key)
        for name, x, y in self.stars:
            if not isinstance(name, str) or not name.strip():
                raise ConstellationError("星名不能为空")
            for value in (x, y):
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise ConstellationError("坐标必须是数字")
                if value < 0 or value > 100:
                    raise ConstellationError("坐标必须在 0–100 之间")
        seen = set()
        for a, b in self.edges:
            if a == b:
                raise ConstellationError("连线不能连接同一颗星")
            for index in (a, b):
                if index < 0 or index >= len(self.stars):
                    raise ConstellationError("连线索引越界")
            pair = (min(a, b), max(a, b))
            if pair in seen:
                raise ConstellationError("连线不能重复")
            seen.add(pair)


class ConstellationError(ValueError):
    """星座相关的输入错误。"""


CONSTELLATIONS: Tuple[Constellation, ...] = (
    Constellation(
        key="北斗七星",
        english="Big Dipper",
        season="春季",
        stars=(
            ("天枢", 10, 42),
            ("天璇", 22, 36),
            ("天玑", 34, 40),
            ("天权", 46, 46),
            ("玉衡", 58, 42),
            ("开阳", 72, 38),
            ("摇光", 86, 30),
        ),
        edges=((0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)),
    ),
    Constellation(
        key="猎户座",
        english="Orion",
        season="冬季",
        stars=(
            ("参宿四", 25, 22),
            ("参宿五", 25, 34),
            ("参宿一", 44, 46),
            ("参宿二", 51, 46),
            ("参宿三", 58, 46),
            ("参宿六", 74, 62),
            ("参宿七", 74, 74),
        ),
        edges=((0, 1), (0, 2), (1, 2), (2, 3), (3, 4), (2, 5), (4, 6)),
    ),
    Constellation(
        key="仙后座",
        english="Cassiopeia",
        season="秋季",
        stars=(
            ("王良四", 10, 30),
            ("王良一", 28, 52),
            ("策", 46, 32),
            ("阁道三", 64, 52),
            ("阁道二", 82, 30),
        ),
        edges=((0, 1), (1, 2), (2, 3), (3, 4)),
    ),
    Constellation(
        key="天鹅座",
        english="Cygnus",
        season="夏季",
        stars=(
            ("天津四", 50, 14),
            ("天鹅座β", 50, 38),
            ("天津一", 34, 54),
            ("天津二", 66, 54),
            ("辇道增七", 50, 72),
        ),
        edges=((0, 1), (1, 2), (1, 3), (1, 4)),
    ),
    Constellation(
        key="天琴座",
        english="Lyra",
        season="夏季",
        stars=(
            ("织女一", 46, 18),
            ("织女二", 56, 32),
            ("织女三", 40, 46),
            ("渐台二", 62, 50),
            ("渐台三", 50, 64),
        ),
        edges=((0, 1), (1, 2), (1, 3), (2, 4), (3, 4)),
    ),
)

KINDS = ("count", "season", "star")


def constellations() -> List[str]:
    """返回全部星座名称。"""
    return [item.key for item in CONSTELLATIONS]


def get(key: str) -> Constellation:
    """按名称取星座。"""
    if not isinstance(key, str):
        raise ConstellationError("星座名称必须是字符串")
    for item in CONSTELLATIONS:
        if item.key == key:
            return item
    raise ConstellationError("未知星座：%s" % key)


def star_names(key: str) -> List[str]:
    """返回星座内的星名。"""
    return [name for name, _, _ in get(key).stars]


def star_count(key: str) -> int:
    """返回星数。"""
    return len(get(key).stars)


def edge_count(key: str) -> int:
    """返回连线数。"""
    return len(get(key).edges)


def season(key: str) -> str:
    """返回最佳观测季节。"""
    return get(key).season


def find_by_star(name: str) -> Constellation:
    """按星名查找所属星座。"""
    if not isinstance(name, str) or not name.strip():
        raise ConstellationError("星名不能为空")
    for item in CONSTELLATIONS:
        if any(star == name for star, _, _ in item.stars):
            return item
    raise ConstellationError("未知星名：%s" % name)


@dataclass(frozen=True)
class ConstellationProblem:
    """一道星座题。"""

    key: str
    kind: str
    star: str = ""

    def __post_init__(self) -> None:
        get(self.key)
        if self.kind not in KINDS:
            raise ConstellationError("题型只能是 count、season 或 star")
        if self.kind == "star":
            constellation = find_by_star(self.star)
            if constellation.key != self.key:
                raise ConstellationError("星名不属于该星座")

    @property
    def prompt(self) -> str:
        """题干。"""
        if self.kind == "count":
            return "%s 由几颗星组成？" % self.key
        if self.kind == "season":
            return "%s 最适合在哪个季节观测？" % self.key
        return "「%s」属于哪个星座？" % self.star

    @property
    def answer(self) -> str:
        """答案。"""
        if self.kind == "count":
            return str(star_count(self.key))
        if self.kind == "season":
            return season(self.key)
        return self.key


def generate_problems(
    count: int = 8,
    kinds: Sequence[str] = KINDS,
    seed: Optional[int] = None,
) -> List[ConstellationProblem]:
    """随机生成不重复的星座题。"""
    if isinstance(count, bool) or not isinstance(count, int):
        raise ConstellationError("题目数量必须是整数")
    if count < 1:
        raise ConstellationError("题目数量至少为 1")
    chosen = list(kinds)
    if not chosen:
        raise ConstellationError("至少需要一种题型")
    for kind in chosen:
        if kind not in KINDS:
            raise ConstellationError("未知题型：%s" % kind)

    pool: List[ConstellationProblem] = []
    for item in CONSTELLATIONS:
        for kind in chosen:
            if kind == "star":
                for name, _, _ in item.stars:
                    pool.append(ConstellationProblem(item.key, "star", name))
            else:
                pool.append(ConstellationProblem(item.key, kind))
    if count > len(pool):
        raise ConstellationError("题目数量不能超过 %d" % len(pool))
    rng = random.Random(seed)
    rng.shuffle(pool)
    return pool[:count]
