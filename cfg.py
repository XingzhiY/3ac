#!/usr/bin/env python3
import random
import argparse
import sys
import argparse
import json

from pycparser import parse_file, c_generator, c_ast, c_parser
from pycparser.c_ast import *
from pycparser.c_generator import CGenerator
import os
import sys
import re
from graphviz import Digraph

from pycparser import c_generator
from pycparser.c_ast import *

# bb_num=0
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
        self.addr_dict={}
        self.goto_dict={}
        self.edge_dict={}
        self.pre_if_goto=False
        self.pre_statement=None
        self.bb_num=0
    def get_bbnum(self):
        return self.bb_num
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
                if(self.pre_if_goto==False):
                    self.bb_num += 1
                    if(not isinstance(self.pre_statement,c_ast.Goto)):

                        # 检查键是否存在，如果不存在，则初始化一个空 set
                        if ("BB%03d" % (self.bb_num - 1)) not in self.edge_dict:
                            self.edge_dict["BB%03d" % (self.bb_num - 1)] = set()
                        # 现在键肯定存在，可以安全地添加元素
                        self.edge_dict["BB%03d" % (self.bb_num - 1)].add("BB%03d" % (self.bb_num))

                        # self.edge_dict.get(("BB%03d" % (self.bb_num-1)),set()).add("BB%03d" % (self.bb_num))
                        # self.edge_dict[("BB%03d" % (self.bb_num-1))] = ("BB%03d" % (self.bb_num))
                new_block_flag=True
                self.addr_dict[statement.name] = ("BB%03d" % self.bb_num)
            elif(isinstance(statement,c_ast.If)):
                end_block_flag=True
                self.goto_dict[("BB%03d" % self.bb_num)] = (statement.iftrue.name)
                # self.goto_dict[statement.iftrue.name] = ("BB%03d" % self.bb_num)

                # 确保键存在，如果不存在则创建一个新集合
                if "BB%03d" % self.bb_num not in self.edge_dict:
                    self.edge_dict["BB%03d" % self.bb_num] = set()
                # 现在键肯定存在，向集合中添加元素
                self.edge_dict["BB%03d" % self.bb_num].add("BB%03d" % (self.bb_num + 1))

                # self.edge_dict.get(("BB%03d" % self.bb_num), set()).add("BB%03d" % (self.bb_num+1))
                # self.edge_dict[("BB%03d" % self.bb_num)] = ("BB%03d" % (self.bb_num+1))
            elif(isinstance(statement,c_ast.Goto)):
                end_block_flag=True
                self.goto_dict[("BB%03d" % self.bb_num)] = (statement.name)
                # self.goto_dict[statement.name] = ("BB%03d" % self.bb_num)

            # 上一个block的底部 label：
            if(new_block_flag and (len(block)!=0)):
                compound_block=c_ast.Compound(block_items=block)
                block_list.append(compound_block)
                block=[]
            self.pre_if_goto = False
            block.append(statement)
            # 这个block的底部 if goto
            if(end_block_flag ):
                compound_block = c_ast.Compound(block_items=block)
                block_list.append(compound_block)
                block = []
                self.bb_num+=1
                self.pre_if_goto=True

            new_block_flag=False
            end_block_flag=False

            self.pre_statement = statement
        if(len(block)!=0):
            compound_block=c_ast.Compound(block_items=block)
            block_list.append(compound_block)
            self.bb_num+=1

        new_body=c_ast.Compound(block_items=block_list)


        # return node
        return c_ast.FuncDef(decl=node.decl, body=new_body,param_decls=node.param_decls)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog=sys.argv[0])
    parser.add_argument('infile')
    parser.add_argument('edgefile')
    parser.add_argument('outfile')

    args = parser.parse_args()

    input_path = args.infile
    edge_path = args.edgefile
    graph_path = args.outfile

    ast = parse_file(input_path, use_cpp=True)

    # 打印我的 ast 原始格式到文件,用来debug
    # print_json_ast(ast)

    bbgenerator = bbGenerator()
    bb_ast = bbgenerator.visit(ast)
    bbnum=bbgenerator.get_bbnum()

    # print(bbgenerator.addr_dict)
    # print(bbgenerator.goto_dict)
    # print(bbgenerator.edge_dict)

    # 创建 edge
    for key, label in bbgenerator.goto_dict.items():
        # print(f'{key}: {value}')
        addr=bbgenerator.addr_dict[label]
        if key not in bbgenerator.edge_dict:
            # 如果不存在，先为 key 创建一个新的集合
            bbgenerator.edge_dict[key] = set()
        bbgenerator.edge_dict[key].add(addr)
    bbgenerator.edge_dict["ENTRY"] = set()
    bbgenerator.edge_dict["ENTRY"].add('BB000')
    bbgenerator.edge_dict[("BB%03d" % (bbnum-1))] = set()
    bbgenerator.edge_dict[("BB%03d" % (bbnum-1))].add('EXIT')

    print(bbgenerator.edge_dict)

    # 创建一个有向图对象
    dot = Digraph(comment='CFG')

    # 画node
    cgenerator = c_generator.CGenerator()
    for i in range(bbnum):
        dot.node("BB%03d" % i,("BB%03d" % i)+cgenerator.visit(bb_ast.ext[0].body.block_items[i]))
    dot.node("ENTRY")
    dot.node("EXIT")

    #输出 edge
    with open(edge_path, 'w') as file:
        # 遍历字典中的每一项
        for key, values in bbgenerator.edge_dict.items():
            # 遍历集合中的每一个值
            for value in values:
                # 将键和值写入文件，格式为“键 值”
                file.write(f"{key} {value}\n")
                dot.edge(key, value)

    dot.render(directory='.', filename=graph_path)

    # cgenerator = c_generator.CGenerator()
    # tab = "    "
    # with open(args.outfile, 'w') as f:
    #     for i in range(bbnum):
    #         f.write("BB%03d:\n" % i)
    #         f.write(cgenerator.visit(bb_ast.ext[0].body.block_items[i]))


