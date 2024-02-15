import argparse
from pycparser import parse_file, c_generator, c_ast, c_parser
from pycparser.c_ast import *
from pycparser.c_generator import CGenerator


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


    def reset(self):
        self.braces = [] #大括号
        self.tempId = 0 #临时var的计数器
        self.binaryVar = [] #临时var
        self.unaryVar = [] #unary操作推进去的var name
        self.ids = []  #ID 的name
        self.constants = []  #常数的value
        # -------------------------

    def generate_temp(self):
        temp_name = f"temp{self.tempId}"
        self.tempId += 1
        return temp_name
    def generate_label(self):
        label_name = f"label{self.labelId}"
        self.labelId += 1
        # print(f"goto {label_name};")
        # self.labels.append(label_name)
        return label_name
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
            if isinstance(i, Decl):
                # out.append(i)
                print("declare bug 1")
            else:
                self.visit(i)
            self.reset()

    def visit_FuncDef(self, node):
        # 首先处理函数定义的其他部分，比如函数声明等
        # ...
        self.visit(node.decl)
        # 然后找到并访问Compound节点
        if isinstance(node.body, c_ast.Compound):
            self.visit(node.body) # visit compound
        print("}")
        # out = []
        # for i in node.decl.type.args.params:
        #     self.visit(i)
        # out = self.visit(node.body)
        # decl = []
        # oth = []
        # for i in out:
        #     if isinstance(i, Decl):
        #         decl.append(i)
        #     else:
        #         oth.append(i)
        # decl.extend(oth)
        # node = c_ast.FuncDef(node.decl, node.param_decls, Compound(decl))
        # return node
    def visit_FuncDecl(self, node):
        generator = c_generator.CGenerator()
        func_decl_code = generator.visit(node)
        print(func_decl_code)
        print("{")


    def visit_Compound(self, node):
        # 在这里处理Compound节点
        # 遍历Compound节点中的所有语句和声明
        for item in node.block_items:
            self.visit(item)

        # out = []
        # for n in node:
        #     tmp = self.visit(n)
        #
        #     if tmp is not None:
        #         out.extend(tmp)
        #     while len(self.unary):
        #         out.append(self.unary.pop())
        # node = Compound(out)
        # return node
    def visit_Assignment(self, node):
        # # 获取被赋值的变量名
        # variable_name = node.lvalue.name
        #
        # # 获取赋值表达式的值
        # # 这里假设值是一个简单的常量，对于更复杂的表达式，可能需要更复杂的处理
        # value = node.rvalue.value
        #
        # # 打印赋值语句
        # print(f"{variable_name} = {value};")

        # if isinstance(node.lvalue, ArrayRef): # 假设左值是一个列表
        #     self.visit(node.lvalue)
        #     # lvalue_str = f'{self.ls.pop()}'
        # else:
        left = self.visit(node.lvalue)  # 假设左值是一个简单的标识符
        right = self.visit(node.rvalue)

        # 打印三地址代码
        print(f"{left} = {right};")
    def visit_ExprList(self, node):
        name_list=[]
        if node.exprs:
            for expr in node.exprs:
                name_list.append(expr.value)
        return name_list
    def visit_FuncCall(self,node):
        name=self.visit(node.name)
        func_call_str = f"{name}()"

        # 检查是否存在参数
        if node.args:
            # 访问参数节点并获取包含所有参数的字符串列表
            args = self.visit(node.args)

            # 将参数列表转换为字符串，参数之间用逗号和空格分隔
            args_str = ', '.join(args)

            # 使用参数字符串更新func_call_str
            func_call_str = f"{name}({args_str})"

        # 返回完整的函数调用字符串
        temp=self.generate_temp()
        print(f"{temp}={func_call_str}")
        return temp


    def visit_TypeDecl(self,node):
        name = node.declname
        type_list = node.type.names
        print(f"{' '.join(type_list)} {name}")
        return name

    def visit_Decl(self, node):
        name="unknown 34254"
        if node.type:
            name=self.visit(node.type)
        if node.init:
            right=self.visit(node.init)
            print(f"{name} = {right};")
        # print(f"{type}")


        # # 生成并打印3AC
        # if init_str:  # 如果存在初始化表达式
        #     print(f"{type_str} {node.name} = {init_str};")
        # else:  # 仅声明，无初始化
        #     print(f"{type_str} {node.name};")

    def visit_UnaryOp(self, node):
        res="visit_UnaryOp res"
        # 获取表达式的字符串表示
        if node.expr:
            name=self.visit(node.expr)
        else:
            print("todo 4231")
            return

        if node.op == '++':
            # 前置自增
            print(f"{name} = {name} + 1;")
            res=name
        elif node.op == 'p++':
            # 如果是后置自增，使用临时变量保存原始值
            res = self.generate_temp()
            print(f"{res} = {name};")
            print(f"{name} = {name} + 1;")
        elif node.op in '--':
            # 前置自减
            print(f"{name} = {name} - 1;")
            res=name
        elif node.op == 'p--':
            # 如果是后置自减，使用临时变量保存原始值
            res = self.generate_temp()
            print(f"{res} = {name};")
            print(f"{name} = {name} - 1;")
        else:
            print("unkbown unary op")
        return res

    def visit_BinaryOp(self, node):
        right_name = ""
        left_name = ""
        # 处理左侧表达式
        left_name = self.visit(node.left)
        # 处理右侧表达式
        right_name = self.visit(node.right)


        # 打印二元操作的3AC
        result_name = self.generate_temp()
        print(f"{result_name} = {left_name} {node.op} {right_name};")
        return result_name

    def visit_ID(self, node):
        return node.name

    def visit_Constant(self, node):
        # 打印Constant节点的类型和值
        return node.value



    def visit_If(self, node):
        label0 = self.generate_label()
        label1 = self.generate_label()
        label2 = self.generate_label()
        if(isinstance(node.cond,BinaryOp)):
            self.visit(node.cond)
            resName=self.binaryVar.pop()
            print(f"if ({resName})  goto {label0};")
            print(f"goto {label1};")
        if(node.iftrue):
            print(f"{label0}:")
            self.visit(node.iftrue)
            print(f"goto {label2};")
        if(node.iffalse):
            print(f"{label1}:")
            self.visit(node.iffalse)
            print(f"{label2}:")
    def visit_Switch(self,node):
        #拿到 case 的对象 i
        self.visit(node.cond)
        name = self.ids.pop()
        # 拿到 case 的数量
        num_case=len(node.stmt.block_items)
        # print(num_case)
        # print(name)
        label_end=self.generate_label()
        # 对每一个 case
        case_labels=[]
        for i in range(num_case):
            case_labels.append(self.generate_label())
        for i in range(num_case):
            item=node.stmt.block_items[i]

            if (isinstance(item,Case)):
                # print("yes")
                self.visit(item.expr)
                case=self.constants.pop()
                print(f"if ({name} == {case})")
                print(f"goto {case_labels[i]};")
            # if (isinstance(item,Break)):
            #     print(f"goto {label_end};")
        for i in range(num_case):
            item=node.stmt.block_items[i]
            print(f"{case_labels[i]}:")
            if (isinstance(item, Case)):
                for s in item.stmts:
                    self.visit(s)
                    if(isinstance(s,Break)):
                        print(f"goto {label_end};")
            if(isinstance(item, Default)):
                for s in item.stmts:
                    self.visit(s)
        print(f"{label_end}:")

    def visit_For(self,node):
        #init
        self.visit(node.init)
        label0 = self.generate_label()
        label1 = self.generate_label()
        label2 = self.generate_label()
        print(f"{label0}:")
        #cond
        if(isinstance(node.cond,BinaryOp)):

            res=self.visit(node.cond)
            print(f"if ({res})")
        print(f"goto {label2};")
        print(f"goto {label1};")
        print(f"{label2}:")
        #stmt
        self.visit(node.stmt)
        #next
        self.visit(node.next)
        #end
        print(f"goto {label0};")
        print(f"{label1}:")











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
