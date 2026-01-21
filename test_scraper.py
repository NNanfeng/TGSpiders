#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 验证 TGSpider 的基本功能
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import csv

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(__file__))


def test_csv_headers():
    """测试CSV表头是否完整"""
    print("测试 1: CSV 表头...")
    from tg_scraper import TGGroupScraper
    
    # 创建临时实例（使用环境变量默认值）
    os.environ['API_ID'] = '12345'
    os.environ['API_HASH'] = 'test_hash'
    os.environ['PHONE'] = '+1234567890'
    os.environ['GROUP_USERNAME'] = 'test_group'
    
    scraper = TGGroupScraper()
    
    # 验证表头字段
    expected_fields = [
        'message_id', 'date', 'time', 'sender_id', 'sender_username',
        'sender_first_name', 'sender_last_name', 'sender_phone', 'sender_is_bot',
        'message_text', 'reply_to_msg_id', 'forward_from_id', 'forward_from_name',
        'views', 'forwards', 'replies', 'edit_date', 'media_type', 'has_media',
        'file_name', 'file_size', 'txt_content', 'grouped_id', 'post_author'
    ]
    
    assert scraper.csv_headers == expected_fields, "CSV headers do not match"
    print(f"  ✓ CSV 表头包含 {len(scraper.csv_headers)} 个字段")
    

def test_csv_content_escape():
    """测试CSV内容转义"""
    print("\n测试 2: CSV 内容转义...")
    from tg_scraper import TGGroupScraper
    
    os.environ['API_ID'] = '12345'
    os.environ['API_HASH'] = 'test_hash'
    os.environ['PHONE'] = '+1234567890'
    os.environ['GROUP_USERNAME'] = 'test_group'
    
    scraper = TGGroupScraper()
    
    # 测试换行符处理
    test_text = "第一行\n第二行\r\n第三行"
    result = scraper.escape_csv_content(test_text)
    assert '\r' not in result, "Should remove \\r"
    assert '\n' in result, "Should keep \\n"
    print("  ✓ 换行符处理正确")
    
    # 测试 None 处理
    result = scraper.escape_csv_content(None)
    assert result == '', "None should return empty string"
    print("  ✓ None 处理正确")


def test_checkpoint_operations():
    """测试检查点功能"""
    print("\n测试 3: 检查点功能...")
    from tg_scraper import TGGroupScraper
    
    os.environ['API_ID'] = '12345'
    os.environ['API_HASH'] = 'test_hash'
    os.environ['PHONE'] = '+1234567890'
    os.environ['GROUP_USERNAME'] = 'test_group'
    
    scraper = TGGroupScraper()
    
    # 保存检查点
    test_message_id = 12345
    test_date = "2024-01-01 12:00:00"
    scraper.save_checkpoint(test_message_id, test_date)
    
    # 读取检查点
    checkpoint = scraper.load_checkpoint()
    assert checkpoint['last_message_id'] == test_message_id
    assert checkpoint['last_date'] == test_date
    print(f"  ✓ 检查点保存和读取正常")
    
    # 清理测试文件
    if os.path.exists('checkpoint.json'):
        os.remove('checkpoint.json')


def test_csv_file_naming():
    """测试CSV文件命名"""
    print("\n测试 4: CSV 文件命名...")
    from tg_scraper import TGGroupScraper
    
    os.environ['API_ID'] = '12345'
    os.environ['API_HASH'] = 'test_hash'
    os.environ['PHONE'] = '+1234567890'
    os.environ['GROUP_USERNAME'] = 'test_group'
    
    scraper = TGGroupScraper()
    
    # 测试不同月份的文件名
    test_date = datetime(2024, 1, 15)
    filename = scraper.get_csv_filename(test_date)
    assert filename.name == "messages_2024-01.csv"
    print(f"  ✓ 文件名格式正确: {filename.name}")
    
    test_date = datetime(2024, 12, 31)
    filename = scraper.get_csv_filename(test_date)
    assert filename.name == "messages_2024-12.csv"
    print(f"  ✓ 跨月文件名正确: {filename.name}")


def test_data_directory_creation():
    """测试数据目录创建"""
    print("\n测试 5: 数据目录创建...")
    from tg_scraper import TGGroupScraper
    
    os.environ['API_ID'] = '12345'
    os.environ['API_HASH'] = 'test_hash'
    os.environ['PHONE'] = '+1234567890'
    os.environ['GROUP_USERNAME'] = 'test_group'
    
    scraper = TGGroupScraper()
    
    # 验证数据目录已创建
    assert scraper.data_dir.exists(), "Data directory should exist"
    assert scraper.data_dir.is_dir(), "Data directory should be a directory"
    print(f"  ✓ 数据目录已创建: {scraper.data_dir}")


def test_csv_creation():
    """测试CSV文件创建"""
    print("\n测试 6: CSV 文件创建...")
    from tg_scraper import TGGroupScraper
    
    os.environ['API_ID'] = '12345'
    os.environ['API_HASH'] = 'test_hash'
    os.environ['PHONE'] = '+1234567890'
    os.environ['GROUP_USERNAME'] = 'test_group'
    
    scraper = TGGroupScraper()
    
    # 创建测试CSV
    test_file = scraper.data_dir / "test_messages.csv"
    scraper.ensure_csv_exists(test_file)
    
    # 验证文件存在并有表头
    assert test_file.exists(), "CSV file should be created"
    
    with open(test_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        assert headers == scraper.csv_headers, "CSV headers should match"
    
    print(f"  ✓ CSV 文件创建正确，包含完整表头")
    
    # 清理测试文件
    if test_file.exists():
        test_file.unlink()


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("TGSpiders 功能测试")
    print("=" * 60)
    
    try:
        test_csv_headers()
        test_csv_content_escape()
        test_checkpoint_operations()
        test_csv_file_naming()
        test_data_directory_creation()
        test_csv_creation()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过!")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        return False
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
