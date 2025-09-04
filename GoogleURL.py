import time
import re
import os
import sys
import random
import tldextract
from colorama import init, Fore, Style
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException
)
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr

# 初始化彩色输出
init(autoreset=True)

# 默认过滤列表（可通过环境变量或配置文件扩展）
DEFAULT_FILTERS = ['google.com', 'googleadservices.com', 'googletagmanager.com']

# 文档文件扩展名列表
DOCUMENT_EXTS = ['.pdf', '.docx', '.doc', '.rar', '.inc', '.txt', '.sql', '.conf', '.xlsx', '.xls', '.csv', '.ppt',
                 '.pptx']

# 定义每个字母的像素轮廓（逐行绘制，严格对齐）
LETTERS = {
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
COLORS = {
    'G': '\033[94m',  # 蓝色
    'o1': '\033[91m',  # 第一个 o 红色
    'o2': '\033[93m',  # 第二个 o 黄色
    'g': '\033[94m',  # 蓝色
    'l': '\033[92m',  # 绿色
    'e': '\033[91m'  # 红色
}


def print_banner():
    """打印程序横幅（保持原始图案不变）"""
    # 字母顺序
    sequence = ['G', 'o1', 'o2', 'g', 'l', 'e']

    # 逐行打印（共7行）
    for row in range(7):
        line = ""
        for char in sequence:
            # 获取字母的轮廓
            if char == 'o1' or char == 'o2':
                letter = LETTERS['o'][row]
            else:
                letter = LETTERS[char][row]

            # 添加颜色
            line += f"{COLORS[char]}{letter}{'\033[0m'}  "

        print(line)

    print(Fore.GREEN + "=" * 60)
    print(Fore.GREEN + "  Google URL Search - v1.0")
    print(Fore.GREEN + "=" * 60)
    print(Style.RESET_ALL)


def check_environment():
    """检查运行环境"""
    print(Fore.YELLOW + "[+] 检查运行环境...")

    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
        print(Fore.RED + f"[-] 请使用Python 3.7或更高版本 (当前: {sys.version.split()[0]})")
        return False

    # 检查依赖库安装
    required_libraries = {
        'selenium': 'pip install selenium',
        'tldextract': 'pip install tldextract',
        'colorama': 'pip install colorama'
    }
    for library, install_command in required_libraries.items():
        try:
            __import__(library)
            import importlib
            version = importlib.import_module(library).__version__
            print(Fore.GREEN + f"[✓] {library}已安装 (版本: {version})")
        except ImportError:
            print(Fore.RED + f"[-] 未找到{library}库，请运行: {install_command}")
            return False

    return True


def find_chromedriver():
    """查找ChromeDriver可执行文件"""
    print(Fore.YELLOW + "[+] 查找ChromeDriver...")

    # 检查系统PATH
    from shutil import which
    if which("chromedriver"):
        print(Fore.GREEN + "[✓] 在系统PATH中找到ChromeDriver")
        return which("chromedriver")

    # 检查当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    chromedriver_exe = os.path.join(current_dir, "chromedriver.exe" if os.name == 'nt' else "chromedriver")

    if os.path.exists(chromedriver_exe):
        print(Fore.GREEN + f"[✓] 在当前目录找到ChromeDriver: {chromedriver_exe}")
        return chromedriver_exe

    print(Fore.RED + "[-] 未找到ChromeDriver")
    print(Fore.YELLOW + "[*] 请从https://sites.google.com/chromium.org/driver/下载对应版本")
    print(Fore.YELLOW + "[*] 并将chromedriver.exe放在脚本同一目录或系统PATH中")
    return None


def setup_driver(proxy=None):
    """配置并启动浏览器驱动（增强反检测能力）"""
    print(Fore.YELLOW + "[+] 准备启动浏览器...")

    # 查找ChromeDriver
    chromedriver_path = find_chromedriver()
    if not chromedriver_path:
        raise FileNotFoundError("未找到ChromeDriver")

    options = webdriver.ChromeOptions()

    # 增强反检测参数
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-notifications")
    options.add_argument("--window-size=1920,1080")

    # 设置随机User-Agent
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")

    # 设置代理
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")
        print(Fore.YELLOW + f"[+] 使用代理: {proxy}")

    # 创建浏览器实例
    try:
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        print(Fore.GREEN + f"[✓] 浏览器已成功启动")

        # 添加额外的JavaScript隐藏自动化特征
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                window.chrome = {
                    runtime: {},
                };
            """
        })

        return driver
    except WebDriverException as e:
        print(Fore.RED + f"[-] 启动浏览器时出错: {str(e)}")
        print(Fore.RED + "[-] 请确保ChromeDriver版本与您的Chrome浏览器版本兼容")
        raise


def check_for_captcha(driver):
    """检查页面是否存在验证码"""
    captcha_elements = [
        '//div[@class="g-recaptcha"]',
        '//iframe[contains(@src, "recaptcha")]',
        '//input[@id="captcha"]',
        '//div[contains(text(), "验证")]',
        '//div[contains(text(), "captcha")]',
        '//div[contains(text(), "are you a robot")]'
    ]

    for xpath in captcha_elements:
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            print(Fore.RED + "[!] 检测到验证码！")
            return True
        except TimeoutException:
            continue

    return False


def handle_captcha(driver, max_attempts=3):
    """处理验证码"""
    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        print(Fore.YELLOW + f"[+] 尝试处理验证码 ({attempts}/{max_attempts})...")

        # 人工干预方式
        print(Fore.YELLOW + "[!] 需要人工干预：")
        print(Fore.YELLOW + "[!] 1. 请在打开的浏览器中完成验证码")
        print(Fore.YELLOW + "[!] 2. 完成后按回车键继续")
        print(Fore.YELLOW + "[!] 3. 如无法完成，请按 Ctrl+C 终止程序")

        # 等待用户输入
        input("[*] 按回车键继续...")

        # 再次检查验证码是否还存在
        if not check_for_captcha(driver):
            print(Fore.GREEN + "[✓] 验证码已成功处理")
            return True

        print(Fore.RED + "[-] 验证码仍然存在，请重试")

    print(Fore.RED + "[!] 验证码处理失败，达到最大尝试次数")
    return False


def get_url_ext(url):
    """获取URL的文件扩展名"""
    # 处理可能包含查询参数的URL
    path = url.split('?')[0].split('#')[0]
    return os.path.splitext(path)[1].lower()


def should_filter_url(url, target_domain, filters=DEFAULT_FILTERS):
    """判断URL是否应该被过滤"""
    # 排除包含过滤关键词的URL
    for filter_domain in filters:
        if filter_domain in url:
            return True

    # 确保URL包含目标域名（可选增强逻辑）
    if target_domain and target_domain not in url:
        return True

    return False


def extract_urls(driver, query, max_possible_pages=100):
    """爬取所有可访问页面中的URL，并应用过滤规则"""
    base_domain = query.split(":")[1] if ":" in query else query
    regular_urls = set()  # 普通URL
    document_urls = {ext: set() for ext in DOCUMENT_EXTS}  # 按扩展名分类的文档URL
    retry_count = 0
    max_retries = 3
    timeout_count = 0
    max_timeout_count = 9  # 连续超时次数上限
    filtered_count = 0  # 记录过滤掉的URL数量

    print(Fore.YELLOW + f"[+] 使用过滤规则: {', '.join(DEFAULT_FILTERS)}")
    print(Fore.YELLOW + f"[+] 文档类型检测: {', '.join(DOCUMENT_EXTS)}")

    while retry_count < max_retries:
        try:
            search_url = f"https://www.google.com/search?q={query}"
            driver.get(search_url)
            print(Fore.YELLOW + f"[+] 访问搜索页面: {search_url}")

            # 等待页面加载完成
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href]'))
                )
                timeout_count = 0  # 页面加载成功，重置超时计数器
            except TimeoutException:
                # 页面加载超时，可能遇到验证码
                print(Fore.RED + "[-] 页面加载超时，检查是否遇到验证码...")
                if check_for_captcha(driver):
                    if not handle_captcha(driver):
                        print(Fore.RED + "[!] 验证码处理失败，跳过当前域名")
                        return regular_urls, document_urls
                    else:
                        # 重新加载页面
                        driver.get(search_url)
                        WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href]'))
                        )
                else:
                    print(Fore.RED + "[-] 页面加载超时，但未检测到验证码")
                    timeout_count += 1
                    if timeout_count >= max_timeout_count:
                        print(Fore.YELLOW + "[*] 连续多次页面加载超时，停止爬取")
                        return regular_urls, document_urls

            current_page = 1
            has_more_pages = True

            while has_more_pages and current_page <= max_possible_pages:
                print(Fore.YELLOW + f"\n[+] 正在处理第 {current_page} 页...")

                try:
                    # 尝试提取链接
                    links = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[href]'))
                    )

                    if not links:
                        # 没有找到链接，可能遇到验证码
                        print(Fore.RED + "[-] 未找到搜索结果链接，检查是否遇到验证码...")
                        if check_for_captcha(driver):
                            if not handle_captcha(driver):
                                print(Fore.RED + "[!] 验证码处理失败，停止爬取当前域名")
                                has_more_pages = False
                                break
                            else:
                                # 刷新页面重新尝试
                                driver.refresh()
                                WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href]'))
                                )
                                continue
                        else:
                            print(Fore.RED + "[-] 未找到链接，但未检测到验证码")
                            break

                    print(Fore.YELLOW + f"[*] 找到 {len(links)} 个链接")

                    page_regular_urls = set()
                    page_document_urls = {ext: set() for ext in DOCUMENT_EXTS}
                    page_filtered = 0

                    for i, link in enumerate(links, 1):
                        try:
                            href = link.get_attribute('href')
                            if href and 'http' in href:
                                # 应用过滤规则
                                if should_filter_url(href, base_domain):
                                    page_filtered += 1
                                    continue

                                # 检查是否为文档文件
                                ext = get_url_ext(href)
                                if ext in DOCUMENT_EXTS:
                                    if href not in document_urls[ext]:
                                        page_document_urls[ext].add(href)
                                        print(Fore.BLUE + f"[✓] 找到文档URL ({ext}): {href}")
                                    continue

                                # 普通URL处理
                                if href not in regular_urls:
                                    page_regular_urls.add(href)
                                    print(Fore.GREEN + f"[✓] 找到普通URL ({i}/{len(links)}): {href}")
                        except Exception as e:
                            print(Fore.RED + f"[-] 提取链接时出错: {str(e)}")

                    # 合并URL并去重
                    new_regular_urls = page_regular_urls - regular_urls
                    regular_urls.update(new_regular_urls)

                    for ext in DOCUMENT_EXTS:
                        new_docs = page_document_urls[ext] - document_urls[ext]
                        document_urls[ext].update(new_docs)

                    filtered_count += page_filtered

                    # 计算文档URL总数
                    page_doc_count = sum(len(urls) for urls in page_document_urls.values())
                    total_doc_count = sum(len(urls) for urls in document_urls.values())

                    print(
                        Fore.YELLOW + f"[*] 本页新增 {len(new_regular_urls)} 个普通URL，{page_doc_count} 个文档URL，过滤 {page_filtered} 个")
                    print(
                        Fore.YELLOW + f"[*] 累计: {len(regular_urls)} 个普通URL | {total_doc_count} 个文档URL | 总过滤: {filtered_count}")

                    # 尝试翻页
                    try:
                        # 查找下一页按钮
                        next_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.ID, 'pnnext'))
                        )
                        # 滚动到按钮并点击
                        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                        time.sleep(1)
                        next_button.click()

                        # 随机延迟
                        delay = 4 + random.uniform(1, 3)
                        print(Fore.YELLOW + f"[*] 等待 {delay:.1f} 秒后加载下一页...")
                        time.sleep(delay)

                        # 检查翻页后是否能正常加载内容
                        try:
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href]'))
                            )
                        except TimeoutException:
                            # 翻页后内容未加载，可能遇到验证码
                            print(Fore.RED + "[-] 翻页后内容加载超时，检查是否遇到验证码...")
                            if check_for_captcha(driver):
                                if not handle_captcha(driver):
                                    print(Fore.RED + "[!] 验证码处理失败，停止爬取当前域名")
                                    has_more_pages = False
                                    break
                                else:
                                    # 刷新页面重新尝试
                                    driver.refresh()
                                    WebDriverWait(driver, 10).until(
                                        EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href]'))
                                    )
                            else:
                                print(Fore.RED + "[-] 翻页后内容加载超时，但未检测到验证码")
                                break

                        current_page += 1

                    except (NoSuchElementException, TimeoutException):
                        # 无下一页按钮，结束爬取
                        print(Fore.YELLOW + "[*] 未找到更多页面，爬取结束")
                        has_more_pages = False

                except Exception as e:
                    print(Fore.RED + f"[-] 处理页面时出错: {str(e)}")
                    # 检查是否遇到验证码
                    if check_for_captcha(driver):
                        if not handle_captcha(driver):
                            print(Fore.RED + "[!] 验证码处理失败，停止爬取当前域名")
                            has_more_pages = False
                            break
                    else:
                        print(Fore.RED + "[-] 处理页面时出错，但未检测到验证码")
                        has_more_pages = False
                        break

            # 所有页面处理完成
            print(Fore.GREEN + f"[✓] 已完成所有可访问页面的爬取（共 {current_page - 1} 页）")
            print(Fore.YELLOW + f"[*] 总共过滤掉 {filtered_count} 个URL")
            break

        except WebDriverException as e:
            if "invalid session id" in str(e) and retry_count < max_retries:
                print(Fore.RED + f"[-] 会话中断，第 {retry_count + 1}/{max_retries} 次重试...")
                retry_count += 1
                time.sleep(5)
            else:
                print(Fore.RED + f"[-] 致命错误: {str(e)}")
                break

    return regular_urls, document_urls


def save_results(regular_urls, document_urls, base_domain):
    """保存结果到文件"""
    results_saved = False
    documents_saved = False
    # 创建results文件夹
    results_dir = "results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    # 创建域名对应的文件夹
    domain_dir = os.path.join(results_dir, base_domain)
    if not os.path.exists(domain_dir):
        os.makedirs(domain_dir)
    # 保存普通URL
    if regular_urls:
        regular_file = os.path.join(domain_dir, f"Google_URLs_{base_domain}.txt")
        with open(regular_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sorted(regular_urls)))
        print(Fore.GREEN + f"[✓] 普通URL保存至: {regular_file}")
        results_saved = True
    # 计算文档URL总数
    total_documents = sum(len(urls) for urls in document_urls.values())
    # 如果有文档URL，创建文档文件夹并保存
    if total_documents > 0:
        documents_dir = os.path.join(domain_dir, "documents")
        if not os.path.exists(documents_dir):
            os.makedirs(documents_dir)
        # 按文件类型保存文档URL
        for ext, urls in document_urls.items():
            if urls:
                doc_type_dir = os.path.join(documents_dir, ext[1:])  # 去掉扩展名前的点
                if not os.path.exists(doc_type_dir):
                    os.makedirs(doc_type_dir)
                doc_file = os.path.join(doc_type_dir, f"{base_domain}{ext}.txt")
                with open(doc_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(sorted(urls)))
                print(Fore.BLUE + f"[✓] {ext.upper()} 文档URL保存至: {doc_file}")
                documents_saved = True
    return results_saved, documents_saved


def print_results(regular_urls, document_urls, base_domain):
    """打印结果"""
    if not regular_urls and sum(len(urls) for urls in document_urls.values()) == 0:
        print(Fore.RED + "\n[-] 未找到任何URL，请检查搜索语法或网络")
        return
    print(Fore.GREEN + f"\n[+] 为 {base_domain} 提取到的结果:")
    print(Fore.GREEN + "-" * 60)
    if regular_urls:
        print(Fore.GREEN + f"[+] {len(regular_urls)} 个普通URL:")
        for i, url in enumerate(sorted(regular_urls), 1):
            print(f"{i}. {url}")
    # 计算文档URL总数
    total_documents = sum(len(urls) for urls in document_urls.values())
    if total_documents > 0:
        print(Fore.BLUE + f"\n[+] {total_documents} 个文档URL (按类型分类):")
        for ext, urls in document_urls.items():
            if urls:
                print(Fore.BLUE + f"\n  [{ext.upper()}] ({len(urls)} 个):")
                for i, url in enumerate(sorted(urls), 1):
                    print(f"  {i}. {url}")
    print(Fore.GREEN + "-" * 60)


def send_email(sender_email, sender_password, receiver_email, subject, content):
    # 创建邮件对象
    message = MIMEMultipart()
    # 使用 formataddr 函数严格按照 RFC 标准格式化 From 字段
    sender_name = "Python 邮件发送"
    message['From'] = formataddr((str(Header(sender_name, 'utf-8')), sender_email))
    message['To'] = receiver_email  # 直接使用邮箱地址，QQ邮箱不接受 Header 包装
    message['Subject'] = Header(subject, 'utf-8')
    # 添加邮件正文
    message.attach(MIMEText(content, 'plain', 'utf-8'))
    try:
        # 连接QQ邮箱SMTP服务器（SSL加密）
        smtp_obj = smtplib.SMTP_SSL('smtp.qq.com', 465)
        smtp_obj.login(sender_email, sender_password)
        # 发送邮件
        smtp_obj.sendmail(sender_email, [receiver_email], message.as_string())
        print("邮件发送成功！")
    except smtplib.SMTPException as e:
        print(f"邮件发送失败: {e}")
    finally:
        # 关闭连接
        if 'smtp_obj' in locals():
            smtp_obj.quit()


if __name__ == "__main__":
    print_banner()
    if not check_environment():
        sys.exit(1)
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Google URL Search')
    parser.add_argument('-f', '--file', type=str, required=True, help='域名文件路径')
    parser.add_argument('--proxy', type=str, default='127.0.0.1:7890', help='HTTP代理地址 (默认: 127.0.0.1:7890)')
    args = parser.parse_args()

    # 初始化统计信息
    total_domains = 0
    total_regular_urls = 0
    total_document_urls = 0

    try:
        with open(args.file, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
        total_domains = len(domains)
        print(Fore.GREEN + f"[+] 读取到 {total_domains} 个域名")
    except Exception as e:
        print(Fore.RED + f"[-] 读取域名文件失败: {str(e)}")
        sys.exit(1)

    driver = setup_driver(args.proxy)
    for domain in domains:
        print(Fore.CYAN + f"\n{'=' * 50}")
        print(Fore.CYAN + f"[+] 开始爬取域名: {domain}")
        print(Fore.CYAN + f"{'=' * 50}")
        try:
            start_time = time.time()
            query = f"site:{domain}"
            regular_urls, document_urls = extract_urls(driver, query)
            end_time = time.time()
            # 计算文档URL总数
            domain_doc_count = sum(len(urls) for urls in document_urls.values())
            # 更新全局统计
            total_regular_urls += len(regular_urls)
            total_document_urls += domain_doc_count

            if regular_urls or domain_doc_count > 0:
                regular_saved, docs_saved = save_results(regular_urls, document_urls, domain)
                print(Fore.GREEN + "\n[✓] 爬取统计:")
                print(Fore.GREEN + f"  - 爬取总URL数量: {len(regular_urls) + domain_doc_count}")
                print(Fore.GREEN + f"  - 普通URL: {len(regular_urls)}")
                print(Fore.BLUE + f"  - 文档URL: {domain_doc_count}")
                print(Fore.YELLOW + f"  - 耗时: {end_time - start_time:.2f} 秒")
                if regular_saved:
                    print(
                        Fore.GREEN + f"  - 普通URL路径: {os.path.join('results', domain, f'Google_URLs_{domain}.txt')}")
                if docs_saved:
                    print(Fore.BLUE + f"  - 文档URL路径: {os.path.join('results', domain, 'documents')}")
            else:
                print(Fore.RED + f"[-] {domain} 未找到任何有效URL，不生成文件")
        except Exception as e:
            print(Fore.RED + f"[-] 处理 {domain} 出错: {str(e)}")

    driver.quit()
    print(Fore.GREEN + "\n[+] 所有域名处理完毕！")

    # 发送汇总邮件
    email_config = {
        "sender_email": "xxx@qq.com",
        "sender_password": "xxx",
        "receiver_email": "xxx@163.com",
        "subject": "📧 Chrome的URL信息收集工作已完成！",
        "content": f"""
        您好！尊敬的辉小鱼先生！
        关于Chrome的URL收集工作已全面完成！

        本次爬取统计：
        - 总域名数量：{total_domains}
        - 普通URL总数：{total_regular_urls}
        - 文档URL总数：{total_document_urls}

        如果你收到了这封邮件，说明GoogleURLSearch.py脚本已运行完毕！
        祝您挖洞愉快，必出高危哦~~~
        GoogleFirefoxURL 邮件助手
        """
    }

    send_email(**email_config)
