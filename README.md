![GitHub release (latest by date)](https://img.shields.io/github/v/release/nemo2014kk/kane-ai-code-merger?color=green)
![GitHub license](https://img.shields.io/github/license/nemo2014kk/kane-ai-code-merger?color=blue)
![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)

# 🚀 KANE AI - 安卓代码合并工具 (Code Merge Master)

这是一个基于 Python 和 Tkinter 编写的图形化界面工具。它的主要作用是将整个 Android 项目（或任意代码项目）的源代码，一键提取并合并成一个 `.md` (Markdown) 文件，极大地去除了多余文件，方便开发者将代码库作为全局上下文“投喂”给 ChatGPT、Claude 等大语言模型。

## ✨ 核心功能
- **图形化界面 (GUI)**：告别繁琐的命令行，操作简单直观。
- **智能过滤**：支持自定义提取的文件后缀（如 `.kt, .java, .xml` 等），并自动排除 `.git, build` 等无关编译目录。
- **防爆破保护**：自动跳过大于 2MB 的单个文件，防止撑爆大模型的 Token 上限。
- **AI 友好格式**：生成的 Markdown 文件带有明确的目录树索引和标准的语法高亮标签。
- **Token 预估**：合并完成后，自动预估本次投喂将消耗的 Token 数量。
- **配置记忆**：自动保存上一次使用的路径和配置，下次打开直接使用。

## 🛠️ 如何运行
1. 确保你的电脑安装了 [Python 3.x](https://www.python.org/)。
2. 下载本项目中的 `Android Code Merge Master.py` 文件。
3. 双击运行，或者在终端执行：
   ```bash
   python "Android Code Merge Master.py"
