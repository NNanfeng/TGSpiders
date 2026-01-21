# TGSpiders - Telegram群组消息爬虫

一个基于 Python 和 Telethon 的 Telegram 群组历史消息爬虫工具，支持将群组消息导出为 CSV 文件。

## 功能特点

- ✅ 支持爬取公开群组的所有历史消息
- ✅ 按月自动分割 CSV 文件，便于管理大量数据
- ✅ 详细的 CSV 表头，包含发送者信息、消息内容等完整数据
- ✅ 完善的断点续传机制，支持中断后继续爬取
- ✅ 自动处理换行符，确保 CSV 格式正确
- ✅ 支持提取 txt 文件内容并保存到 CSV
- ✅ 从旧到新的时间顺序爬取
- ✅ 不下载其他媒体文件（图片、视频等），节省空间

## CSV 字段说明

导出的 CSV 文件包含以下字段：

| 字段名 | 说明 |
|--------|------|
| message_id | 消息ID |
| date | 发送日期 |
| time | 发送时间 |
| sender_id | 发送者ID |
| sender_username | 发送者用户名 |
| sender_first_name | 发送者名字 |
| sender_last_name | 发送者姓氏 |
| sender_phone | 发送者电话 |
| sender_is_bot | 是否机器人 |
| message_text | 消息文本内容 |
| reply_to_msg_id | 回复的消息ID |
| forward_from_id | 转发来源ID |
| forward_from_name | 转发来源名称 |
| views | 查看数 |
| forwards | 转发数 |
| replies | 回复数 |
| edit_date | 编辑日期 |
| media_type | 媒体类型 |
| has_media | 是否有媒体 |
| file_name | 文件名 |
| file_size | 文件大小 |
| txt_content | txt文件内容 |
| grouped_id | 分组ID |
| post_author | 发帖者 |

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/NNanfeng/TGSpiders.git
cd TGSpiders
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 获取 Telegram API 凭证

1. 访问 https://my.telegram.org
2. 登录你的 Telegram 账号
3. 进入 "API development tools"
4. 创建一个新应用，获取 `api_id` 和 `api_hash`

### 4. 配置环境变量

复制示例配置文件并编辑：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的配置：

```
API_ID=your_api_id
API_HASH=your_api_hash
PHONE=your_phone_number
GROUP_USERNAME=target_group_username
```

**参数说明：**
- `API_ID`: 从 my.telegram.org 获取的 API ID
- `API_HASH`: 从 my.telegram.org 获取的 API Hash
- `PHONE`: 你的 Telegram 手机号（包含国家代码，如 +86）
- `GROUP_USERNAME`: 目标群组的用户名（不带 @ 符号）

## 使用方法

### 首次运行

```bash
python tg_scraper.py
```

首次运行时，程序会要求你：
1. 输入验证码（Telegram 会发送到你的手机）
2. 如果启用了两步验证，还需要输入密码

### 断点续传

程序会自动保存爬取进度到 `checkpoint.json` 文件。如果中途中断，再次运行程序时会自动从上次的位置继续爬取：

```bash
python tg_scraper.py
```

### 查看数据

爬取的数据保存在 `data/` 目录下，按月份分文件：

```
data/
├── messages_2024-01.csv
├── messages_2024-02.csv
├── messages_2024-03.csv
└── ...
```

## 文件结构

```
TGSpiders/
├── tg_scraper.py          # 主程序
├── requirements.txt       # Python 依赖
├── .env.example          # 配置文件示例
├── .env                  # 配置文件（需自行创建）
├── .gitignore           # Git 忽略文件
├── checkpoint.json      # 断点记录（自动生成）
├── data/                # 数据目录（自动生成）
│   └── messages_*.csv   # 按月分割的消息文件
└── tg_scraper_session.session  # Telegram 会话文件（自动生成）
```

## 注意事项

1. **API 限制**：Telegram API 有速率限制，如果遇到限制，程序会自动等待。对于十万级别的群组，完整爬取可能需要较长时间。

2. **账号安全**：
   - 不要分享你的 `api_id`、`api_hash` 和 `.session` 文件
   - `.env` 文件已被 `.gitignore` 忽略，不会被提交到 Git

3. **存储空间**：确保有足够的磁盘空间存储 CSV 文件

4. **换行处理**：消息中的换行符会被正确保存在 CSV 中（通过双引号包裹），可以正常使用 Excel 或其他工具打开

5. **txt 文件**：如果消息包含 txt 文件附件，程序会自动下载并提取内容，保存到 `txt_content` 字段

6. **媒体文件**：程序不会下载图片、视频等其他媒体文件，只会记录文件名和大小

## 常见问题

### Q: 如何找到群组的 username？

A: 在 Telegram 中打开群组，群组信息页面会显示 `@username` 格式的链接，使用其中的 `username` 部分（不带 @）

### Q: 可以爬取私有群组吗？

A: 如果你是群组成员，也可以爬取。但需要使用群组的邀请链接或 ID，而不是 username。需要修改代码中的 `get_entity` 调用。

### Q: 程序中断了怎么办？

A: 不用担心，再次运行程序即可。程序会从 `checkpoint.json` 读取上次的进度，自动从中断处继续。

### Q: CSV 文件用 Excel 打开乱码？

A: 程序使用 `utf-8-sig` 编码（带 BOM 标记），Excel 应该能正确识别。如果还有问题，可以尝试用记事本打开后另存为，或者使用专业的 CSV 编辑器。

### Q: 如何重新爬取？

A: 删除 `checkpoint.json` 文件和 `data/` 目录，然后重新运行程序。

## 技术细节

- **Telethon**: 使用 Telethon 库与 Telegram API 交互
- **异步编程**: 基于 asyncio 实现高效的异步爬取
- **CSV 处理**: 正确处理换行、特殊字符等，确保 CSV 格式规范
- **断点机制**: JSON 文件记录爬取进度，支持随时中断和恢复
- **按月分文件**: 自动根据消息日期分割 CSV 文件，避免单文件过大
- **编码检测**: 对 txt 文件尝试多种编码（UTF-8, GBK, GB2312, UTF-16）

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 免责声明

本工具仅供学习和研究使用，使用者需遵守 Telegram 的服务条款和相关法律法规。请勿用于非法用途。
