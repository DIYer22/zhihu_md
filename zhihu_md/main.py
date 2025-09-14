import os
import re
import subprocess
import chardet
import functools
import os.path as op
from typing import Optional, Union
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

DEFAULT_MIRROR_URL = "https://bgithub.xyz/"


class ZhihuMDConverter:
    """
    知乎 Markdown 转换器

    将普通 Markdown 转为知乎可导入格式，主要处理图片链接与公式。
    """

    COMPRESS_THRESHOLD = 5e5  # 图片压缩阈值（暂未启用）

    def __init__(
        self,
        mirror_url: str = DEFAULT_MIRROR_URL,
        encoding: Optional[str] = None,
        compress_images: bool = False,
    ):
        """
        初始化

        Args:
            mirror_url: 额外前缀（如自建 CDN），会直接拼接在最终图片 URL 前
            encoding: 文件编码，None 时自动检测
            compress_images: 是否压缩图片（暂未启用）
        """
        self.mirror_url = mirror_url
        self.encoding = encoding
        self.compress_images = compress_images
        # 以下属性在转换时计算
        self.git_root: Optional[Path] = None
        self.raw_mirror_url: Optional[str] = (
            None  # 形如 https://raw.githubusercontent.com/owner/repo/branch/
        )

    def detect_encoding(self, file_path: Union[str, Path]) -> str:
        """自动检测文件编码"""
        with open(str(file_path), "rb") as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            detected_encoding = result["encoding"]
            print(f"检测到编码: {result}")
            return detected_encoding

    def formula_ops_old(self, lines: str) -> str:
        """旧版公式处理（转为图片）"""
        lines = re.sub(
            "((.*?)\$\$)(\s*)?([\s\S]*?)(\$\$)\n",
            '\n<img src="https://www.zhihu.com/equation?tex=\\4" alt="\\4" class="ee_img tr_noresize" eeimg="1">\n',
            lines,
        )
        lines = re.sub(
            "(\$)(?!\$)(.*?)(\$)",
            ' <img src="https://www.zhihu.com/equation?tex=\\2" alt="\\2" class="ee_img tr_noresize" eeimg="1"> ',
            lines,
        )
        return lines

    def formula_ops(self, lines: str) -> str:
        """将 $...$ 转为 $$...$$（知乎更稳）"""
        lines = re.sub("(\$)(?!\$)(.*?)(\$)", " $$\\2$$ ", lines)
        return lines

    # ---------------- Git / URL 相关 ----------------
    def find_github_url(self, start_path: Union[str, Path]) -> str:
        """
        基于 start_path 查找 git 根目录与 GitHub 仓库信息，设置 raw_mirror_url。
        无 git 仓库时提示用户先 git clone；无 GitHub 远程时提示必须属于 GitHub 仓库。

        返回 GitHub 项目页 URL（https://github.com/owner/repo）。
        """
        start_path = Path(start_path).resolve()
        work_dir = start_path if start_path.is_dir() else start_path.parent

        # 1) 找 git 根
        try:
            git_root = (
                subprocess.check_output(
                    ["git", "-C", str(work_dir), "rev-parse", "--show-toplevel"],
                    stderr=subprocess.STDOUT,
                )
                .decode()
                .strip()
            )
        except subprocess.CalledProcessError:
            raise RuntimeError(
                "未检测到 git 仓库，请先 git clone 对应的 GitHub 仓库后再运行。"
            )

        self.git_root = Path(git_root)

        # 2) 找远程并解析 GitHub 地址
        try:
            remote_txt = subprocess.check_output(
                ["git", "-C", git_root, "remote", "-v"], stderr=subprocess.STDOUT
            ).decode()
        except subprocess.CalledProcessError:
            raise RuntimeError("读取 git remote 失败，请检查仓库配置。")

        # 选择优先 origin 的 GitHub 远程
        github_url = None
        candidates = []
        for line in remote_txt.splitlines():
            # 例: origin  https://github.com/owner/repo.git (fetch)
            #     origin  git@github.com:owner/repo.git (push)
            parts = line.split()
            if len(parts) >= 2:
                name, url = parts[0], parts[1]
                if "github.com" in url:
                    if name == "origin":
                        candidates.insert(0, url)
                    else:
                        candidates.append(url)
        if candidates:
            raw_url = candidates[0]
            # 统一为 https://github.com/owner/repo 形式
            if raw_url.startswith("git@github.com:"):
                owner_repo = raw_url.split(":", 1)[1]
                owner_repo = owner_repo.rstrip(".git")
                github_url = f"https://github.com/{owner_repo}"
            elif raw_url.startswith("https://github.com/") or raw_url.startswith(
                "http://github.com/"
            ):
                owner_repo = raw_url.split("github.com/", 1)[1]
                owner_repo = owner_repo.rstrip(".git")
                github_url = f"https://github.com/{owner_repo}"

        if not github_url:
            raise RuntimeError(
                "未找到 GitHub 远程，请确保此项目属于某个 GitHub 仓库（配置 remote）。"
            )

        # owner 与 repo
        owner_repo = github_url.rstrip("/").split("github.com/")[-1]

        # 3) 检测默认分支（优先 origin/HEAD），回退 main，再回退 master
        branch = None
        try:
            head_ref = (
                subprocess.check_output(
                    [
                        "git",
                        "-C",
                        git_root,
                        "symbolic-ref",
                        "--short",
                        "refs/remotes/origin/HEAD",
                    ],
                    stderr=subprocess.STDOUT,
                )
                .decode()
                .strip()
            )
            # 形如 origin/main
            if "/" in head_ref:
                branch = head_ref.split("/", 1)[1]
        except subprocess.CalledProcessError:
            pass

        if not branch:
            # 若无法检测，尝试存在性检查
            for b in ("main", "master"):
                try:
                    subprocess.check_output(
                        ["git", "-C", git_root, "rev-parse", f"origin/{b}"],
                        stderr=subprocess.STDOUT,
                    )
                    branch = b
                    break
                except subprocess.CalledProcessError:
                    continue

        if not branch:
            # 兜底 main
            branch = "main"

        self.raw_mirror_url = (
            f"https://raw.githubusercontent.com/{owner_repo}/{branch}/"
        )
        self.owner_repo = owner_repo
        self.branch = branch
        return github_url

    def relative_path_to_url(self, ori_path: str, mirror_url: Optional[str]) -> str:
        """
        将仓库内相对路径转为可直接访问的图片 URL。
        例（owner/repo = xxx/xxx.github.io, 分支 main, 路径 img/ddn-intro.png）：
        - 当 mirror_url 为空：
          https://raw.githubusercontent.com/xxx/xxx.github.io/main/img/ddn-intro.png
        - 当 mirror_url 不为空：
          f"{mirror_url}/xxx/xxx.github.io/blob/main/img/ddn-intro.png?raw=true"
        """
        if not self.raw_mirror_url:
            raise RuntimeError("尚未初始化仓库信息，请先调用 find_github_url()。")

        # 统一路径分隔符
        rel_path = ori_path.replace("\\", "/").lstrip("./")
        raw_url = f"{self.raw_mirror_url}{rel_path}"
        if mirror_url:
            gh_url = f"https://github.com/{self.owner_repo}/blob/{self.branch}/{rel_path}?raw=true"
            return gh_url.replace("https://github.com/", f"{mirror_url.rstrip('/')}/")
        return raw_url

    # ---------------- 图片/公式处理 ----------------
    def _rename_image_ref(self, match, file_parent: str, original: bool = True):
        """图片链接替换：将相对路径替换为 GitHub 原图地址"""
        ori_path = match.group(2) if original else match.group(1)

        # 去掉前导 ./
        if ori_path.startswith("./"):
            ori_path = ori_path[2:]

        # 本地实际路径（相对于 markdown 文件）
        full_local_path = op.join(file_parent, ori_path)
        if not op.exists(full_local_path):
            # print(f"非本地图片文件，跳过: {full_local_path}")
            return match.group(0)

        if not self.git_root or not self.raw_mirror_url:
            # 需要 Git 信息但尚未初始化，直接尝试初始化；失败则抛错退出
            self.find_github_url(file_parent)

        # 计算仓库内相对路径
        try:
            rel_to_repo = os.path.relpath(full_local_path, str(self.git_root))
        except Exception:
            # 兜底：若计算失败，按原始相对路径
            rel_to_repo = ori_path

        github_url = self.relative_path_to_url(rel_to_repo, self.mirror_url)

        print(f"本地: {full_local_path}")
        print(f"链接: {github_url}")

        if original:
            return "![" + match.group(1) + "](" + github_url + ")"
        else:
            return '<img src="' + github_url + '"'

    def image_ops(self, lines: str, file_parent: str) -> str:
        """
        处理图片链接：
        1. ![]()
        2. <img src="LINK" alt="..." />
        """
        lines = re.sub(
            r"\!\[(.*?)\]\((.*?)\)",
            functools.partial(
                self._rename_image_ref, file_parent=file_parent, original=True
            ),
            lines,
        )
        lines = re.sub(
            r'<img src="(.*?)"',
            functools.partial(
                self._rename_image_ref, file_parent=file_parent, original=False
            ),
            lines,
        )
        return lines

    def _has_local_images(self, text: str, file_parent: str) -> bool:
        """
        预扫描内容中是否包含“指向本地文件且真实存在”的图片引用。

        - Markdown: ![alt](path)
        - HTML: <img src="path" ...>
        仅当 path 不是 http(s) 或 data:，且拼接到 file_parent 后存在时返回 True。
        """
        # Markdown 图片
        md_paths = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
        # HTML 图片（同时支持单/双引号）
        html_paths = re.findall(r"<img\s+[^>]*src=[\"']([^\"']+)[\"']", text)
        candidates = md_paths + html_paths

        def is_remote(p: str) -> bool:
            ps = p.strip()
            return (
                ps.startswith("http://")
                or ps.startswith("https://")
                or ps.startswith("//")
                or ps.startswith("data:")
            )

        for raw in candidates:
            # 处理 markdown 中可能出现的标题，例如: (a.png "title")
            cand = raw.strip()
            if not cand:
                continue
            # 拆掉可能的 title，取第一个空白前的部分
            cand = cand.split()[0].strip("\"'")
            if is_remote(cand):
                continue
            # 去掉可能的前导 ./
            local_path = cand[2:] if cand.startswith("./") else cand
            full_local_path = op.join(file_parent, local_path)
            if op.exists(full_local_path):
                return True
        return False

    def reduce_single_image_size(self, image_path: Union[str, Path]) -> Path:
        """
        压缩单图（暂未启用）
        """
        if Image is None:
            raise ImportError("需要安装 Pillow 才能压缩图片")

        output_path = Path(image_path).parent / (Path(image_path).stem + ".jpg")
        if op.exists(image_path):
            img = Image.open(image_path)
            if img.size[0] > img.size[1] and img.size[0] > 1920:
                img = img.resize(
                    (1920, int(1920 * img.size[1] / img.size[0])), Image.ANTIALIAS
                )
            elif img.size[1] > img.size[0] and img.size[1] > 1080:
                img = img.resize(
                    (int(1080 * img.size[0] / img.size[1]), 1080), Image.ANTIALIAS
                )
            img.convert("RGB").save(output_path, optimize=True, quality=85)
        return output_path

    def convert_file(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
    ) -> str:
        """
        转换 Markdown 文件
        """
        input_path = Path(input_path)
        file_parent = str(input_path.parent)

        # 编码
        encoding = self.encoding
        if encoding is None:
            encoding = self.detect_encoding(input_path)

        # 读文件
        with open(str(input_path), "r", encoding=encoding) as f:
            lines = f.read()

        # 仅当存在本地图片时，才尝试检测 Git 仓库；否则无需依赖 Git
        if self._has_local_images(lines, file_parent):
            # 若没有 git 或不是 GitHub 仓库，find_github_url 会抛出 RuntimeError，直接终止
            self.find_github_url(file_parent)

        # 图片与公式
        lines = self.image_ops(lines, file_parent)
        lines = self.formula_ops(lines)

        # 输出路径
        if output_path is None:
            output_path = op.join(file_parent, input_path.stem + "_for_zhihu.md")
        else:
            output_path = str(output_path)

        # 写出
        with open(output_path, "w+", encoding=encoding) as fw:
            fw.write(lines)

        print(f"已生成: {output_path}")
        return output_path

    def git_ops(self, input_path: Union[str, Path]):
        """将变更推送到 GitHub"""
        input_path = Path(input_path)
        subprocess.run(["git", "add", "-A"])
        subprocess.run(["git", "commit", "-m", f"update file {input_path.stem}"])
        subprocess.run(["git", "push", "-u", "origin", "master"])
