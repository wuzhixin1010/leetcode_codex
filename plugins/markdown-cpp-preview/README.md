# Markdown Cpp Preview

这是一个本地 Codex 插件，用于把 Markdown 文件转换为带 C++ 代码高亮的 HTML 预览。

## 能做什么

- 识别 ` ```cpp `、` ```c++ ` 和 ` ```C++ ` 代码块。
- 渲染标题、列表、引用、链接和普通段落。
- 对 C++ 关键字、类型、字符串、数字、注释和预处理指令做基础高亮。
- 不修改原始 Markdown 文件。

## 使用方式

在 Codex 中请求：

```text
用 Markdown Cpp Preview 预览 F:\codex\leetcode\解题模板.md
```

插件会生成同目录下的 `.html` 预览文件，然后在浏览器中打开。

## 限制

该插件不能替换 Codex 内置 Markdown 查看器本身，只能提供一个带高亮的独立本地 HTML 预览。
