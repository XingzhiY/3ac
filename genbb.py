#!/usr/bin/env python3
import random
import argparse
import sys
import argparse
import json

from pycparser import parse_file, c_generator, c_ast, c_parser
from pycparser.c_ast import *
from pycparser.c_generator import CGenerator

bb_num=0
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


def print_json_ast(ast):
    ast_dict = ast_to_dict(ast)
    with open("aaaaaaaaaaa_my_bb_ast.json", 'w') as output_file:
        json.dump(ast_dict, output_file, indent=2)

class bbGenerator(c_ast.NodeVisitor):
    def __init__(self):
        self.list=[]
    def visit_FileAST(self, node):
        out=[]
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
        compound_list=node.body.block_items #Assignment, Decl...
        block_list=[]
        block=[]
        compound_block=None

        new_block_flag=False
        end_block_flag=False

        for statement in compound_list:
            if(isinstance(statement,c_ast.Label)):
                new_block_flag=True

            if(isinstance(statement,c_ast.If)):
                end_block_flag=True
            if(isinstance(statement,c_ast.Goto)):
                end_block_flag=True
            global bb_num
            if(new_block_flag and (len(block)!=0)):
                compound_block=c_ast.Compound(block_items=block)
                block_list.append(compound_block)
                block=[]
                bb_num+=1
            block.append(statement)
            if(end_block_flag ):
                compound_block = c_ast.Compound(block_items=block)
                block_list.append(compound_block)
                block = []
                bb_num += 1

            new_block_flag=False
            end_block_flag=False
        compound_block=c_ast.Compound(block_items=block)
        block_list.append(compound_block)
        bb_num += 1

        new_body=c_ast.Compound(block_items=block_list)
        # return node
        return c_ast.FuncDef(decl=node.decl, body=new_body,param_decls=node.param_decls)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog=sys.argv[0])
    parser.add_argument('infile')
    parser.add_argument('outfile')
    args = parser.parse_args()

    input_path = args.infile
    output_path = args.outfile

    ast = parse_file(input_path, use_cpp=True)

    # 打印我的 ast 原始格式到文件,用来debug
    # print_json_ast(ast)

    bbgenerator = bbGenerator()
    bb_ast = bbgenerator.visit(ast)

    print_json_ast(bb_ast)

    cgenerator = c_generator.CGenerator()

    tab = "    "
    with open(args.outfile, 'w') as f:
        for i in range(bb_num):
            f.write("BB%03d:\n" % i)
            f.write(cgenerator.visit(bb_ast.ext[0].body.block_items[i]))

            # instr_num = random.randint(1, 5)
            # for j in range(instr_num):
            #     f.write(f"{tab}op left_{j} right_{j}\n")
