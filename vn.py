import random
import argparse
import sys
import argparse
import json

from pycparser import parse_file, c_generator, c_ast, c_parser
from pycparser.c_ast import *
from pycparser.c_generator import CGenerator


def ast_to_dict(node):
    if isinstance(node, c_ast.Node):
        result = {type(node).__name__: {attr: ast_to_dict(getattr(node, attr)) for attr in node.attr_names}}
        for name, child in node.children():
            result[type(node).__name__][name] = ast_to_dict(child)
        return result
    elif isinstance(node, list):
        return [ast_to_dict(child) for child in node]
    else:
        return node


class bbGenerator(c_ast.NodeVisitor):
    def __init__(self):
        self.list = []
        self.bb_num = 0

    def get_bbnum(self):
        return self.bb_num

    def visit_FileAST(self, node):
        out = []
        for i in node:
            if isinstance(i, Decl):
                out.append(i)
                print("declare bug 1")
            else:
                out.append(self.visit(i))
            # self.reset()
            # print("@@@@@@@@@@@@@@@@@@@@")
        return FileAST(out)

    def visit_FuncDef(self, node):
        compound_list = node.body.block_items  # Assignment, Decl...
        block_list = []
        block = []
        compound_block = None

        new_block_flag = False
        end_block_flag = False

        for statement in compound_list:
            if (isinstance(statement, c_ast.Label)):
                new_block_flag = True

            if (isinstance(statement, c_ast.If)):
                end_block_flag = True
            if (isinstance(statement, c_ast.Goto)):
                end_block_flag = True
            # global bb_num
            if (new_block_flag and (len(block) != 0)):
                compound_block = c_ast.Compound(block_items=block)
                block_list.append(compound_block)
                block = []
                self.bb_num += 1
            block.append(statement)
            if (end_block_flag):
                compound_block = c_ast.Compound(block_items=block)
                block_list.append(compound_block)
                block = []
                self.bb_num += 1

            new_block_flag = False
            end_block_flag = False
        compound_block = c_ast.Compound(block_items=block)
        block_list.append(compound_block)
        self.bb_num += 1

        new_body = c_ast.Compound(block_items=block_list)
        # return node
        return c_ast.FuncDef(decl=node.decl, body=new_body, param_decls=node.param_decls)


class vnGenerator(c_ast.NodeVisitor):
    def __init__(self):
        self.list = []
        self.bb_num = 0

    def get_bbnum(self):
        return self.bb_num

    def visit_FileAST(self, node):
        out = []
        for i in node:
            if isinstance(i, Decl):
                out.append(i)
                print("declare bug 1")
            else:
                out.append(self.visit(i))
            # self.reset()
            # print("@@@@@@@@@@@@@@@@@@@@")
        return FileAST(out)

    def visit_FuncDef(self, node):
        block_list = node.body.block_items  # Assignment, Decl...

        num = 0

        for block in block_list:
            num += 1
        print(num)
        new_body = c_ast.Compound(block_items=block_list)
        # return node
        return c_ast.FuncDef(decl=node.decl, body=new_body, param_decls=node.param_decls)


def main(input_path, output_path):
    # 获取3ac ast
    ast = parse_file(input_path, use_cpp=True)

    # 打印3ac到output
    new_generator = c_generator.CGenerator()
    ast_str = new_generator.visit(ast)
    with open(output_path, 'w') as file:
        file.write(ast_str)

    # 打印我的 ast json原始格式到文件,用来debug
    ast_dict = ast_to_dict(ast)
    with open("ccc_my_new_ast.json", 'w') as output_file:
        json.dump(ast_dict, output_file, indent=2)

    # 处理成区块ast
    bbgenerator = bbGenerator()
    bb_ast = bbgenerator.visit(ast)
    bbnum = bbgenerator.get_bbnum()

    # 打印我的 ast json原始格式到文件,用来debug
    ast_dict = ast_to_dict(bb_ast)
    with open("ccc_my_new_ast.json", 'w') as output_file:
        json.dump(ast_dict, output_file, indent=2)

    # 用vn generator去把bb ast变成去除冗余的ast
    vngenerator = vnGenerator()
    vn_ast = vngenerator.visit(bb_ast)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=sys.argv[0])
    parser.add_argument('infile')
    parser.add_argument('outfile')

    args = parser.parse_args()
    input_path = args.infile
    output_path = args.outfile
    main(input_path, output_path)
