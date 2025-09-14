# `zhihu_md`: 自动转换为知乎编辑器支持的 markdown, 支持图片、公式和表格


## 用法

```bash
# 安装
pip install zhihu_md -U

# 帮助
python -m zhihu_md --help  # 或者 zhihu_md --help

# 使用
python -m zhihu_md your_markdown.md  # 或者 zhihu_md xxx.md
# 自动生成 your_markdown_for_zhihu.md

# 如果包含图片，请确保图片和 markdown 都在一个公开的 github repo 中。
# zhihu_md 会自动通过 git remote -v 获取 github repo 地址
# 然后把 markdown 中的 img 转换为知乎能访问的 github 代理地址
```

## 原理
### 图片上传
- 知乎无法通过 `https://github.com/{user-name}/{repo-name}/blob/main/img.png?raw=true` 这种 URL 形式上传 Github 图像
- 但可以走各式各样的 [GitHub 镜像站](https://zhuanlan.zhihu.com/p/706370088) 来中转 repo 中的 image URL
    - 默认方案，用的 `https://bgithub.xyz/`，失效了可自行更换 GitHub 镜像站
- 这些 URL 只需让 知乎 服务器访问一次，就可以完成上传


## 相似项目
- [Markdown4Zhihu](https://github.com/miracleyoo/Markdown4Zhihu)（失去维护）
    - 失去维护，不支持图片 (知乎无法访问 github 服务器) 和公式了
    - Markdown4Zhihu 对 repo 中的 md file 和图片的文件结构有琐碎的要求。还有比较麻烦的配置步骤
    - 本项目 `zhihu_md` 是基于 [Markdown4Zhihu](https://zhuanlan.zhihu.com/p/97455277) 完善而来，改进如下：
        - 一键安装，无需配置
        - 通过镜像站来支持 GitHub 图片上传
        - 对文件结构无要求，更加灵活
        - 增加了对公式的支持
- [VSCode-Zhihu](https://github.com/niudai/VSCode-Zhihu)（失去维护）
    - [作者放弃维护](https://github.com/niudai/VSCode-Zhihu/issues/193) 已经无法登录和使用

