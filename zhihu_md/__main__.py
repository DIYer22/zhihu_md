# 简单命令行入口（中文提示）
import argparse
from pathlib import Path
from .main import ZhihuMDConverter, DEFAULT_MIRROR_URL


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zhihu_md",
        description="把 Markdown 转为知乎可导入格式（自动处理图片与公式）\n  GitHub: https://github.com/DIYer22/zhihu_md ",
    )
    parser.add_argument(
        "input",
        metavar="MD_PATH",
        help="要转换的 .md 文件路径",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="输出文件",
        help="输出路径，默认在同目录生成 *_for_zhihu.md",
    )
    parser.add_argument(
        "-m",
        "--mirror-url",
        dest="mirror_url",
        default=DEFAULT_MIRROR_URL,
        help="可选的自定义 GitHub 镜像站 URL， 用于中转上传图片到知乎服务器 \n用于替换掉原始 URL 的 https://github.com/ \n 若默认镜像站失效了，可自行搜索 “GitHub 镜像站”",
    )
    parser.add_argument(
        "-e",
        "--encoding",
        help="文件编码，默认自动检测",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        parser.error(f"未找到文件: {in_path}")

    conv = ZhihuMDConverter(mirror_url=args.mirror_url, encoding=args.encoding)
    try:
        conv.convert_file(in_path, args.output)
    except RuntimeError as e:
        # 直接报错退出（例如需要 git 但未检测到 git 仓库）
        parser.error(str(e))


if __name__ == "__main__":
    main()
