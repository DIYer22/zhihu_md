# Markdown 导入知乎编辑器的测试文档

## 文字

这是普通文字

这是 **加粗文字**

这是 *倾斜文字*

这是 ***加粗+倾斜文字***


列表1：

- 一
- 二
- 三

列表2：

* 一
* 二
* 三

数字列表1：

1. 一
2. 二
3. 三

数字列表2：

1. 一
1. 二
1. 三

## 排版
#### 空格结尾：

第一行，末尾两个空格  
两个空格后的另起一行


#### 无空格结尾：

第一行，末尾没有空格
没有空格直接另起一行

#### 分割线：

---


> 这是引用

## 图像

GitHub mirror 图（能成功）:

![GitHub mirror 图](https://ghfast.top/https://raw.githubusercontent.com/Discrete-Distribution-Networks/Discrete-Distribution-Networks.github.io/main/img/ddn-intro.png)

GitHub raw=true URL 图（知乎图片上传失败）:

![GitHub raw=true URL 图](https://github.com/Discrete-Distribution-Networks/Discrete-Distribution-Networks.github.io/blob/main/img/ddn-intro.png?raw=true)

GitHub raw.githubusercontent URL 图（能成功）:

![GitHub raw.githubusercontent URL 图](https://raw.githubusercontent.com/Discrete-Distribution-Networks/Discrete-Distribution-Networks.github.io/main/img/ddn-intro.png)

`githu.io` URL 图（有时候成功、有时候失败）：  

![`githu.io` URL 图](https://discrete-distribution-networks.github.io/img/2d-density.png)


## 公式

**行内公式**：  
DDN 是由 $L$ 层 DDL 组成，以第 $l$ 层 DDL $f_l$ 为例，输入上一层选中的样本 $\mathbf{x}^ * _ {l-1}$，生成 K 个新的样本 $f_l(\mathbf{x}^ * _ {l-1})$， 并从中找出和当前训练样本 $\mathbf{x}$ 最相似的样本 $\mathbf{x}^ * _ l$ 及其 index $k _ {l}^ * $。

**多行公式**：  

$$
k_{l}^* = \underset{k \in \{1, \dots, K\}}{\operatorname{argmin}} \; \left\| f_l(\mathbf{x}^*_{l-1})[k] - \mathbf{x} \right\|^2
$$

$$
\mathbf{x}^*_l = f_l(\mathbf{x}^*_{l-1})[k_l^*]
$$
$$
J_l = \left\| \mathbf{x}^*_l - \mathbf{x} \right\|^2
$$


## 代码

行内代码： 这是 `Python` 库 `zhihu_md`, 使用 `pip install zhihu_md` 安装

Bash：
```bash
# 帮助
python -m zhihu_md --help  # 或者 zhihu_md --help

# 使用
python -m zhihu_md your_markdown.md  # 或者 zhihu_md xxx.md
# 自动生成 your_markdown_for_zhihu.md
```

Python:
```python
from boxx import tree

l = []
for i in range(3):
    item = dict(idx=i, pow=i**2, char=chr(97+i))
    l.append(item)
tree(l)
```
```
└── /: list  3
    ├── 0: dict  3
    │   ├── idx: 0
    │   ├── pow: 0
    │   └── char: a
    ├── 1: dict  3
    │   ├── idx: 1
    │   ├── pow: 1
    │   └── char: b
    └── 2: dict  3
        ├── idx: 2
        ├── pow: 4
        └── char: c
```

## 表格

**空格整齐排列**:

| Item1 | Item2   | Item3   | Item4   |
| ----- | ------- | ------- | ------- |
| Row1  |  value  |  value  |  value  |
| Row2  |  value  |  value  |  value  |
| Row3  |  value  |  value  |  value  |


**生产环境复杂表格**:

| Model   | Efficient | Sample quality | Coverage | Well-behaved latent space | Disentangled latent space | Efficient likelihood | 0-Shot Condition Generation |
|---------|----------|----------------|---------|-----------------------------|-----------------------------|----------------------|--------------------------|
| GANs    | ✓        | ✓              | ✗       | ✓                            | ？                            | n/a                  | ✗                    |
| VAEs    | ✓        | ✗              | ？      | ✓                            | ？                            | ✗                    | ✗                    |
| Flows   | ✓        | ✗              | ？      | ✓                            | ？                            | ✓                    | ✗                    |
| Diffusion | ✗      | ✓              | ？      | ✗                            | ✗                            | ✗                    | ？                    |
| **DDNs (ours)** | ✓       | ✗              | ？      | ✓                            | ？                            | ✗                    | ✓                    |


