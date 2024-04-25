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

        # 常量变量表达式 map 到编号的表
        self.expr_num_dict = dict()

        # 编号到变量的地方
        self.num_var_dict = dict()
        # 编号到常量的表
        self.num_const_dict = dict()
        # 编号计数器
        self.num = 0
        # 每个block暂存的statement
        self.temp_statements = []

    def reset(self):
        # 常量变量表达式 map 到编号的表
        self.expr_num_dict = dict()

        # 编号到变量的地方
        self.num_var_dict = dict()
        # 编号到常量的表
        self.num_const_dict = dict()
        # 编号计数器
        self.num = 0
        # 每个block暂存的statement
        self.temp_statements = []

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
        new_block_list = []

        for block in block_list:
            self.reset()
            # components
            statement_list = block.block_items
            # print(len(statement_list))
            for statement in statement_list:
                if isinstance(statement, c_ast.Assignment):
                    self.visit(statement)
                else:
                    self.temp_statements.append(statement)
            second_level_compound = Compound(block_items=self.temp_statements)
            new_block_list.append(second_level_compound)
        new_body = c_ast.Compound(block_items=new_block_list)
        # return node
        return c_ast.FuncDef(decl=node.decl, body=new_body, param_decls=node.param_decls)

    def visit_Assignment(self, node):
        left_id = node.lvalue.name
        if isinstance(node.rvalue, c_ast.Constant):


            self.expr_num_dict[left_id]=self.get_num(node.rvalue)


        #右边是 id 的情况
        elif isinstance(node.rvalue, c_ast.ID):

            self.expr_num_dict[left_id] = self.get_num(node.rvalue)

        #右边是 binary operation 的情况
        elif isinstance(node.rvalue, c_ast.BinaryOp):
            #获取 op 左右两边的 number
            b_left=self.get_num(node.rvalue.left)
            b_op=self.get_num(node.rvalue.op)
            b_right=self.get_num(node.rvalue.right)
            #把他们俩和op加起来去查找一下有没有对应的 number
            expr=b_left+b_op+b_right
            expr_num=self.get_num(expr)
            #有的话就把右边替换成对应的 const，或者id
            if expr_num in self.num_const_dict:
                expr_num=Constant(type="int",value=self.num_const_dict[expr_num])
            elif
            #没有的话，看一下能不能把单个替换成 const
        #给左边一个新的 number，或者是从右边获取的 number
        self.temp_statements.append()
        # modified_rvalue = self.visit(node.rvalue)
        # modified_lvalue = self.visit(node.lvalue)
        modified_node = Assignment(node.op, node.lvalue, modified_rvalue, node.coord)
        # 返回修改后的节点
        self.temp_statements.append(modified_node)
        # return modified_node

    def get_num(self,node):
        if isinstance(node,c_ast.ID):
            # 右边有没有出现过？
            right_id = str(node.name)
            # 如果出现过，那左边打上同样的编号
            if right_id in self.expr_num_dict:
                return self.expr_num_dict[right_id]
            # 如果右边没有出现过，那右边赋予一个新的编号,左边打上同样的编号
            else:
                str_num = str(self.num)
                self.expr_num_dict[right_id] = str_num
                self.num_var_dict[str_num] = right_id
                self.num += 1
                return str_num
        elif isinstance(node.rvalue, c_ast.Constant):

            #右边有没有出现过？
            right_value = str(node.rvalue.value)
            # 如果出现过，那左边打上同样的编号
            if right_value in self.expr_num_dict:
                return self.expr_num_dict[right_value]
            #如果右边没有出现过，那右边赋予一个新的编号,左边打上同样的编号
            else:
                str_num=str(self.num)
                self.expr_num_dict[right_value]=str_num
                self.num_const_dict[str_num]=right_value
                self.num+=1
                return str_num
        elif isinstance(node,str):
            if node in self.expr_num_dict:
                return self.expr_num_dict[node]
            #如果右边没有出现过，那右边赋予一个新的编号,左边打上同样的编号
            else:
                str_num=str(self.num)
                self.expr_num_dict[node]=str_num
                self.num+=1
                return str_num
        print("errorrrrr")
        return "-1"

    # def visit_BinaryOp(self, node):
    #     right_node = self.visit(node.right)
    #     left_node = self.visit(node.left)
    #
    #     binary_op = BinaryOp(op=node.op, left=left_node, right=right_node)
    #     return binary_op

    # def visit_FuncCall(self, node):
    #
    #     return node
    #
    # def visit_ID(self, node):
    #     # return node.name
    #     id = node.name
    #     if id not in self.expr_num_dict:
    #         self.expr_num_dict[id] = str(self.num)
    #         self.num_var_dict[str(self.num)] = id
    #         self.num += 1
    #     return node
    #
    # def visit_Constant(self, node):
    #     # 打印Constant节点的类型和值
    #     # return node.value
    #     value = str(node.value)
    #     if value not in self.expr_num_dict:
    #         self.expr_num_dict[value] = str(self.num)
    #         self.num_cont_dict[str(self.num)] = value
    #         self.num += 1
    #     return node


def main(input_path, output_path):
    # 获取3ac ast
    ast = parse_file(input_path, use_cpp=True)

    # 打印3ac到output
    new_generator = c_generator.CGenerator()
    ast_str = new_generator.visit(ast)
    with open("ccc_3ac.c", 'w') as file:
        file.write(ast_str)

    # 打印我的 ast json原始格式到文件,用来debug
    ast_dict = ast_to_dict(ast)
    with open("ccc_my_flat_ast.json", 'w') as output_file:
        json.dump(ast_dict, output_file, indent=2)

    # 处理成区块ast
    bbgenerator = bbGenerator()
    bb_ast = bbgenerator.visit(ast)
    bbnum = bbgenerator.get_bbnum()

    # 打印我的 ast json原始格式到文件,用来debug
    ast_dict = ast_to_dict(bb_ast)
    with open("ccc_my_bb_ast.json", 'w') as output_file:
        json.dump(ast_dict, output_file, indent=2)

    # 用vn generator去把bb ast变成去除冗余的ast
    vngenerator = vnGenerator()
    vn_ast = vngenerator.visit(bb_ast)

    # 打印我的 ast json原始格式到文件,用来debug
    ast_dict = ast_to_dict(vn_ast)
    with open("ccc_my_vn_ast.json", 'w') as output_file:
        json.dump(ast_dict, output_file, indent=2)
    # 打印AST
    new_generator = c_generator.CGenerator()
    print(new_generator.visit(vn_ast))
    ast_str = new_generator.visit(vn_ast)
    with open(output_path, 'w') as file:
        file.write(ast_str)  # 将AST字符串写入文件


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=sys.argv[0])
    parser.add_argument('infile')
    parser.add_argument('outfile')

    args = parser.parse_args()
    input_path = args.infile
    output_path = args.outfile
    main(input_path, output_path)
