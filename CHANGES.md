# 更新说明 (Change Log)

## 新功能 (New Features)

### 1. 多群组同时爬取
- 支持在 `.env` 文件中配置多个群组，使用逗号分隔
- 示例：`GROUP_USERNAMES=group1,group2,group3`
- 每个群组独立存储在 `data/群组名/` 目录下
- 每个群组有独立的检查点文件，支持独立的断点续传

### 2. 按群组名称分开存储
- 新的目录结构：
  ```
  data/
  ├── group1/
  │   ├── checkpoint.json
  │   ├── messages_2024-01.csv
  │   └── ...
  ├── group2/
  │   ├── checkpoint.json
  │   └── ...
  ```

### 3. 日期范围过滤
- 支持设置开始日期和结束日期来过滤消息
- 在 `.env` 文件中配置：
  ```
  START_DATE=2024-01-01
  END_DATE=2024-01-31
  ```
- 适合定时爬取特定时间段的消息

### 4. 定时爬取昨天的消息
- 新增 `scrape_yesterday()` 函数，自动爬取前一天的消息
- 新增 `daily_scraper.py` 脚本，可配合 cron 定时任务使用
- 使用方法：
  ```bash
  # 每天凌晨1点执行
  0 1 * * * cd /path/to/TGSpiders && python daily_scraper.py >> logs/daily_scraper.log 2>&1
  ```

### 5. 优化 CSV 换行处理
- 将 `message_text` 和 `txt_content` 中的换行符替换为空格
- 压缩多个连续空格为单个空格
- 防止 CSV 多行记录问题，提高 Elasticsearch 导入兼容性

## 安全改进 (Security Improvements)

### 路径安全
- 强化了群组名称的路径清理逻辑
- 防止路径遍历攻击
- 只允许字母、数字、下划线和连字符

### 环境变量处理
- `scrape_yesterday()` 函数现在会正确恢复原始环境变量
- 避免全局状态污染

## 代码质量改进 (Code Quality Improvements)

- 将 `re` 模块导入移至文件顶部，提高性能
- 增加了新的测试用例覆盖新功能
- 更新了文档说明新功能的使用方法

## 向后兼容性 (Backward Compatibility)

- 仍然支持旧的 `GROUP_USERNAME` (单数) 环境变量
- 如果只配置一个群组，行为与之前版本相同
- 现有的数据目录结构会自动迁移到新结构

## 测试覆盖 (Test Coverage)

新增测试：
- 多群组配置解析
- 日期过滤功能
- 改进的 CSV 内容转义
- 群组独立的数据目录和检查点

所有测试均通过 ✓
