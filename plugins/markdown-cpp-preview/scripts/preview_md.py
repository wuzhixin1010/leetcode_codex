"""Create a self-contained HTML preview for Markdown with basic C++ highlighting."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path


CPP_KEYWORDS = {
    "auto", "bool", "break", "case", "catch", "char", "class", "const",
    "continue", "default", "delete", "do", "double", "else", "enum", "false",
    "float", "for", "if", "int", "long", "namespace", "new", "nullptr",
    "private", "protected", "public", "return", "short", "signed", "sizeof",
    "static", "struct", "switch", "template", "this", "throw", "true", "try",
    "typename", "union", "unsigned", "using", "virtual", "void", "while",
}
CPP_TYPES = {
    "array", "deque", "greater", "map", "pair", "priority_queue", "queue",
    "set", "size_t", "stack", "string", "unordered_map", "unordered_set", "vector",
}


def highlight_cpp(source: str) -> str:
    escaped = html.escape(source)
    token_re = re.compile(
        r"(//[^\n]*|/\*[\s\S]*?\*/|\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|\b\d+(?:\.\d+)?\b|#[A-Za-z_]+|\b[A-Za-z_][A-Za-z0-9_]*\b)"
    )

    def replace(match: re.Match[str]) -> str:
        token = match.group(0)
        if token.startswith("//") or token.startswith("/*"):
            cls = "comment"
        elif token.startswith(("\"", "'")):
            cls = "string"
        elif token.startswith("#"):
            cls = "preproc"
        elif token[0].isdigit():
            cls = "number"
        elif token in CPP_KEYWORDS:
            cls = "keyword"
        elif token in CPP_TYPES:
            cls = "type"
        else:
            return token
        return f'<span class="{cls}">{token}</span>'

    return token_re.sub(replace, escaped)


def inline_markup(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def render_markdown(source: str) -> str:
    lines = source.replace("\r\n", "\n").split("\n")
    output: list[str] = []
    in_code = False
    language = ""
    code_lines: list[str] = []
    list_tag: str | None = None

    def close_list() -> None:
        nonlocal list_tag
        if list_tag:
            output.append(f"</{list_tag}>")
            list_tag = None

    def close_code() -> None:
        nonlocal in_code, language, code_lines
        css_class = "language-cpp" if language in {"cpp", "c++"} else "language-text"
        code = highlight_cpp("\n".join(code_lines)) if css_class == "language-cpp" else html.escape("\n".join(code_lines))
        output.append(f'<pre><code class="{css_class}">{code}</code></pre>')
        in_code = False
        language = ""
        code_lines = []

    for line in lines:
        fence = re.match(r"^\s*```\s*([\w+#-]*)\s*$", line)
        if fence:
            if in_code:
                close_code()
            else:
                close_list()
                in_code = True
                language = fence.group(1).lower()
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line.strip():
            close_list()
            continue
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if heading:
            close_list()
            level = len(heading.group(1))
            output.append(f"<h{level}>{inline_markup(heading.group(2))}</h{level}>")
            continue
        bullet = re.match(r"^\s*[-*]\s+(.+)$", line)
        ordered = re.match(r"^\s*\d+[.)]\s+(.+)$", line)
        if bullet or ordered:
            wanted = "ol" if ordered else "ul"
            if list_tag != wanted:
                close_list()
                output.append(f"<{wanted}>")
                list_tag = wanted
            item = (ordered or bullet).group(1)
            output.append(f"<li>{inline_markup(item)}</li>")
            continue
        quote = re.match(r"^\s*>\s?(.*)$", line)
        if quote:
            close_list()
            output.append(f"<blockquote>{inline_markup(quote.group(1))}</blockquote>")
            continue
        close_list()
        output.append(f"<p>{inline_markup(line)}</p>")

    if in_code:
        close_code()
    close_list()
    return "\n".join(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    body = render_markdown(args.input.read_text(encoding="utf-8"))
    title = html.escape(args.input.stem)
    document = f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
body {{ max-width: 980px; margin: 40px auto; padding: 0 24px; color: #24292f; font: 16px/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
h1, h2, h3 {{ line-height: 1.25; margin-top: 1.5em; }}
a {{ color: #0969da; }}
code {{ padding: .15em .3em; background: #f6f8fa; border-radius: 4px; font-family: Consolas, monospace; }}
pre {{ padding: 16px; overflow-x: auto; background: #0d1117; border-radius: 8px; }}
pre code {{ padding: 0; color: #c9d1d9; background: transparent; }}
.keyword {{ color: #ff7b72; }} .type {{ color: #79c0ff; }} .string {{ color: #a5d6ff; }}
.number {{ color: #79c0ff; }} .comment {{ color: #8b949e; }} .preproc {{ color: #d2a8ff; }}
blockquote {{ margin-left: 0; padding-left: 16px; color: #57606a; border-left: 4px solid #d0d7de; }}
li {{ margin: 4px 0; }}
</style>
</head>
<body>
{body}
</body>
</html>
'''
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(document, encoding="utf-8")
    print(f"Created: {args.output}")


if __name__ == "__main__":
    main()
