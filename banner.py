import sys


def colored(text, color_code, style=None):
    """使用ANSI转义序列为文本添加颜色和样式"""
    if sys.platform.startswith('win'):
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

    # 基础颜色代码
    code = color_code

    # 添加样式代码（如果有）
    if style:
        styles = {
            'bold': '1',
            'underline': '4',
            'blink': '5',
            'reverse': '7'
        }
        code = f"{styles.get(style, '')};{code}" if styles.get(style) else code

    return f"\033[{code}m{text}\033[0m"


# 梅花鹿颜色配置
DEER_BODY = '38;5;39'  # 主体蓝色
DEER_ACCENT = '38;5;33'  # 辅助蓝色
SPOT_COLOR = '38;5;196'  # 梅花红色
ACCENT_COLOR = '38;5;166'  # 强调色
WHITE = '38;5;255'  # 白色
DARK = '38;5;240'  # 深色

# 梅花鹿ASCII艺术图案（优化颜色覆盖）
deer_art = fr'''
    {colored('                            .-"`  `"-.', DEER_BODY)}
    {colored('                          /`          `\\', DEER_BODY)}
    {colored('                        /                \\', DEER_BODY)}
    {colored('                  .-.,_|      .-""""-. |', DEER_ACCENT)}  
    {colored('                  |     `",_,-\'   (((-. \'(', DEER_ACCENT)}  
    {colored('                   \\ (`"=._.\'/   ( ' + colored('o', SPOT_COLOR) + '"', DEER_ACCENT)} 
    {colored('        ,           \'.`"-'' /     `--`   \'==;', ACCENT_COLOR)}
    {colored('       /\\\\            `\'--''\\         _.\'~~', ACCENT_COLOR)}
    {colored('      / | \\                  `.,___,-}', DEER_BODY)}
    {colored('      | |  |                       )  {  }', DEER_BODY)}
    {colored('       \\ \\ (.--==---==---=\' o {  }', DEER_BODY)}
    {colored('        ",/` (_) (_)  (_)  (_)   \\/', DEER_BODY)}
    {colored('         / (' + colored(')', SPOT_COLOR) + '   ' + colored('o', SPOT_COLOR) + '   (' + colored(')', SPOT_COLOR) + '    (' + colored(')', SPOT_COLOR) + '         ^' + colored('|', WHITE), ACCENT_COLOR)}
    {colored('         \\   (' + colored(')', SPOT_COLOR) + '  (    (' + colored(')', SPOT_COLOR) + ' ' + colored('o', SPOT_COLOR) + '        ;   /', DEER_BODY)}
    {colored('          `\\      \\         ;    / }}   |', DEER_BODY)}
    {colored('            )      \\       /   /`  }}  /', DEER_BODY)}
    {colored('         ,-\'       |=,_   |   /,_ ,/', DEER_BODY)}
    {colored('         |    _,.-`/   `"=\\   \\\\   \\', DEER_BODY)}
    {colored('         | ."` \\  |          \\   \\`\\  \\', DEER_BODY)}
    {colored('         | |    \\ \\           `\\  \\ `\\ \\', DEER_BODY)}
    {colored('         | |     \\ \\            `\\ \\  \\ \\', DEER_BODY)}
    {colored('         | |      \\ \\             \\ \\  \\ \\', DEER_BODY)}
    {colored('         | |       \\ \\             \\ \\  \\ \\', DEER_BODY)}
    {colored('         | |        \\ \\             \\ \\  \\ \\', DEER_BODY)}
    {colored('         | |         ) \\             \\ \\  ) \\', DEER_BODY)}
'''


# 美化标识部分（优化代码结构）
def print_signature():
    border = colored('╔═══════════════════════════════════════════════╗', '38;5;208')
    author_line = colored('║', '38;5;208') + '  ' + colored('Author:', '38;5;46', 'bold') + '    ' + colored('Bifish',
                                                                                                             '38;5;39') + ' ' * 28 + colored(
        '║', '38;5;208')
    github_line = colored('║', '38;5;208') + '  ' + colored('GitHub:', '38;5;46', 'bold') + '    ' + colored(
        'https://github.com/Bifishone', '38;5;39') + ' ' * 8 + colored('║', '38;5;208')
    script_line = colored('║', '38;5;208') + '  ' + colored('Shell Script:', '38;5;46', 'bold') + '  ' + colored(
        'GoogleFirefoxURL.py', '38;5;39') + ' ' * 11+ colored('║', '38;5;208')
    bottom_border = colored('╚═══════════════════════════════════════════════╝', '38;5;208')

    print(border)
    print(author_line)
    print(github_line)
    print(script_line)
    print(bottom_border)


# 打印完整内容
print(deer_art)

print_signature()
