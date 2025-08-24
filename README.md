# `zhihu_md`: 一键转换为知乎编辑器支持的 markdown, 支持图片、公式和表格


## 用法

```bash
# 安装
pip install zhihu_md

# 帮助
python -m zhihu_md --help  # 或者 zhihu_md --help

# 使用
python -m zhihu_md your_markdown.md  # 或者 zhihu_md xxx.md
# 自动生成 your_markdown_for_zhihu.md

# 如果包含图片，请确保图片和 markdown 都在一个公开的 github repo 中。
# zhihu_md 会自动通过 git remote -v 获取 github repo 地址
# 然后把 markdown 中的 img 转换为知乎能访问的 github 代理地址
```

## 相似项目
- [Markdown4Zhihu](https://github.com/miracleyoo/Markdown4Zhihu)
    - Markdown4Zhihu 失去维护，不支持图片 (知乎切断了对 github 图片) 和公式了
    - Markdown4Zhihu 对 repo 中的 md file 和图片的文件结构有琐碎的要求。还有比较麻烦的配置步骤
    - 本项目 `zhihu_md` 是基于 [Markdown4Zhihu](https://zhuanlan.zhihu.com/p/97455277) 完善而来
- [VSCode-Zhihu](https://github.com/niudai/VSCode-Zhihu)
    - [作者放弃维护](https://github.com/niudai/VSCode-Zhihu/issues/193) 已经无法登录和使用

