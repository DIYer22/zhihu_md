import os
import re
import argparse
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


class ZhihuMDConverter:
    """
    知乎 Markdown 转换器
    
    用于将普通 Markdown 文件转换为适合知乎导入的格式，
    主要处理图片链接和数学公式。
    """
    
    COMPRESS_THRESHOLD = 5e5  # The threshold of compression
    
    def __init__(self, 
                 base_url: str = "http://113.44.140.251:9000/junk/Discrete-Distribution-Networks.github.io/",
                 encoding: Optional[str] = None,
                 compress_images: bool = False):
        """
        初始化转换器
        
        Args:
            base_url: 图片的基础 URL
            encoding: 文件编码，如果为 None 会自动检测
            compress_images: 是否压缩图片（当前未使用）
        """
        self.base_url = base_url
        self.encoding = encoding
        self.compress_images = compress_images
        
    def detect_encoding(self, file_path: Union[str, Path]) -> str:
        """检测文件编码"""
        with open(str(file_path), "rb") as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            detected_encoding = result["encoding"]
            print(f"Detected encoding: {result}")
            return detected_encoding
    
    def formula_ops_old(self, lines: str) -> str:
        """旧版公式处理（转换为图片）"""
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
        """处理公式，将单个 $ 包围的公式转换为 $$ 包围"""
        lines = re.sub("(\$)(?!\$)(.*?)(\$)", " $$\\2$$ ", lines)
        return lines

    def _rename_image_ref(self, match, file_parent: str, original: bool = True):
        """重命名图片引用的内部方法"""
        ori_path = match.group(2) if original else match.group(1)

        # Remove any leading ./ from the path
        if ori_path.startswith("./"):
            ori_path = ori_path[2:]

        # Check if the image file exists relative to the markdown file
        full_local_path = op.join(file_parent, ori_path)
        if not op.exists(full_local_path):
            print(f"Warning: Image file not found: {full_local_path}")
            return match.group(0)  # Return original if file doesn't exist

        # Convert relative path to absolute URL
        github_url = self.base_url + ori_path

        print(f"Local path: {full_local_path}")
        print(f"Converted URL: {github_url}")

        if original:
            return "![" + match.group(1) + "](" + github_url + ")"
        else:
            return '<img src="' + github_url + '"'

    def image_ops(self, lines: str, file_parent: str) -> str:
        """
        处理图片链接
        
        支持两种格式：
        1. ![]() 
        2. <img src="LINK" alt="CAPTION" style="zoom:40%;" />
        """
        lines = re.sub(
            r"\!\[(.*?)\]\((.*?)\)",
            functools.partial(self._rename_image_ref, file_parent=file_parent, original=True),
            lines,
        )
        lines = re.sub(
            r'<img src="(.*?)"', 
            functools.partial(self._rename_image_ref, file_parent=file_parent, original=False), 
            lines
        )
        return lines

    def reduce_single_image_size(self, image_path: Union[str, Path]) -> Path:
        """
        压缩单个图片大小（当前未使用）
        
        Args:
            image_path: 图片路径
            
        Returns:
            压缩后的图片路径
        """
        if Image is None:
            raise ImportError("PIL is required for image compression")
            
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

    def convert_file(self, 
                     input_path: Union[str, Path], 
                     output_path: Optional[Union[str, Path]] = None) -> str:
        """
        转换 Markdown 文件
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径，如果为 None 则自动生成
            
        Returns:
            输出文件路径
        """
        input_path = Path(input_path)
        file_parent = str(input_path.parent)
        
        # 检测编码
        encoding = self.encoding
        if encoding is None:
            encoding = self.detect_encoding(input_path)
        
        # 读取文件内容
        with open(str(input_path), "r", encoding=encoding) as f:
            lines = f.read()
        
        # 处理图片和公式
        lines = self.image_ops(lines, file_parent)
        lines = self.formula_ops(lines)
        
        # 确定输出路径
        if output_path is None:
            output_path = op.join(file_parent, input_path.stem + "_for_zhihu.md")
        else:
            output_path = str(output_path)
        
        # 写入转换后的内容
        with open(output_path, "w+", encoding=encoding) as fw:
            fw.write(lines)
        
        print(f"Output file created: {output_path}")
        return output_path

    def git_ops(self, input_path: Union[str, Path]):
        """推送更改到 GitHub"""
        input_path = Path(input_path)
        subprocess.run(["git", "add", "-A"])
        subprocess.run(["git", "commit", "-m", f"update file {input_path.stem}"])
        subprocess.run(["git", "push", "-u", "origin", "master"])


def main():
    """命令行入口点"""
    parser = argparse.ArgumentParser(
        description='将 Markdown 文件转换为适合知乎导入的格式',
        prog='zhihu-md'
    )
    parser.add_argument(
        "--compress",
        action="store_true",
        help="Compress the image which is too large (currently not used)",
    )
    parser.add_argument(
        "-i", "--input", 
        type=str, 
        required=True,
        help="Path to the file you want to transfer."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file path (optional, will auto-generate if not provided)"
    )
    parser.add_argument(
        "-e", "--encoding", 
        type=str, 
        help="Encoding of the input file (will auto-detect if not provided)"
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://113.44.140.251:9000/junk/Discrete-Distribution-Networks.github.io/",
        help="Base URL for images"
    )
    parser.add_argument(
        "--git",
        action="store_true",
        help="Push changes to git after conversion"
    )

    args = parser.parse_args()
    
    # 创建转换器实例
    converter = ZhihuMDConverter(
        base_url=args.base_url,
        encoding=args.encoding,
        compress_images=args.compress
    )
    
    try:
        # 执行转换
        output_path = converter.convert_file(args.input, args.output)
        
        # 如果需要，执行 git 操作
        if args.git:
            converter.git_ops(args.input)
            
    except FileNotFoundError:
        print(f"Error: File not found: {args.input}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
