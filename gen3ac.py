import argparse
import json

from pycparser import parse_file, c_generator, c_ast, c_parser
from pycparser.c_ast import *
from pycparser.c_generator import CGenerator

from a2.show_ast import ast_to_dict


class Generator(c_ast.NodeVisitor):
    def __init__(self):
        self.braces = [] #大括号
        self.tempId = 0 #临时var的计数器
        self.binaryVar = [] #binary临时var
        self.unaryVar = [] #unary操作推进去的var name
        self.ids = []  #ID 的name
        self.constants = []  #常数的value
        self.labelId=0 #label 的 id
        self.labels=[] #label列表，都要消耗掉
        self.cond_labels=[] #cond产生的label
        # -------------------------
        self.break_labels=[]
        self.continue_labels=[]
        self.name_list=[]
        self.temp_list=[]
        self.flat_block_items = []
        #常数------------
        self.const=c_ast.Constant(type="int",value="1")


    def reset(self):
        self.braces = [] #大括号
        self.tempId = 0 #临时var的计数器
        self.binaryVar = [] #binary临时var
        self.unaryVar = [] #unary操作推进去的var name
        self.ids = []  #ID 的name
        self.constants = []  #常数的value
        self.labelId=0 #label 的 id
        self.labels=[] #label列表，都要消耗掉
        self.cond_labels=[] #cond产生的label
        # -------------------------
        self.break_labels=[]
        self.continue_labels=[]
        self.name_list=[]
        self.temp_list=[]
        self.flat_block_items = []
    def get_label(self,x):
        return c_ast.Label(name=x,stmt=self.const)
    def get_goto(self,x):
        return c_ast.Goto(name=x)
    def myprint(self,x):
        print("\n======start=====\n")
        print (x)
        print("\n====end=======\n")
    def enter_switch(self,label):
        self.break_labels.append(label)

    def quit_switch(self):
        self.break_labels.pop()
    def get_switch(self):
        return self.break_labels[-1]
    def enter_loop(self,continue_label,break_label):
        self.break_labels.append(break_label)
        self.continue_labels.append(continue_label)

    def quit_loop(self):
        self.break_labels.pop()
        self.continue_labels.pop()
    def get_continue(self):
        return self.continue_labels[-1]
    def get_break(self):
        return self.break_labels[-1]
    def generate_temp(self):
        temp_name = f"temp{self.tempId}"
        self.tempId += 1
        print(f"int {temp_name};")
        new_type=c_ast.IdentifierType(names=["int"])
        new_TypeDecl=c_ast.TypeDecl(declname=temp_name,type=new_type,quals=None,align=None)
        self.flat_block_items.append(c_ast.Decl(name=temp_name,type=new_TypeDecl,quals=None,align=None,storage=None,funcspec=None,init=None,bitsize=None))
        return temp_name
    def get_id(self,s):
        return c_ast.ID(name=s)
    def generate_label(self):
        label_name = f"label{self.labelId}"
        self.labelId += 1

        return label_name
    def visit_FileAST(self, node):
        out=[]
        for i in node:
            if isinstance(i, Decl):
                out.append(i)
                print("declare bug 1")
            else:
                out.append(self.visit(i))
            self.reset()
            # print("@@@@@@@@@@@@@@@@@@@@")
        return FileAST(out)
    def visit_FuncDef(self, node):
        # 首先处理函数定义的其他部分，比如函数声明等
        # ...
        # self.visit(node.decl)
        # 然后找到并访问Compound节点
        # out = []
        # if isinstance(node.body, c_ast.Compound):
        #     out.append(self.visit(node.body)) # visit compound
        # print("}")
        # return FuncDef(node.decl,node.param_decls,out,node.coord)
        # return node


        modified_body = None
        if isinstance(node.body, c_ast.Compound):
            # 如果函数体是一个复合语句，访问并可能修改它
            # modified_body = self.visit(node.body)
            self.visit(node.body)

            modified_body = c_ast.Compound(block_items=self.flat_block_items)
            # self.flat_block_items = []



        # 构造一个新的FuncDef节点
        # 假设FuncDef的构造器参数为: decl（函数声明）, param_decls（参数声明列表）, body（函数体）, coord（节点的坐标）
        # 你需要根据你使用的具体AST库的文档来调整这些参数
        modified_node = c_ast.FuncDef(
            decl=node.decl,
            param_decls=None,
            body=modified_body if modified_body is not None else node.body,
            # coord=node.coord
        )
        # self.myprint(node.decl)
        # self.myprint(node.param_decls)
        # self.myprint(self.flat_block_items)
        # self.myprint(modified_body)

        return modified_node
    def visit_FuncDecl(self, node):
        generator = c_generator.CGenerator()
        func_decl_code = generator.visit(node)
        print(func_decl_code)
        print("{")


    # def visit_Compound(self, node):
    #     # 在这里处理Compound节点
    #     # 遍历Compound节点中的所有语句和声明
    #     # out=[]
    #     # for item in node.block_items:
    #     #     out.append(item)
    #     #     self.visit(item)
    #     # # out.append(node.block_items[0])
    #     # return Compound(out)
    #
    #     # self.myprint(len(node.block_items))
    #
    #     # 初始化一个列表来收集可能已修改的语句和声明
    #     out = []
    #
    #     # 检查node.block_items是否存在
    #     if node.block_items:
    #         for item in node.block_items:
    #             # 对每个项调用self.visit()，这可能会返回一个修改过的节点
    #             visited_item = self.visit(item)

                # 如果self.visit返回了一个值，我们假设它是一个修改过的节点，并将其添加到out列表中
                # 如果没有返回值（即self.visit返回None），则添加原始项
                # if visited_item is not None:
                #     print("hello")
                #     out.append(visited_item)
                # else:
                #     out.append(item)

        # 使用可能已修改的项列表构造一个新的Compound节点
        # 注意：根据你所使用的AST库，Compound节点的构造方式可能有所不同
        # 以下是一个示例，你可能需要根据你的库文档进行调整
        # modified_node = c_ast.Compound(block_items=self.flat_block_items)
        # self.flat_block_items = []
        # self.myprint(len(modified_node.block_items))


        # 返回修改后的Compound节点
        # return modified_node
        # return c_ast.Compound(block_items=self.flat_block_items)


    def visit_Assignment(self, node):

        # left = self.visit(node.lvalue)  # 假设左值是一个简单的标识符
        # left=self.name_list.pop()
        # right = self.visit(node.rvalue)
        # right=self.name_list.pop()
        #
        # # 打印三地址代码
        # print(f"{left} = {right};")

        modified_lvalue = self.visit(node.lvalue)
        # 从name_list中弹出左值名字，这假设self.visit(node.lvalue)导致了一个名字被推入name_list
        left = self.name_list.pop()

        # 访问并可能修改右值
        modified_rvalue = self.visit(node.rvalue)
        # 根据修改后的rvalue更新name_list，并弹出最后一个元素
        right = self.name_list.pop()

        # 打印三地址代码形式的赋值，这里假设修改后的right已经是3AC格式
        print(f"{left} = {right};")

        # 构造一个新的Assignment节点，使用原始的操作符、左值和修改后的右值
        # 注意：这里假设op和coord在原始节点中是可用的，且你希望保持它们不变
        modified_node = Assignment(node.op, node.lvalue, modified_rvalue, node.coord)
        self.flat_block_items.append(modified_node)
        # 返回修改后的节点
        return modified_node
    def visit_ExprList(self, node):
        name_list=[]
        id_list=[]
        if node.exprs:
            for expr in node.exprs:
                id_list.append(self.visit(expr))
                value=self.name_list.pop()
                name_list.append(value)
        # return name_list
        self.name_list.append(name_list)
        return id_list
    def visit_FuncCall(self,node):
        name=self.visit(node.name)
        name=self.name_list.pop()

        id_list=[]

        func_call_str = f"{name}()"


        # 检查是否存在参数
        if node.args:
            # 访问参数节点并获取包含所有参数的字符串列表
            id_list = self.visit(node.args)
            args = self.name_list.pop()

            # 将参数列表转换为字符串，参数之间用逗号和空格分隔
            args_str = ', '.join(args)

            # 使用参数字符串更新func_call_str
            func_call_str = f"{name}({args_str})"

        # 返回完整的函数调用字符串
        temp_name=self.generate_temp()
        temp=self.get_id(temp_name)

        print(f"{temp_name}={func_call_str};")
        # self.myprint(id_list)

        # return temp
        self.name_list.append(temp_name)
        self.flat_block_items.append(c_ast.Assignment(op="=",lvalue=temp,rvalue=c_ast.FuncCall(name=node.name,args=c_ast.ExprList(exprs=id_list))))




    def visit_TypeDecl(self,node):
        name = node.declname
        type_list = node.type.names
        print(f"{' '.join(type_list)} {name};")
        # return name
        self.name_list.append(name)

    def visit_Decl(self, node):
        name="unknown 34254"
        if node.type:
            name=self.visit(node.type)
            name=self.name_list.pop()
        if node.init:
            right=self.visit(node.init)
            right=self.name_list.pop()
            print(f"{name} = {right};")
        # print(f"{type}")
        self.flat_block_items.append(node)


    def visit_UnaryOp(self, node):
        res="visit_UnaryOp res"
        temp=None
        # 获取表达式的字符串表示
        if node.expr:
            a=self.visit(node.expr)
            name=self.name_list.pop()
        else:
            print("todo 4231")
            return

        if node.op == '++':
            # 前置自增
            print(f"{name} = {name} + 1;")
            self.flat_block_items.append(c_ast.Assignment(op="=",lvalue=a,rvalue=c_ast.BinaryOp(op="+",left=a,right=self.const)))
            res=name
            temp=a;
        elif node.op == 'p++':
            # 如果是后置自增，使用临时变量保存原始值
            res = self.generate_temp()
            temp=self.get_id(res)

            print(f"{res} = {name};")
            self.flat_block_items.append(c_ast.Assignment(op="=",lvalue=temp,rvalue=a))

            print(f"{name} = {name} + 1;")
            self.flat_block_items.append(c_ast.Assignment(op="=",lvalue=a,rvalue=c_ast.BinaryOp(op="+",left=a,right=self.const)))

        elif node.op in '--':
            # 前置自减
            print(f"{name} = {name} - 1;")
            self.flat_block_items.append(c_ast.Assignment(op="=",lvalue=a,rvalue=c_ast.BinaryOp(op="-",left=a,right=self.const)))

            res=name
            temp=a
        elif node.op == 'p--':
            # 如果是后置自减，使用临时变量保存原始值
            res = self.generate_temp()
            temp=self.get_id(res)

            print(f"{res} = {name};")
            self.flat_block_items.append(c_ast.Assignment(op="=",lvalue=temp,rvalue=a))

            print(f"{name} = {name} - 1;")
            self.flat_block_items.append(c_ast.Assignment(op="=",lvalue=a,rvalue=c_ast.BinaryOp(op="-",left=a,right=self.const)))

        elif node.op == '&':
            res=self.generate_temp()
            temp=self.get_id(res)

            id=self.visit(node.expr)
            value=self.name_list.pop()
            print(f"{res} = &{value};")
            self.flat_block_items.append(c_ast.Assignment(op="=",lvalue=temp,rvalue=c_ast.UnaryOp(op="&",expr=id)))

        else:
            print("unkbown unary op")
        # return res
        self.name_list.append(res)
        #return 给别人的数，const或者temp或者ID
        return temp


    def visit_BinaryOp(self, node):
        right_name = ""
        left_name = ""
        # 处理左侧表达式
        left_node = self.visit(node.left)
        left_name=self.name_list.pop()
        # 处理右侧表达式
        right_node = self.visit(node.right)
        right_name=self.name_list.pop()


        # 打印二元操作的3AC
        result_name = self.generate_temp()
        print(f"{result_name} = {left_name} {node.op} {right_name};")
        new_binary_op = BinaryOp(node.op, left_node, right_node)
        new_id=ID(result_name)

        new_assign=Assignment("=", new_id, new_binary_op)
        self.flat_block_items.append(new_assign)
        # return result_name
        self.name_list.append(result_name)
        return new_id

    def visit_ID(self, node):
        # return node.name
        self.name_list.append(node.name)
        return node

    def visit_Constant(self, node):
        # 打印Constant节点的类型和值
        # return node.value
        self.name_list.append(node.value)
        return node
    def visit_DoWhile(self,node):
        start_label = self.generate_label()
        end_label = self.generate_label()
        label2 = self.generate_label()
        self.enter_loop(start_label,end_label)
        print(f"goto {label2};")
        print(f"{start_label}:1;")

        resName = self.visit(node.cond)
        resName=self.name_list.pop()
        print(f"if ({resName})  goto {label2};")
        print(f"goto {end_label};")

        print(f"{label2}:1;")
        self.visit(node.stmt)

        print(f"goto {start_label};")
        print(f"{end_label}:1;")
        self.quit_loop()

    def visit_While(self,node):
        start_label = self.generate_label()
        end_label = self.generate_label()
        label2 = self.generate_label()
        self.enter_loop(start_label,end_label)
        print(f"{start_label}:1;")
        resName= self.visit(node.cond)
        resName=self.name_list.pop()
        print(f"if ({resName})  goto {label2};")
        print(f"goto {end_label};")
        print(f"{label2}:1;")
        self.visit(node.stmt)
        print(f"goto {start_label};")
        print(f"{end_label}:1;")
        self.quit_loop()
    def visit_If(self, node):
        label0 = self.generate_label()
        label1 = self.generate_label()
        label2 = self.generate_label()

        temp=self.visit(node.cond)
        resName=self.name_list.pop()
        print(f"if ({resName})  goto {label0};")
        self.flat_block_items.append(c_ast.If(cond=temp,iftrue=self.get_goto(label0),iffalse=None))
        print(f"goto {label1};")
        self.flat_block_items.append(self.get_goto(label1))

        print(f"{label0}:1;")
        self.flat_block_items.append(self.get_label(label0))
        if(node.iftrue):

            self.visit(node.iftrue)
            print(f"goto {label2};")
            self.flat_block_items.append(self.get_goto(label2))
        print(f"{label1}:1;")
        self.flat_block_items.append(self.get_label(label1))
        if(node.iffalse):
            self.visit(node.iffalse)
        print(f"{label2}:1;")
        self.flat_block_items.append(self.get_label(label2))
    def visit_Switch(self,node):
        #拿到 case 的对象 i
        temp=self.visit(node.cond)
        name = self.name_list.pop()
        # 拿到 case 的数量
        num_case=len(node.stmt.block_items)
        # print(num_case)
        # print(name)
        label_end=self.generate_label()
        self.enter_switch(label_end)
        # 对每一个 case
        case_labels=[]
        real_case_labels=[]
        for i in range(num_case):
            temp_label=self.generate_label()
            case_labels.append(temp_label)
            real_case_labels.append(self.get_label(temp_label))
        for i in range(num_case):
            item=node.stmt.block_items[i]

            if (isinstance(item,Case)):
                # print("yes")
                temp_right = self.visit(item.expr)
                case=self.name_list.pop()
                print(f"if ({name} == {case})")
                print(f"goto {case_labels[i]};")
                temp_equal=c_ast.BinaryOp(op="==",left=temp,right=temp_right)
                self.flat_block_items.append(c_ast.If(cond=temp_equal, iftrue=self.get_goto(case_labels[i]), iffalse=None))
            # if (isinstance(item,Break)):
            #     print(f"goto {label_end};")
        for i in range(num_case):
            item=node.stmt.block_items[i]
            print(f"{case_labels[i]}:1;")
            self.flat_block_items.append(self.get_label(case_labels[i]))
            for s in item.stmts:
                self.visit(s)
        print(f"{label_end}:1;")
        self.flat_block_items.append(self.get_label(label_end))
        self.quit_switch()

    def visit_For(self,node):
        #init
        self.visit(node.init)
        start_label = self.generate_label()
        end_label = self.generate_label()
        label2 = self.generate_label()
        print(f"{start_label}:1;")
        self.flat_block_items.append(self.get_label(start_label))

        self.enter_loop(start_label,end_label)
        #cond
        # if(isinstance(node.cond,BinaryOp)):

        temp_cond=self.visit(node.cond)
        res=self.name_list.pop()
        print(f"if ({res})")
        print(f"goto {label2};")
        self.flat_block_items.append(c_ast.If(cond=temp_cond, iftrue=self.get_goto(label2), iffalse=None))
        print(f"goto {end_label};")
        self.flat_block_items.append(self.get_goto(end_label))
        print(f"{label2}:1;")
        self.flat_block_items.append(self.get_label(label2))
        #stmt
        self.visit(node.stmt)
        #next
        self.visit(node.next)
        #end
        print(f"goto {start_label};")
        self.flat_block_items.append(self.get_goto(start_label))
        print(f"{end_label}:1;")
        self.flat_block_items.append(self.get_label(end_label))
        self.quit_loop()

    def visit_ArrayRef(self,node):
        temp_name=self.visit(node.name)
        name=self.name_list.pop()
        temp_id=self.visit(node.subscript)
        num=self.name_list.pop()
        temp=self.generate_temp()
        real_temp=self.get_id(temp)
        print(f"{temp} = {name} + {num};")
        self.flat_block_items.append(c_ast.Assignment(op="=",lvalue=real_temp,rvalue=c_ast.BinaryOp(op="+",left=temp_name,right=temp_id)))
        temp2 = self.generate_temp()
        real_temp2=self.get_id(temp2)
        print(f"{temp2} = *{temp};")
        self.flat_block_items.append(c_ast.Assignment(op="=",lvalue=real_temp2,rvalue=c_ast.UnaryOp(op="*",expr=real_temp)))
        # return temp2
        self.name_list.append(temp2)
        return real_temp2

    def visit_Break(self,node):
        label=self.get_break()
        print(f"goto {label};")
        self.flat_block_items.append(self.get_goto(label))

    def visit_Continue(self, node):
        label = self.get_continue()
        print(f"goto {label};")
        self.flat_block_items.append(self.get_goto(label))
    def visit_Return(self, node):
        res=self.visit(node.expr)
        res=self.name_list.pop()
        print(f"return {res};")



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

    # with open(output_path, 'w', encoding='utf-8') as file:
    #     # 保存当前的stdout
    #     original_stdout = sys.stdout
    #     try:
    #         # 将stdout重定向到文件
    #         sys.stdout = file
    #
    #         # 现在使用print将文本写入文件应该不会引发错误
    #         generator = Generator()
    #         generator.visit(ast)
    #         # 更多的print调用...
    #
    #     finally:
    #         # 恢复原始的stdout，确保后续的print调用正常输出到控制台
    #         sys.stdout = original_stdout

    generator = Generator()
    new_ast=generator.visit(ast)
    print("---------------------")
    ast_dict=ast_to_dict(new_ast)
    with open("aaaaaaaaaaa_my_new_ast.json", 'w') as output_file:
        json.dump(ast_dict, output_file, indent=2)
    # 打印AST
    # ast.show()
    new_generator = c_generator.CGenerator()
    print(new_generator.visit(new_ast))





if __name__ == '__main__':
    main()
