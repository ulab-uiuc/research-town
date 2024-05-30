import subprocess

def run_test():
    # 使用 subprocess.run 来运行命令
    result = subprocess.run(['pytest', '--pdb', 'tests.test_db_base'], capture_output=True, text=True)

    # 打印输出和错误信息
    print("Output:")
    print(result.stdout)
    print("Errors:")
    print(result.stderr)

    # 检查命令是否成功执行
    if result.returncode == 0:
        print("Tests ran successfully!")
    else:
        print("Tests failed.")

if __name__ == "__main__":
    run_test()
