#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日定时爬取脚本
用于定时任务，每天爬取前一天的群组消息

使用方法：
1. 配置 .env 文件中的群组列表
2. 使用 cron 或其他定时任务工具每天执行此脚本

例如，每天凌晨1点执行：
0 1 * * * cd /path/to/TGSpiders && python daily_scraper.py >> logs/daily_scraper.log 2>&1
"""

import asyncio
import sys
from datetime import datetime

# 导入爬虫模块
from tg_scraper import scrape_yesterday


async def main():
    """主函数"""
    print(f"\n{'='*60}")
    print(f"定时任务开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    try:
        await scrape_yesterday()
        print(f"\n{'='*60}")
        print(f"定时任务成功完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        return 0
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"定时任务失败: {e}")
        print(f"{'='*60}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
