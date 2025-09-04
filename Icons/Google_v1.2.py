# 定义每个字母的像素轮廓（逐行绘制，严格对齐）
letters = {
    'G': [
        "  █████  ",
        " █     █ ",
        " █     █ ",
        " █  ███  ",
        " █     █ ",
        " █     █ ",
        "  █████  "
    ],
    'o': [
        "  ████  ",
        " █    █ ",
        " █    █ ",
        " █    █ ",
        " █    █ ",
        " █    █ ",
        "  ████  "
    ],
    'g': [
        "  ████  ",
        " █    █ ",
        " █    █ ",
        " █  ███ ",
        " █    █ ",
        " █  █   ",
        "  ████  "
    ],
    'l': [
        " █      ",
        " █      ",
        " █      ",
        " █      ",
        " █      ",
        " █      ",
        " █████  "
    ],
    'e': [
        "  ████  ",
        " █    █ ",
        " █      ",
        "  ████  ",
        " █      ",
        " █    █ ",
        "  ████  "
    ]
}

# 定义ANSI颜色代码
colors = {
    'G': '\033[94m',  # 蓝色
    'o1': '\033[91m',  # 第一个 o 红色
    'o2': '\033[93m',  # 第二个 o 黄色
    'g': '\033[94m',  # 蓝色
    'l': '\033[92m',  # 绿色
    'e': '\033[91m'  # 红色
}


def print_colored_google():
    # 字母顺序
    sequence = ['G', 'o1', 'o2', 'g', 'l', 'e']

    # 逐行打印（共7行）
    for row in range(7):
        line = ""
        for char in sequence:
            # 获取字母的轮廓
            if char == 'o1' or char == 'o2':
                letter = letters['o'][row]
            else:
                letter = letters[char][row]

            # 添加颜色
            line += f"{colors[char]}{letter}{'\033[0m'}  "

        print(line)


if __name__ == "__main__":
    print_colored_google()