import argparse
import io
from contextlib import redirect_stdout

from pycparser import parse_file, c_generator, c_ast, c_parser
from pycparser.c_ast import *


import json

def ast_to_dict_1(node):
    if isinstance(node, c_ast.Node):
        result = {type(node).__name__: {attr: ast_to_dict_1(getattr(node, attr)) for attr in node.attr_names}}
        for name, child in node.children():
            result[type(node).__name__][name] = ast_to_dict_1(child)
        return result
    elif isinstance(node, list):
        return [ast_to_dict_1(child) for child in node]
    else:
        return node



def main():
    parser = argparse.ArgumentParser(description='Process some files.')

    parser.add_argument('input_file', type=str, help='the path to the preprocessed input C file')
    parser.add_argument('output_file', type=str, help='the path to the output 3AC C file')

    args = parser.parse_args()

    input_path = args.input_file
    output_path = args.output_file


    # 创建一个 C 语言解析器的实例
    parser = c_parser.CParser()

    # 解析输入文件
    ast = parse_file(input_path, use_cpp=True)
    ast_dict=ast_to_dict_1(ast)
    with open(output_path, 'w') as output_file:
        json.dump(ast_dict, output_file, indent=2)
    # 将捕获的输出写入文件
    # 使用StringIO来捕获show的输出
    # buffer = io.StringIO()
    # ast.show()
    new_generator = c_generator.CGenerator()
    print(new_generator.visit(ast))
    # with open(output_path, 'w') as output_file:
    #     output_file.write(buffer.getvalue())
    # 打印AST
    # ast.show()




if __name__ == '__main__':
    main()
