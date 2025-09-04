# 🌊 GoogleFirefoxURL - 智能双引擎 URL 爬取工具

<img width="1277" height="750" alt="image02" src="https://github.com/user-attachments/assets/b2347ccd-5030-40db-928f-c5948fb4a2ea" />


GoogleFirefoxURL 是一套基于 Selenium 的 URL 智能爬取解决方案，包含`GoogleURL.py`和`FireFoxURL.py`两个核心工具，分别针对 Google 和 DuckDuckGo 搜索引擎，帮助您高效收集指定域名下的网络资源。

## 🚀 核心功能

### 🔍 双引擎爬取系统

- **GoogleURL.py**：基于 Chrome 浏览器内核，针对 Google 搜索引擎优化
- **FireFoxURL.py**：基于 Firefox 浏览器内核，针对 DuckDuckGo 搜索引擎优化
- 自动切换搜索结果页面，深度挖掘目标资源

### 📁 智能内容分类

- 自动区分普通网页 URL 和文档类 URL

- 支持 13 种常见文档格式识别：

  ```plaintext
  .pdf  .docx  .doc  .rar  .inc  .txt  .sql  .conf
  .xlsx  .xls  .csv  .ppt  .pptx
  ```

- 结构化存储结果，按域名和文件类型自动分类

### 🛡️ 反检测机制

- 浏览器指纹随机化处理
- 禁用自动化特征标识
- 智能处理验证码（支持人工干预）
- 自定义代理支持，避免 IP 限制

### 📊 结果管理

- 自动去重处理，确保数据唯一性
- 分类存储结构，便于后续分析
- 详细爬取日志，便于问题排查

### 📧 完成通知

- 任务结束自动发送邮件通知
- 包含爬取统计信息和结果路径

## 📋 技术规格

| 特性         | GoogleURL.py   | FireFoxURL.py   |
| ------------ | -------------- | --------------- |
| 核心浏览器   | Google Chrome  | Mozilla Firefox |
| 目标搜索引擎 | Google         | DuckDuckGo      |
| 依赖驱动     | ChromeDriver   | GeckoDriver     |
| 额外依赖     | tldextract     | 无              |
| 默认代理     | 127.0.0.1:7890 | 无默认代理      |
| 多浏览器支持 | 仅 Chrome      | 仅 Firefox      |

## 🛠️ 安装指南

### 前置要求

- Python 3.7 或更高版本
- Google Chrome 浏览器（用于 GoogleURL.py）
- Mozilla Firefox 浏览器（用于 FireFoxURL.py）
- 对应版本的驱动程序：
  - [ChromeDriver](https://sites.google.com/chromium.org/driver/) - 需与 Chrome 版本匹配
  - [GeckoDriver](https://github.com/mozilla/geckodriver/releases) - 需与 Firefox 版本匹配

### 安装步骤

1. **克隆仓库**

   ```bash
   git clone https://github.com/Bifishone/GoogleFirefoxURL.git
   cd GoogleFirefoxURL
   ```

2. **安装依赖包**

   ```bash
   # 安装核心依赖
   pip install selenium colorama
   
   # 安装GoogleURL.py额外依赖
   pip install tldextract
   ```

3. **配置浏览器驱动**

   - 将下载的

     ```
     chromedriver
     ```

     和

     ```
     geckodriver
     ```

     放置在：

     - 与脚本相同的目录下，或
     - 系统环境变量`PATH`包含的目录中

## 📖 使用指南

### 准备工作

创建包含目标域名的文本文件（例如`target_domains.txt`），格式如下：



```plaintext
example.com
test.org
sample.net
```



> ⚠️ 注意：域名不要包含`http://`或`https://`前缀

### 基本用法

#### 运行 GoogleURL 爬虫

```bash
# 基本使用
python GoogleURL.py -f target_domains.txt

# 使用代理
python GoogleURL.py -f target_domains.txt --proxy 127.0.0.1:1080
```

#### 运行 FireFoxURL 爬虫

```bash
# 基本使用
python FireFoxURL.py -f target_domains.txt

# 使用代理
python FireFoxURL.py -f target_domains.txt --proxy 127.0.0.1:1080
```

### 参数说明

| 参数        | 缩写 | 描述                               | 适用工具         |
| ----------- | ---- | ---------------------------------- | ---------------- |
| `--file`    | `-f` | 包含目标域名的文本文件路径（必填） | 两者均支持       |
| `--proxy`   | 无   | 代理服务器地址（格式：host:port）  | 两者均支持       |
| `--browser` | 无   | 指定浏览器（目前仅支持 firefox）   | 仅 FireFoxURL.py |
| `--help`    | `-h` | 显示帮助信息                       | 两者均支持       |

## 📂 结果输出结构

爬取结果将保存在当前目录的`results`文件夹中，采用以下组织结构：

```plaintext
results/
└── example.com/                  # 按域名分类的文件夹
    ├── Google_URLs_example.com.txt  # Google爬取的普通URL（仅GoogleURL）
    ├── Firefox_URLs_example.com.txt # Firefox爬取的普通URL（仅FireFoxURL）
    └── documents/                # 文档URL分类存储
        ├── pdf/
        │   └── example.com.pdf.txt
        ├── docx/
        │   └── example.com.docx.txt
        ├── xls/
        │   └── example.com.xls.txt
        └── ...（其他文档类型）
```

## 🔍 验证码处理

当工具检测到验证码时：

1. 程序会暂停并显示提示信息
2. 请在打开的浏览器窗口中手动完成验证码
3. 完成后返回终端，按回车键继续爬取过程
4. 如无法完成验证，可按`Ctrl+C`终止程序

## 📧 邮件通知配置

工具默认配置了邮件通知功能，任务完成后会自动发送通知邮件。



默认配置（可在代码中修改）：

- **发件人**：1794686508@qq.com
- **收件人**：shenghui3301@163.com
- **SMTP 服务器**：[smtp.qq.com](https://smtp.qq.com/)
- **SMTP 端口**：587



如需修改配置，请在代码中找到`email_config`（GoogleURL.py）或`EMAIL_CONFIG`（FireFoxURL.py）部分进行调整。

## ⚠️ 注意事项

1. **驱动兼容性**：确保浏览器驱动版本与您安装的浏览器版本完全匹配
2. **频率控制**：避免短时间内对同一搜索引擎发送过多请求，以防 IP 被临时封禁
3. **网络环境**：部分网络环境可能无法访问 Google 搜索引擎，请确保网络通畅
4. **浏览器窗口**：爬取过程中请勿关闭程序自动打开的浏览器窗口
5. **大型任务**：对于包含大量域名的任务，建议分批次处理

## ❓ 常见问题

### 1. 驱动未找到错误

**解决方案**：

- 确认驱动文件名正确（`chromedriver`或`geckodriver`）
- 确保驱动与脚本在同一目录，或已添加到系统 PATH
- 检查驱动版本与浏览器版本是否匹配

### 2. 爬取结果为空

**可能原因**：

- 域名格式不正确（包含了`http://`前缀）
- 网络连接问题或代理配置错误
- 搜索引擎没有相关结果
- IP 被搜索引擎临时限制

### 3. 邮件发送失败

**解决方案**：

- 检查网络连接和 SMTP 服务器配置
- 确认 SMTP 端口是否正确（通常是 587 或 465）
- 对于 QQ 邮箱，需使用授权码而非登录密码
- 检查收件人邮箱地址是否正确

## 📜 许可证

```plaintext
MIT License

Copyright (c) 2023 一只鱼（Bifishone）

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## 👤 作者信息

**一只鱼（Bifishone）**



专注于网络信息收集与数据分析工具开发，致力于提供高效、可靠的网络爬虫解决方案。

------




⭐ 如果这个工具对您有帮助，请给项目点个 Star 支持一下！ ⭐
