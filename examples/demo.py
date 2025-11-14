import operator
from formulaparser import Parser


def demo1():
    """演示普通四则运算"""
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


def demo2():
    """演示带变量的公式及求值"""
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
    print(f'令 (abc=6, _efg=7), 带入公式求值: {ast.evaluate(context)}')
    print('=' * 60)


def demo3():
    """带函数的公式, 可自定义函数"""
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
    print(f'带入 abc=3, 公式求值：{ast.evaluate(context)}')
    print('=' * 60)


def demo4():
    """自定义运算符"""
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


def demo5():
    import pandas as pd
    """自定义函数和运算符, 实现类似R语言的pipline功能"""
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


def demo6():
    """支持部分Python语法，如list/tuple/property/slice/kwargs等"""
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
    print(f'带入 abc=3, operator="operator模块"， 公式求值：{ast.evaluate(context)}')
    print('=' * 60)


if __name__ == '__main__':
    demo1()
    print('\n\n\n')
    demo2()
    print('\n\n\n')
    demo3()
    print('\n\n\n')
    demo4()
    print('\n\n\n')
    demo5()
    print('\n\n\n')
    demo6()
    print('\n\n\n')