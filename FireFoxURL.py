import os
import time
import random
import argparse
import traceback
from colorama import init, Fore, Style
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException
)
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
import smtplib

# 初始化彩色输出
init(autoreset=True)

# 配置
SCROLL_PAUSE_TIME = 1.5  # 滚动等待时间
MAX_RETRIES = 9  # 页面加载重试次数
RESULTS_DIR = "results"
# 增强过滤列表
DEFAULT_FILTERS = [
    'google.com', 'googleadservices.com', 'googletagmanager.com',
    'duckduckgo.com', 'mozilla.org', 'firefox.com', 'javascript:void(0)'
]

# 文档文件扩展名列表
DOCUMENT_EXTS = ['.pdf', '.docx', '.doc', '.rar', '.inc', '.txt', '.sql', '.conf', '.xlsx', '.xls', '.csv', '.ppt',
                 '.pptx']

# 邮件配置
EMAIL_CONFIG = {
    # 发件人QQ邮箱信息（必须修改）
    "sender_email": "xxx@qq.com",  # 你的QQ邮箱地址
    "sender_password": "xxx",  # 你的QQ邮箱SMTP授权码

    # 收件人邮箱信息（可修改）
    "receiver_email": "xxx@163.com",  # 收件人邮箱地址

    # 邮件内容（可修改）
    "subject": "📧 Firefox的URL信息收集工作已完成！",  # 邮件主题
    "content": """
    您好！尊敬的辉小鱼先生！

    关于Firefox的URL收集工作已全面完成！
    如果你收到了这封邮件，说明FireFoxURLSearch.py脚本已运行完毕！

    祝您挖洞愉快，必出高危哦~~~
    GoogleFirefoxURL 邮件助手
    """
}


def print_banner():
    banner = r"""
                                                                                           ):)
                                                                                         (:::(
                                                                                         ):::::)
   _     ___/\\____________________________/))__ _  (:::::::)
 (::(  \ |         __________                                              |...):::::::)
  \::\  (        (__________,)                                          _|\::)
    \::\   )            __            ____________________|\:::|/
      ¯  /¤¤¤¤¤¤(    (   (::( ¯¯)\:::::::::::::::::::::::::::::::::::::\|¯
         /¤¤¤¤¤¤¤\\    \_.\::\   /:::/¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
        /¤¤¤¤¤¤¤¤\ \______/::'/
       /¤¤¤¤¤¤¤¤¤/\ :::::::::::\:/
      /¤¤¤¤¤¤¤¤¤¤):::)¯¯¯¯¯
     /¤¤¤¤¤¤¤¤¤¤/:::/
 _ /¤¤¤¤¤¤¤¤¤¤/:::/
(  ¯¯¯¯¯¯¯¯¯¯¯\::/     BY : Bifishone
  ¯¯¯¯¯¯¯¯¯¯¯¯
    """
    print(Fore.CYAN + banner)
    print(Fore.GREEN + "=" * 60)
    print(Fore.GREEN + "  Firefox URL Search - v1.0")
    print(Fore.GREEN + "=" * 60)
    print(Style.RESET_ALL)


def find_geckodriver():
    from shutil import which
    geckodriver_path = which("geckodriver")
    if geckodriver_path:
        print(Fore.GREEN + f"[✓] 找到geckodriver: {geckodriver_path}")
        return geckodriver_path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    geckodriver_exe = os.path.join(current_dir, "geckodriver.exe" if os.name == 'nt' else "geckodriver")
    if os.path.exists(geckodriver_exe):
        print(Fore.GREEN + f"[✓] 找到geckodriver: {geckodriver_exe}")
        return geckodriver_exe
    print(Fore.RED + "[-] 未找到geckodriver！")
    print(Fore.YELLOW + "[*] 请下载对应版本：https://github.com/mozilla/geckodriver/releases")
    import sys
    sys.exit(1)


def setup_firefox_driver(proxy=None):
    print(Fore.YELLOW + "[+] 配置Firefox浏览器...")
    options = Options()
    # 强化反爬配置
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    # 随机化浏览器指纹
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    options.set_preference("general.useragent.override", random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Mozilla/5.0 (Windows NT 11.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
    ]))
    # 代理配置
    if proxy:
        try:
            host, port = proxy.split(':')
            options.set_preference("network.proxy.type", 1)
            options.set_preference("network.proxy.http", host)
            options.set_preference("network.proxy.http_port", int(port))
            options.set_preference("network.proxy.ssl", host)
            options.set_preference("network.proxy.ssl_port", int(port))
            print(Fore.GREEN + f"[+] 代理配置成功: {proxy}")
        except:
            print(Fore.RED + f"[-] 代理格式错误（应为host:port），将不使用代理")
    try:
        service = Service(find_geckodriver())
        driver = webdriver.Firefox(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print(Fore.GREEN + "[✓] Firefox启动成功")
        return driver
    except Exception as e:
        print(Fore.RED + f"[-] 浏览器启动失败: {str(e)}")
        import sys
        sys.exit(1)


def wait_for_manual_verification(driver):
    """等待用户处理验证码或短暂等待后继续"""
    print(Fore.YELLOW + "\n[!] 正在检查是否需要验证码...")
    # 检查是否存在验证码元素
    try:
        # 通用验证码检测（示例选择器，需根据实际情况调整）
        captcha_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.captcha, div.g-recaptcha'))
        )
        print(Fore.RED + "[!] 检测到验证码，请手动完成验证后按Enter继续...")
        input()  # 等待用户确认
        print(Fore.GREEN + "[✓] 验证码验证完成，继续爬取")
    except TimeoutException:
        print(Fore.GREEN + "[✓] 未检测到验证码，3秒后开始爬取")
        time.sleep(3)
    except Exception as e:
        print(Fore.YELLOW + f"[*] 验证码检查出错: {str(e)}，继续爬取")


def get_url_ext(url):
    """获取URL的文件扩展名"""
    # 处理可能包含查询参数的URL
    path = url.split('?')[0].split('#')[0]
    return os.path.splitext(path)[1].lower()


def extract_urls(driver, domain, all_urls, document_urls):
    """提取并过滤URL"""
    urls = set()
    filtered_count = 0
    document_count = 0
    selectors = [
        'a[href]',
        'a.js-accessible-link',
        'div.g a'
    ]
    for selector in selectors:
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            links = driver.find_elements(By.CSS_SELECTOR, selector)
            print(Fore.YELLOW + f"[*] 使用选择器 '{selector}' 找到 {len(links)} 个链接")
            for link in links:
                try:
                    href = link.get_attribute('href')
                    if not href or not href.startswith('http'):
                        continue
                    # 过滤规则
                    if any(filter_domain in href for filter_domain in DEFAULT_FILTERS):
                        filtered_count += 1
                        continue
                    if domain not in href:
                        filtered_count += 1
                        continue
                    if href.endswith('.apk'):
                        filtered_count += 1
                        continue
                    # 检查是否为文档文件
                    ext = get_url_ext(href)
                    if ext in DOCUMENT_EXTS:
                        if href not in document_urls:
                            document_urls[ext].add(href)
                            document_count += 1
                            print(Fore.BLUE + f"[✓] 找到文档URL ({ext}): {href}")
                        continue
                    # 普通URL处理
                    if href not in all_urls:
                        urls.add(href)
                        all_urls.add(href)
                        print(Fore.GREEN + f"[✓] 找到有效URL: {href}")
                except:
                    continue
            if links:
                break  # 找到链接后停止尝试其他选择器
        except TimeoutException:
            print(Fore.YELLOW + f"[*] 选择器 '{selector}' 未找到元素，尝试下一种...")
        except Exception as e:
            print(Fore.RED + f"[-] 提取链接出错: {str(e)}")
    return urls, filtered_count, document_count


def click_more_results(driver):
    """点击“更多结果”按钮"""
    try:
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="more-results"]'))
        )
        # 模拟人类行为：滚动到按钮、悬停、随机延迟后点击
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior:'smooth'});", button)
        time.sleep(random.uniform(0.8, 1.5))
        button.click()
        print(Fore.GREEN + "[+] 点击“更多结果”按钮成功，等待页面加载...")
        # 等待新内容加载
        time.sleep(random.uniform(2, 4))
        return True
    except TimeoutException:
        print(Fore.YELLOW + "[*] 未找到“更多结果”按钮，停止翻页")
        return False
    except Exception as e:
        print(Fore.RED + f"[-] 点击按钮出错: {str(e)}")
        return False


def crawl_domain(driver, domain):
    """爬取主逻辑"""
    all_urls = set()
    document_urls = {ext: set() for ext in DOCUMENT_EXTS}  # 按扩展名分类的文档URL
    total_filtered = 0
    total_documents = 0
    page = 1
    try:
        search_url = f"https://duckduckgo.com/?q=site:{domain}"
        driver.get(search_url)
        print(Fore.GREEN + f"[+] 访问搜索页: {search_url}")
        # 等待验证码处理或短暂等待
        wait_for_manual_verification(driver)
        # 循环爬取
        while True:
            print(Fore.CYAN + f"\n[+] 正在爬取第 {page} 页...")
            # 滚动加载内容
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            # 提取并过滤URL
            current_urls, filtered_count, document_count = extract_urls(driver, domain, all_urls, document_urls)
            total_filtered += filtered_count
            total_documents += document_count
            print(
                Fore.YELLOW + f"[*] 本页提取: {len(current_urls)} 个普通URL | {document_count} 个文档URL | 过滤: {filtered_count}")
            print(
                Fore.YELLOW + f"[*] 累计: {len(all_urls)} 个普通URL | {total_documents} 个文档URL | 总过滤: {total_filtered}")
            # 尝试点击下一页
            if not click_more_results(driver):
                break
            page += 1
    except Exception as e:
        print(Fore.RED + f"[-] 爬取过程出错: {str(e)}")
        print(traceback.format_exc())
    return all_urls, document_urls, total_filtered


def save_results(urls, document_urls, domain):
    """保存结果"""
    results_saved = False
    documents_saved = False

    # 创建域名文件夹
    domain_dir = os.path.join(RESULTS_DIR, domain)
    if not os.path.exists(domain_dir):
        os.makedirs(domain_dir)

    # 保存普通URL
    if urls:
        regular_file = os.path.join(domain_dir, f"Firefox_URLs_{domain}.txt")
        with open(regular_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sorted(urls)))
        print(Fore.GREEN + f"[✓] 普通URL保存至: {regular_file}")
        results_saved = True

    # 检查是否有文档URL
    total_document_urls = sum(len(urls) for urls in document_urls.values())
    if total_document_urls > 0:
        # 创建文档文件夹
        documents_dir = os.path.join(domain_dir, "documents")
        if not os.path.exists(documents_dir):
            os.makedirs(documents_dir)

        # 按文件类型保存文档URL
        for ext, urls in document_urls.items():
            if urls:
                doc_type_dir = os.path.join(documents_dir, ext[1:])  # 去掉扩展名前的点
                if not os.path.exists(doc_type_dir):
                    os.makedirs(doc_type_dir)
                doc_file = os.path.join(doc_type_dir, f"{domain}{ext}.txt")
                with open(doc_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(sorted(urls)))
                print(Fore.BLUE + f"[✓] {ext.upper()} 文档URL保存至: {doc_file}")
                documents_saved = True

    return results_saved, documents_saved


def send_email(sender_email, sender_password, receiver_email, subject, content):
    # 创建邮件对象
    message = MIMEMultipart()

    # 使用 formataddr 函数严格按照 RFC 标准格式化 From 字段
    # 发件人姓名（可自定义）
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


def main():
    print_banner()
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=True, help='域名文件路径')
    parser.add_argument('--browser', default='firefox', choices=['firefox'])
    parser.add_argument('--proxy', help='代理（格式host:port）')
    args = parser.parse_args()
    try:
        with open(args.file, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
        print(Fore.GREEN + f"[+] 读取到 {len(domains)} 个域名")
    except Exception as e:
        print(Fore.RED + f"[-] 读取域名文件失败: {str(e)}")
        import sys
        sys.exit(1)
    driver = setup_firefox_driver(args.proxy)
    for domain in domains:
        print(Fore.CYAN + f"\n{'=' * 50}")
        print(Fore.CYAN + f"[+] 开始爬取域名: {domain}")
        print(Fore.CYAN + f"{'=' * 50}")
        try:
            start_time = time.time()
            urls, document_urls, filtered = crawl_domain(driver, domain)
            end_time = time.time()

            # 计算文档URL总数
            total_documents = sum(len(urls) for urls in document_urls.values())

            if urls or total_documents > 0:
                regular_saved, docs_saved = save_results(urls, document_urls, domain)

                print(Fore.GREEN + "\n[✓] 爬取统计:")
                print(Fore.GREEN + f"  - 爬取总URL数量: {len(urls) + total_documents + filtered}")
                print(Fore.YELLOW + f"  - 过滤无关URL: {filtered}")
                print(Fore.GREEN + f"  - 保存普通URL: {len(urls)}")
                print(Fore.BLUE + f"  - 保存文档URL: {total_documents}")
                print(Fore.YELLOW + f"  - 耗时: {end_time - start_time:.2f} 秒")

                if regular_saved:
                    print(
                        Fore.GREEN + f"  - 普通URL路径: {os.path.join(RESULTS_DIR, domain, f'Firefox_URLs_{domain}.txt')}")
                if docs_saved:
                    print(Fore.BLUE + f"  - 文档URL路径: {os.path.join(RESULTS_DIR, domain, 'documents')}")
            else:
                print(Fore.RED + f"[-] {domain} 未找到任何有效URL")
        except Exception as e:
            print(Fore.RED + f"[-] 处理 {domain} 出错: {str(e)}")
    driver.quit()
    print(Fore.GREEN + "\n[+] 所有域名处理完毕！")

    # 发送邮件
    send_email(**EMAIL_CONFIG)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(Fore.RED + f"\n[-] 脚本异常退出: {str(e)}")
        print(traceback.format_exc())

        # input("按任意键退出...")

