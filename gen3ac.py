import argparse
from pycparser import parse_file, c_generator, c_ast, c_parser
from pycparser.c_ast import *


class Generator(c_ast.NodeVisitor):
    def __init__(self):
        self.values = []
        # full of IDs
        self.ls = []
        # var name to type array {'a': ['int'], 'b': ['int'], 'c': ['int']}
        self.dict = dict()
        self.count = 0
        self.unary = []
        self.una = []
        self.blabel = []
        self.cont = []
        self.brea = []
        # self.vals = dict()

    def visit_FileAST(self, node):
        # out = []
        # for i in node:
        #     if isinstance(i, Decl):
        #         out.append(i)
        #     else:
        #         out.append(self.visit(i))
        #     self.__init__()
        # return FileAST(out)
        for i in node:
            self.visit(i)




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

    generator = Generator()
    ast = generator.visit(ast)

    # 打印AST
    # ast.show()



if __name__ == '__main__':
    main()
