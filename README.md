# Formula Parser

一个用于解析和计算字符串公式的Python项目。

实现了基于运算符和函数的公式解析，可自定义公式的运算符和函数，实现公式的自由定义与求值。


## 编译

```bash
python -m build --wheel
```



## 内置函数
| 名称                 | 调用函数                                       | 运算                      |
|:-------------------|--------------------------------------------|-------------------------|
| add                | operator.add(a, b)                         | 加法(a + b)               |
| concat             | operator.concat(seq1, seq2)                | 字符串拼接(seq1 + seq2)      |
| contains           | operator.contains(seq, obj)                | 包含测试(obj in seq)        |
| truediv            | operator.truediv(a, b)                     | 除法(a / b)               |
| floordiv           | operator.floordiv(a, b)                    | 除法(a // b)              |
| and_               | operator.and_(a, b)                        | 按位与(a & b)              |
| xor                | operator.xor(a, b)                         | 按位异或(a ^ b)             |
| invert             | operator.invert(a)                         | 按位取反(~ a)               |
| or_                | operator.or_(a, b)                         | 按位或(a \| b)             |
| pow                | operator.pow(a, b)                         | 取幂(a ** b)              |
| is_                | operator.is_(a, b)                         | 标识(a is b)              |
| is_not             | operator.is_not(a, b)                      | 标识(a is not b)          |
| is_none            | operator.is_none(a)                        | 标识(a is None)           |
| is_not_none        | operator.is_not_none(a)                    | 标识(a is not None)       |
| setitem            | operator.setitem(obj, k, v)                | 索引赋值(obj[k] = v)        |
| delitem            | operator.delitem(obj, k)                   | 索引删除(del obj[k])        |
| getitem            | operator.getitem(obj, k)                   | 索引取值(obj[k])            |
| lshift             | operator.lshift(a, b)                      | 左移(a << b)              |
| mod                | operator.mod(a, b)                         | 取模(a % b)               |
| mul                | operator.mul(a, b)                         | 乘法(a * b)               |
| matmul             | operator.matmul(a, b)                      | 矩阵乘法(a @ b)             |
| neg                | operator.neg(a)                            | 取反（算术）(- a)             |
| not_               | operator.not_(a)                           | 取反（逻辑）(not a)           |
| pos                | operator.pos(a)                            | 正数(+ a)                 |
| rshift             | operator.rshift(a, b)                      | 右移(a >> b)              |
| setitem(seq, slice | operator.setitem(seq, slice(i, j), values) | 切片赋值(seq[i:j] = values) |
| delitem(seq, slice | operator.delitem(seq, slice(i, j))         | 切片删除(del seq[i:j])      |
| getitem(seq, slice | operator.getitem(seq, slice(i, j))         | 切片取值(seq[i:j])          |
| mod                | operator.mod(s, obj)                       | 字符串格式化(s % obj)         |
| sub                | operator.sub(a, b)                         | 减法(a - b)               |
| truth              | operator.truth(obj)                        | 真值测试(obj)               |
| lt                 | operator.lt(a, b)                          | 比较(a < b)               |
| le                 | operator.le(a, b)                          | 比较(a <= b)              |
| eq                 | operator.eq(a, b)                          | 相等(a == b)              |
| ne                 | operator.ne(a, b)                          | 不等(a != b)              |
| ge                 | operator.ge(a, b)                          | 比较(a >= b)              |
| gt                 | operator.gt(a, b)                          | 比较(a > b)               |
| slice              | slice                                      | slice                   |
| abs                | abs                                        | 绝对值                     |
| max                | max                                        | 最大值                     |
| min                | min                                        | 最小值                     |
| sum                | sum                                        | 求和                      |
| sin                | math.sin                                   | sin                     |
| cos                | math.cos                                   | cos                     |
| tan                | math.tan                                   | tan                     |
| log                | math.log                                   | log                     |
| exp                | math.exp                                   | exp                     |
| sqrt               | math.sqrt                                  | sqrt                    |




## 内置运算符

### 单目运算符
| 运算符 | 实际调用函数          |
|-----|-----------------|
| +   | operator.pos    |
| -   | operator.neg    |
| ~   | operator.invert |

### 双目运算符
运算符优先级数值必须大于0,且数字越大，优先级越高。

| 运算符  | 实际调用函数            | 优先级   |
|------|-------------------|-------|
| <    | operator.lt       | 11000 |
| <=   | operator.le       | 11000 |
| ==   | operator.eq       | 11000 |
| !=   | operator.ne       | 11000 |
| \>=  | operator.ge       | 11000 |
| \>   | operator.gt       | 11000 |
| \|   | operator.or_      | 12000 |
| ^    | operator.xor      | 13000 |
| &    | operator.and_     | 14000 |
| <<   | operator.lshift   | 15000 |
| \>\> | operator.rshift   | 15000 |
| +    | operator.add      | 16000 |
| -    | operator.sub      | 16000 |
| *    | operator.mul      | 17000 |
| /    | operator.truediv  | 17000 |
| //   | operator.floordiv | 17000 |
| %    | operator.mod      | 17000 |
| @    | operator.matmul   | 17000 |


## 功能

### 普通四则运算
```python
from formulaparser import Parser
print('演示普通四则运算')
print('=' * 60)
# 创建解析器
parser = Parser()
# 将公式解析为语法树
formula = '2 + 3 * (5 - 2)'
ast = parser.parse(formula)

print(f'公式: {formula}')
print(f'解析后的公式: {ast}')
print('-' * 50)
print(f'解析后的语法树：')
print(ast.render())
print('-' * 50)

print(f'公式求值：{ast.evaluate()}')
print('=' * 60)
```


### 带变量的公式及求值
```python
from formulaparser import Parser
print('演示带变量的公式及求值')
print('=' * 60)
# 创建解析器
parser = Parser()
# 将公式解析为语法树
formula = '2 + 3 * (5 - abc) + _efg'
ast = parser.parse(formula)

print(f'公式: {formula}')
print(f'解析后的公式: {ast}')
print('-' * 50)
print(f'解析后的语法树：')
print(ast.render())
print('-' * 50)

context = dict(abc=6, _efg=7)
print(f'令 (abc=6, _efg=7), 代入公式求值: {ast.evaluate(context)}')
print('=' * 60)
```


### 带函数的公式, 可自定义函数
```python
from formulaparser import Parser
print('带函数的公式, 可自定义函数')
print('=' * 60)
# 创建解析器
parser = Parser()

print('创建并注册 ratio_sum函数, 函数效果为将函数第一个参数后的所有参数相加, 然后与第一个参数相乘, 最后将结果返回')
def ratio_sum(ratio, *args):
    return sum(args) * ratio
parser.register_function('ratio_sum', ratio_sum)

# 将公式解析为语法树
formula = '2 + 3 * max(5, 6, 2) + ratio_sum(5, 1, 2, abc)'
ast = parser.parse(formula)

print(f'公式: {formula}, max为内置函数, ratio_sum为自定义函数')
print(f'解析后的公式: {ast}')
print('-' * 50)
print(f'解析后的语法树：')
print(ast.render())
print('-' * 50)
context = dict(abc=3)
print(f'代入 abc=3, 公式求值：{ast.evaluate(context)}')
print('=' * 60)
```


### 自定义运算符
```python
from formulaparser import Parser
print('自定义运算符')
print('=' * 60)
# 创建解析器
parser = Parser()

print('定义单目运算符 "&*", 效果为计算当前值的三次方并返回')
parser.register_unary_op('&*', lambda x: x ** 3)
print('定义双目运算符 "¥&", 优先级位于加减与乘除之间, 效果为将左右操作数相加后乘2并返回')
parser.register_binary_op('$%', lambda x, y: (x+y)*2, 16500)

# 将公式解析为语法树
formula = '&*3 + 2000 $% 30 / 6'
ast = parser.parse(formula)

print(f'公式: {formula}')
print(f'解析后的公式: {ast}')
print('-' * 50)
print(f'解析后的语法树：')
print(ast.render())
print('-' * 50)

print(f'公式求值：{ast.evaluate()}')
print('=' * 60)
```


### 自定义函数和运算符, 实现类似R语言的pipline功能
```python
import pandas as pd
from formulaparser import Parser
print('自定义函数和运算符, 实现类似R语言的pipline功能')
print('=' * 60)

# 创建解析器
parser = Parser()

print('自定义管道运算符 "%>%", 效果为将左侧作为参数传递给右侧调用执行, left %>% right 等价于执行 right(left)')
parser.register_binary_op('%>%', lambda data, func: func(data), 100000)

print('自定义groupby函数, 结果为返回另外一个函数, 与管道运算符搭配使用, data %>% p_groupby("a") 等价于 data.groupby("a")')
def p_groupby(key):
    def wrapper(data):
        return data.groupby(key)
    return wrapper
parser.register_function('p_groupby', p_groupby)

print('自定义p_mean函数, 结果为返回另外一个函数, 与管道运算符或p_aggregate搭配使用, groupby_obj %>% p_mean("b") 等价于 groupby_obj["b"].mean()')
def p_mean(col):
    def wrapper(data):
        return data[col].mean()
    return wrapper
parser.register_function('p_mean', p_mean)

print('自定义p_sum函数, 结果为返回另外一个函数, 与管道运算符或p_aggregate搭配使用, groupby_obj %>% p_sum("c") 等价于 groupby_obj["c"].sum()')
def p_sum(col):
    def wrapper(data):
        return data[col].sum()
    return wrapper
parser.register_function('p_sum', p_sum)

print('自定义aggregate函数, 结果为返回另外一个函数, 与管道运算符搭配使用, groupby_obj %>% p_aggregate(p_mean("b"), p_sum("c")) 等价于 pd.concat([groupby_obj["b"].mean(), groupby_obj["c"].sum()], axis=1)')
def p_aggregate(*args):
    def wrapper(data):
        return pd.concat([func(data) for func in args], axis=1)
    return wrapper
parser.register_function('p_aggregate', p_aggregate)

formula = 'df %>% p_groupby("a") %>% p_aggregate(p_mean("b"), p_sum("c"))'
ast = parser.parse(formula)

print(f'公式: {formula}')
print(f'解析后的公式: {ast}')
print('-' * 50)
print(f'解析后的语法树：')
print(ast.render())
print('-' * 50)

df = pd.DataFrame([[1,19,3], [2,5,8], [1,5,3], [2,9,7]], columns=['a', 'b', 'c'])
print(f'令变量 df = \n{df}')
print(f'公式求值：\n{ast.evaluate(dict(df=df))}')
print('=' * 60)
```


### 支持部分Python语法，如list/tuple/property/slice/kwargs等
```python
import operator
from formulaparser import Parser

print('支持部分Python语法，如list/tuple/property/slice/kwargs等')
print('=' * 60)
# 创建解析器
parser = Parser()
# 将公式解析为语法树
formula = '2 + 3 * max((5, 6, 2)) + sum([5, 1, 2, abc][::2], start=1) - operator.sub(1, 2)'
ast = parser.parse(formula)

print(f'公式: {formula}')
print(f'解析后的公式: {ast}')
print('-' * 50)
print(f'解析后的语法树：')
print(ast.render())
print('-' * 50)
context = dict(abc=3, operator=operator)
print(f'代入 abc=3, operator="operator模块"， 公式求值：{ast.evaluate(context)}')
print('=' * 60)
```

