"""星座图与练习纸渲染。"""

from __future__ import annotations

import html
from typing import List, Sequence

from .model import (
    CONSTELLATIONS,
    ConstellationError,
    ConstellationProblem,
    get,
    star_names,
)


def render_chart(key: str, size: int = 320) -> str:
    """绘制单个星座的连线图。"""
    constellation = get(key)
    if isinstance(size, bool) or not isinstance(size, int):
        raise ConstellationError("尺寸必须是整数")
    if size < 200 or size > 900:
        raise ConstellationError("尺寸必须在 200–900 之间")
    margin = 34
    span = size - margin * 2

    def sx(value: float) -> float:
        return margin + value / 100.0 * span

    def sy(value: float) -> float:
        return margin + value / 100.0 * span

    parts: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
        'role="img" aria-label="%s">' % (size, size, size, size, html.escape(constellation.key)),
        "<title>%s</title>" % html.escape(constellation.key),
        '<rect x="0" y="0" width="%d" height="%d" fill="#f7fafc"/>' % (size, size),
        '<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="#cbd2d9"/>'
        % (margin, margin, span, span),
    ]
    for a, b in constellation.edges:
        _, ax, ay = constellation.stars[a]
        _, bx, by = constellation.stars[b]
        parts.append(
            '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#90cdf4" stroke-width="1.6"/>'
            % (sx(ax), sy(ay), sx(bx), sy(by))
        )
    for name, x, y in constellation.stars:
        parts.append(
            '<circle cx="%.1f" cy="%.1f" r="4" fill="#2b6cb0"/>' % (sx(x), sy(y))
        )
        parts.append(
            '<text x="%.1f" y="%.1f" font-size="11" fill="#4a5568" '
            'font-family="Noto Sans SC, PingFang SC, sans-serif">%s</text>'
            % (sx(x) + 7, sy(y) - 6, html.escape(name))
        )
    parts.append("</svg>")
    return "\n".join(parts)


_CSS = """
@page { size: A4; margin: 12mm; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
       color: #1f2933; background: #fff; }
.sheet { padding: 4mm; }
h1 { margin: 0 0 2mm; font-size: 22px; text-align: center; letter-spacing: 2px; }
.meta { margin: 0 0 5mm; text-align: center; color: #616e7c; font-size: 12px; }
.cards { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; }
.card { border: 1px solid #cbd2d9; border-radius: 3mm; padding: 4mm; page-break-inside: avoid; }
.prompt { font-size: 15px; line-height: 1.7; margin: 0 0 3mm; }
.answer-line { border-bottom: 1px dashed #9aa5b1; height: 28px; }
.answers { page-break-before: always; margin-top: 6mm; }
.answers h2 { font-size: 18px; border-left: 4px solid #2f855a; padding-left: 3mm; color: #276749; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { border: 1px solid #cbd2d9; padding: 2mm 3mm; text-align: left; }
th { background: #f5f7fa; }
.poster { display: grid; grid-template-columns: 1fr 1fr; gap: 5mm; }
.poster figure { margin: 0; text-align: center; page-break-inside: avoid; }
.poster figcaption { font-size: 13px; color: #4a5568; margin-top: 2mm; }
@media print { .sheet { padding: 0; } }
""".strip()


def render_worksheet(
    problems: Sequence[ConstellationProblem],
    title: str = "星座练习",
    answers: bool = False,
) -> str:
    """生成可打印的星座练习纸。"""
    items = list(problems)
    if not items:
        raise ConstellationError("至少需要一道题")
    for item in items:
        if not isinstance(item, ConstellationProblem):
            raise ConstellationError("题目必须是 ConstellationProblem")
    cards = [
        '<div class="card"><p class="prompt">%d. %s</p><div class="answer-line"></div></div>'
        % (index, html.escape(item.prompt))
        for index, item in enumerate(items, 1)
    ]
    sections = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % html.escape(title),
        "<style>%s</style></head><body>" % _CSS,
        '<main class="sheet">',
        "<h1>%s</h1>" % html.escape(title),
        '<p class="meta">姓名：__________　班级：__________　日期：__________</p>',
        '<section class="cards">',
        "\n".join(cards),
        "</section>",
    ]
    if answers:
        rows = [
            "<tr><td>%d</td><td>%s</td><td>%s</td></tr>"
            % (index, html.escape(item.prompt), html.escape(item.answer))
            for index, item in enumerate(items, 1)
        ]
        sections.append(
            '<section class="answers"><h2>参考答案</h2>'
            "<table><thead><tr><th>题号</th><th>题目</th><th>答案</th></tr></thead>"
            "<tbody>%s</tbody></table></section>" % "\n".join(rows)
        )
    sections.append("</main></body></html>")
    return "\n".join(sections)


def render_poster(title: str = "认识星座") -> str:
    """把全部星座拼成一页 A4 海报。"""
    figures = [
        '<figure>%s<figcaption>%s（%s）· %s</figcaption></figure>'
        % (
            render_chart(item.key, 300),
            html.escape(item.key),
            html.escape(item.english),
            html.escape(item.season),
        )
        for item in CONSTELLATIONS
    ]
    return "\n".join(
        [
            "<!DOCTYPE html>",
            '<html lang="zh-CN"><head><meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>%s</title>" % html.escape(title),
            "<style>%s</style></head><body>" % _CSS,
            '<main class="sheet">',
            "<h1>%s</h1>" % html.escape(title),
            '<p class="meta">星名与连线仅为认星示意，实际星空请以观测软件为准</p>',
            '<section class="poster">',
            "\n".join(figures),
            "</section>",
            "</main></body></html>",
        ]
    )
