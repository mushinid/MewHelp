"""剥掉每个 .py 文件开头那段公众号出处注释。

这四行是仓库里固定不变的文件头,出现在 204 个 py 文件里,且永远紧贴第 1 行:

    # 来源：公众号@小林coding
    # 后端八股网站：xiaolincoding.com
    # Agent网站：xiaolinnote.com
    # 简历模版：jianli.xiaolinnote.com

换行符仓库里 CRLF / LF 混用,所以按字节前缀剥离、不重新拼行,文件其余部分
逐字节保持原样。块不在开头就不动它(宁可漏改,不改坏)。

用法:
    python tests/strip_source_comments.py            # 预览(默认)
    python tests/strip_source_comments.py --apply    # 真改
    python tests/strip_source_comments.py --apply E:\\other\\root
"""

import sys
from pathlib import Path

MARKER_LINES = [
    "# 来源：公众号@小林coding",
    "# 后端八股网站：xiaolincoding.com",
    "# Agent网站：xiaolinnote.com",
    "# 简历模版：jianli.xiaolinnote.com",
]

# 两种换行各拼一份前缀,按长度降序匹配(CRLF 优先,免得 LF 那份先命中留下裸 \r)
_PREFIXES = [
    bytes("\r\n".join(MARKER_LINES) + "\r\n", "utf-8"),
    bytes("\n".join(MARKER_LINES) + "\n", "utf-8"),
]

_SKIP_DIRS = {".git", ".venv", "venv", ".idea", "__pycache__", "node_modules", ".mypy_cache", ".ruff_cache"}


def strip_file(path: Path, apply: bool) -> bool:
    """剥掉 path 开头的出处注释块;剥到了返回 True。"""
    raw = path.read_bytes()
    for prefix in _PREFIXES:
        if raw.startswith(prefix):
            if apply:
                path.write_bytes(raw[len(prefix):])
            return True
    return False


def iter_py_files(root: Path):
    for p in sorted(root.rglob("*.py")):
        if any(part in _SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        if p.resolve() == Path(__file__).resolve():
            continue  # 本脚本源码里就含这几行字面量,别把自己改了
        yield p


def main() -> int:
    argv = sys.argv[1:]
    apply = "--apply" in argv
    rest = [a for a in argv if a != "--apply"]
    root = Path(rest[0]).resolve() if rest else Path(__file__).resolve().parent.parent

    if not root.is_dir():
        print(f"不是目录: {root}")
        return 1

    hits = [p for p in iter_py_files(root) if strip_file(p, apply)]
    verb = "已剥除" if apply else "待剥除"
    for p in hits:
        print(f"{verb} {p.relative_to(root)}")
    print(f"\n{verb} {len(hits)} 个文件(根目录 {root})")
    if not apply and hits:
        print("这是预览,加 --apply 才真改。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
