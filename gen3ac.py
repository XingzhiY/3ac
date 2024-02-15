import argparse
from pycparser import parse_file, c_generator, c_ast, c_parser
from pycparser.c_ast import *
from pycparser.c_generator import CGenerator


class Generator(c_ast.NodeVisitor):
    def __init__(self):
        self.braces = [] #大括号
        self.tempId = 0 #临时var的计数器
        self.temps = [] #临时var
        self.unaryVar = [] #unary操作推进去的var name
        self.ids = []  #ID 的name
        self.constants = []  #常数的value
        self.labelId=0 #label 的 id
        self.labels=[] #label列表，都要消耗掉
        self.cond_labels=[] #cond产生的label
        # -------------------------
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

    def reset(self):
        self.braces = [] #大括号
        self.tempId = 0 #临时var的计数器
        self.temps = [] #临时var
        self.unaryVar = [] #unary操作推进去的var name
        self.ids = []  #ID 的name
        self.constants = []  #常数的value
        # -------------------------
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
        print(self.braces.pop())
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

        self.braces.append("}")

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

        if isinstance(node.lvalue, ArrayRef): # 假设左值是一个列表
            self.visit(node.lvalue)
            lvalue_str = f'{self.ls.pop()}'
        else:
            lvalue_str = node.lvalue.name  # 假设左值是一个简单的标识符

        # 处理右值
        if isinstance(node.rvalue, BinaryOp):
            self.visit(node.rvalue)
            rvalue_str = f'temp{len(self.ls)}'
        elif isinstance(node.rvalue, UnaryOp):
            self.visit(node.rvalue)
            rvalue_str = f'temp{len(self.una)}'
        elif isinstance(node.rvalue, ArrayRef):
            self.visit(node.rvalue)
            rvalue_str = f'temp{len(self.ls)}'
        else:
            rvalue_str = node.rvalue.value  # 假设右值是一个简单的常量

        # 打印三地址代码
        print(f"{lvalue_str} = {rvalue_str};")

    def visit_Decl(self, node):
        name=""
        # 检查声明的类型
        if isinstance(node.type, c_ast.TypeDecl):
            name=node.type.declname
            type_list=node.type.type.names
            print(f"{' '.join(type_list)} {name}")
        elif isinstance(node.type, c_ast.ArrayDecl) or isinstance(node.type, c_ast.PtrDecl) :
            print("todo ArrayDecl PtrDecl")
            return
        elif isinstance(node.type, c_ast.FuncDecl):
            self.visit(node.type)
            return

        # 检查并处理初始化表达式
        if isinstance(node.init, (BinaryOp, UnaryOp, ArrayRef)):
            self.visit(node.init)  # 访问初始化表达式以处理内部结构
            init_str = f'temp_var'  # 假设这是之前处理表达式时生成的临时变量名称
        elif isinstance(node.init, Constant):
            value = node.init.value  # 常量初始化
            print(f"{name} = {value}")
        else:
            init_str = ''

        # # 生成并打印3AC
        # if init_str:  # 如果存在初始化表达式
        #     print(f"{type_str} {node.name} = {init_str};")
        # else:  # 仅声明，无初始化
        #     print(f"{type_str} {node.name};")

    def visit_UnaryOp(self, node):
        # 获取表达式的字符串表示
        if isinstance(node.expr, ID):
            expr_str = node.expr.name
        elif isinstance(node.expr, Constant):
            expr_str = node.expr.value
        else:
            # 对于更复杂的表达式，生成临时变量
            self.visit(node.expr)  # 先处理表达式
            print("unknow expr")

        if node.op in ['p++', '++']:
            # 前置自增
            print(f"{expr_str} = {expr_str} + 1;")
        elif node.op == 'p++':
            # 如果是后置自增，使用临时变量保存原始值
            temp = self.generate_temp()
            print(f"{temp} = {expr_str} - 1;  // {temp} holds the original value of {expr_str}")
        elif node.op in ['p--', '--']:
            # 前置自减
            print(f"{expr_str} = {expr_str} - 1;")
        elif node.op == 'p--':
            # 如果是后置自减，使用临时变量保存原始值
            temp = self.generate_temp()
            print(f"{temp} = {expr_str} + 1;  // {temp} holds the original value of {expr_str}")
        else:
            # 处理其他一元操作
            temp = self.generate_temp()
            print("unkbown unary op")
            # print(f"{temp} = {node.op}{expr_str})

    def visit_BinaryOp(self, node):
        right_name = ""
        left_name = ""
        # 处理左侧表达式
        if isinstance(node.left, BinaryOp):
            self.visit(node.left)
            left_name = self.temps.pop()
        elif isinstance(node.left, UnaryOp):
            self.visit(node.left)
            left_name = self.unaryVar.pop()
        elif isinstance(node.left, ArrayRef):
            print("unknow??好的，好好的ArrayRef ")
        elif isinstance(node.left,ID):
            self.visit(node.left)
            left_name = self.ids.pop()
        elif isinstance(node.left, Constant):
            self.visit(node.left)
            left_name = self.constants.pop()


        # 处理右侧表达式
        if isinstance(node.right, BinaryOp):
            self.visit(node.right)
            right_name = self.temps.pop()
        elif isinstance(node.right, UnaryOp):
            self.visit(node.right)
            right_name = self.unaryVar.pop()
        elif isinstance(node.right, ArrayRef):
            print("unknow??好的，好好的ArrayRef ")
        elif isinstance(node.right,ID):
            self.visit(node.right)
            right_name = self.ids.pop()
        elif isinstance(node.right, Constant):
            self.visit(node.right)
            right_name = self.constants.pop()


        # 打印二元操作的3AC
        result_name = self.generate_temp()
        self.temps.append(result_name)
        print(f"{result_name} = {left_name} {node.op} {right_name};")

    def visit_ID(self, node):
        self.ids.append(node.name)

    def visit_Constant(self, node):
        # 打印Constant节点的类型和值
        self.constants.append(node.value)



    def visit_If(self, node):
        label0 = self.generate_label()
        label1 = self.generate_label()
        label2 = self.generate_label()
        if(isinstance(node.cond,BinaryOp)):
            self.visit(node.cond)
            resName=self.temps.pop()
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
