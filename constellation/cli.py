"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .model import (
    KINDS,
    ConstellationError,
    constellations,
    edge_count,
    find_by_star,
    generate_problems,
    get,
    star_count,
    star_names,
)
from .render import render_chart, render_poster, render_worksheet


def build_parser() -> argparse.ArgumentParser:
    """构造命令行解析器。"""
    parser = argparse.ArgumentParser(
        prog="constellation",
        description="星座：星点连线图、星座信息与练习纸",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="列出全部星座")

    info = subparsers.add_parser("info", help="查看星座信息")
    info.add_argument("key", help="星座名称，如 北斗七星")

    chart = subparsers.add_parser("chart", help="输出星座连线图 SVG")
    chart.add_argument("key", help="星座名称")
    chart.add_argument("--size", type=int, default=320, help="边长，默认 320")
    chart.add_argument("-o", "--output", default=None, help="输出文件")

    poster = subparsers.add_parser("poster", help="输出全部星座海报")
    poster.add_argument("--title", default="认识星座", help="海报标题")
    poster.add_argument("-o", "--output", default=None, help="输出文件")

    sheet = subparsers.add_parser("sheet", help="生成 A4 练习纸")
    sheet.add_argument("--count", type=int, default=8, help="题目数量，默认 8")
    sheet.add_argument("--kinds", default=",".join(KINDS), help="题型，逗号分隔：count、season、star")
    sheet.add_argument("--seed", type=int, default=None, help="随机种子")
    sheet.add_argument("--title", default="星座练习", help="练习纸标题")
    sheet.add_argument("--answers", action="store_true", help="追加参考答案")
    sheet.add_argument("-o", "--output", default=None, help="输出文件")
    return parser


def _write_output(text: str, output: Optional[str]) -> None:
    if not output:
        print(text)
        return
    path = Path(output)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("已写入 %s" % path)


def _parse_kinds(text: str) -> List[str]:
    parts = [part.strip() for part in text.split(",") if part.strip()]
    if not parts:
        raise ConstellationError("至少需要一种题型")
    return parts


def main(argv: Optional[List[str]] = None) -> int:
    """命令行主函数，返回进程退出码。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            for key in constellations():
                item = get(key)
                print("%s（%s）· %s · %d 颗星" % (key, item.english, item.season, len(item.stars)))
            return 0
        if args.command == "info":
            item = get(args.key)
            print("%s（%s）" % (item.key, item.english))
            print("季节：%s" % item.season)
            print("星数：%d，连线：%d" % (star_count(args.key), edge_count(args.key)))
            print("星名：%s" % "、".join(star_names(args.key)))
            return 0
        if args.command == "chart":
            _write_output(render_chart(args.key, args.size), args.output)
            return 0
        if args.command == "poster":
            _write_output(render_poster(args.title), args.output)
            return 0
        problems = generate_problems(args.count, _parse_kinds(args.kinds), args.seed)
        _write_output(render_worksheet(problems, args.title, args.answers), args.output)
        return 0
    except ConstellationError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1
