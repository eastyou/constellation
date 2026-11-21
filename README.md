# constellation

[![CI](https://github.com/eastyou/constellation/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/constellation/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

星座认星工具：北斗七星、猎户座、仙后座、天鹅座、天琴座的星点连线图，支持星名归属查询与 A4 练习纸。

## 安装

```bash
pip install -e .
```

只需要 Python 3.9+，零第三方依赖。

## 用法

```bash
# 列出星座
constellation list

# 查看星座信息
constellation info 北斗七星

# 输出连线图
constellation chart 猎户座 -o orion.svg

# 输出全部星座海报
constellation poster -o poster.html

# 生成 10 道练习，附答案
constellation sheet --count 10 --seed 1 --answers -o sheet.html

# 只练“星名属于哪个星座”
constellation sheet --count 10 --kinds star -o star.html
```

## 功能

- 5 个常见星座、29 颗有名星
- 星点坐标与连线数据内置，输出 SVG
- 星数、连线数、观测季节查询
- 星名反查所属星座
- 三种题型：星数、季节、星名归属
- 题目去重，随机种子可复现
- A4 打印排版，答案单独一页

## 测试

```bash
python -m unittest discover -s tests -v
```

## 许可

[MIT](LICENSE) © 2026 eastyou
