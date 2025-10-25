# Formula Parser

一个用于解析和计算数学公式的Python项目。

## 项目结构

```
formulaparser/
├── src/
│   └── formulaparser/
│       └── __init__.py
├── tests/
│   └── __init__.py
├── requirements.txt
├── README.md
└── .gitignore
```

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

```python
from formulaparser import Parser

# 示例代码
parser = Parser()
result = parser.parse("1 + 2 * 3")
print(result)
```

## 开发

```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
python -m pytest tests/
```

## 许可证

MIT License

