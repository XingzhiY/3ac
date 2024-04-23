import sys

# 打开一个文件用于写入，显式指定使用utf-8编码
with open('output.txt', 'w', encoding='utf-8') as file:
    # 保存当前的stdout
    original_stdout = sys.stdout
    try:
        # 将stdout重定向到文件
        sys.stdout = file

        # 现在使用print将文本写入文件应该不会引发错误
        print("这将写入到文件中")
        # 更多的print调用...

    finally:
        # 恢复原始的stdout，确保后续的print调用正常输出到控制台
        sys.stdout = original_stdout

# 测试：这将正常打印到控制台
print("这将显示在控制台")
