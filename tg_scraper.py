#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Group Message Scraper
爬取Telegram群组历史消息并保存为CSV文件
"""

import os
import csv
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from telethon import TelegramClient
from telethon.tl.types import (
    MessageMediaDocument,
    DocumentAttributeFilename,
    User,
    Channel,
    Chat
)

# Load environment variables
load_dotenv()


class TGGroupScraper:
    """Telegram群组消息爬虫"""
    
    def __init__(self):
        """初始化爬虫"""
        self.api_id = int(os.getenv('API_ID', '0'))
        self.api_hash = os.getenv('API_HASH', '')
        self.phone = os.getenv('PHONE', '')
        self.group_username = os.getenv('GROUP_USERNAME', '')
        
        if not all([self.api_id, self.api_hash, self.phone, self.group_username]):
            raise ValueError("请在.env文件中配置所有必需的参数")
        
        self.client = TelegramClient('tg_scraper_session', self.api_id, self.api_hash)
        self.checkpoint_file = 'checkpoint.json'
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        
        # CSV表头
        self.csv_headers = [
            'message_id',           # 消息ID
            'date',                 # 发送日期
            'time',                 # 发送时间
            'sender_id',            # 发送者ID
            'sender_username',      # 发送者用户名
            'sender_first_name',    # 发送者名字
            'sender_last_name',     # 发送者姓氏
            'sender_phone',         # 发送者电话
            'sender_is_bot',        # 是否机器人
            'message_text',         # 消息文本内容
            'reply_to_msg_id',      # 回复的消息ID
            'forward_from_id',      # 转发来源ID
            'forward_from_name',    # 转发来源名称
            'views',                # 查看数
            'forwards',             # 转发数
            'replies',              # 回复数
            'edit_date',            # 编辑日期
            'media_type',           # 媒体类型
            'has_media',            # 是否有媒体
            'file_name',            # 文件名
            'file_size',            # 文件大小
            'txt_content',          # txt文件内容
            'grouped_id',           # 分组ID
            'post_author',          # 发帖者
        ]
    
    def load_checkpoint(self) -> Dict[str, Any]:
        """加载检查点"""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载检查点失败: {e}")
                return {}
        return {}
    
    def save_checkpoint(self, last_message_id: int, last_date: str):
        """保存检查点"""
        checkpoint = {
            'last_message_id': last_message_id,
            'last_date': last_date,
            'updated_at': datetime.now().isoformat()
        }
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)
    
    def get_csv_filename(self, date: datetime) -> Path:
        """根据日期获取CSV文件名（按月分文件）"""
        month_str = date.strftime('%Y-%m')
        return self.data_dir / f"messages_{month_str}.csv"
    
    def ensure_csv_exists(self, filename: Path):
        """确保CSV文件存在并有表头"""
        if not filename.exists():
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=self.csv_headers)
                writer.writeheader()
    
    def escape_csv_content(self, text: Optional[str]) -> str:
        """转义CSV内容，处理换行符等特殊字符"""
        if text is None:
            return ''
        # CSV会自动处理包含换行的内容（通过双引号包裹）
        # 但我们需要确保内容是字符串类型
        return str(text).replace('\r\n', '\n').replace('\r', '\n')
    
    async def get_sender_info(self, sender) -> Dict[str, Any]:
        """获取发送者信息"""
        info = {
            'sender_id': '',
            'sender_username': '',
            'sender_first_name': '',
            'sender_last_name': '',
            'sender_phone': '',
            'sender_is_bot': False,
        }
        
        if sender is None:
            return info
        
        if isinstance(sender, User):
            info['sender_id'] = sender.id
            info['sender_username'] = sender.username or ''
            info['sender_first_name'] = sender.first_name or ''
            info['sender_last_name'] = sender.last_name or ''
            info['sender_phone'] = sender.phone or ''
            info['sender_is_bot'] = sender.bot or False
        elif isinstance(sender, (Channel, Chat)):
            info['sender_id'] = sender.id
            info['sender_username'] = getattr(sender, 'username', '') or ''
            info['sender_first_name'] = sender.title or ''
        
        return info
    
    async def extract_txt_content(self, message) -> tuple[Optional[str], Optional[int]]:
        """提取txt文件内容"""
        if not message.media:
            return None, None
        
        if isinstance(message.media, MessageMediaDocument):
            document = message.media.document
            
            # 获取文件名
            filename = None
            for attr in document.attributes:
                if isinstance(attr, DocumentAttributeFilename):
                    filename = attr.file_name
                    break
            
            # 只处理txt文件
            if filename and filename.lower().endswith('.txt'):
                try:
                    # 下载txt文件内容
                    file_bytes = await self.client.download_media(message, bytes)
                    if file_bytes:
                        # 尝试多种编码
                        for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-16']:
                            try:
                                txt_content = file_bytes.decode(encoding)
                                return txt_content, document.size
                            except UnicodeDecodeError:
                                continue
                        # 如果所有编码都失败，返回原始内容
                        return str(file_bytes), document.size
                except Exception as e:
                    print(f"提取txt文件内容失败 (message_id={message.id}): {e}")
                    return None, document.size
            
            return None, document.size if document else None
        
        return None, None
    
    async def process_message(self, message) -> Dict[str, Any]:
        """处理单条消息"""
        sender = await message.get_sender()
        sender_info = await self.get_sender_info(sender)
        
        # 提取txt文件内容
        txt_content, file_size = await self.extract_txt_content(message)
        
        # 获取文件名
        file_name = None
        media_type = None
        if message.media:
            if isinstance(message.media, MessageMediaDocument):
                document = message.media.document
                for attr in document.attributes:
                    if isinstance(attr, DocumentAttributeFilename):
                        file_name = attr.file_name
                        break
                media_type = 'document'
            else:
                media_type = type(message.media).__name__
        
        # 构建消息数据
        message_data = {
            'message_id': message.id,
            'date': message.date.strftime('%Y-%m-%d') if message.date else '',
            'time': message.date.strftime('%H:%M:%S') if message.date else '',
            **sender_info,
            'message_text': self.escape_csv_content(message.text),
            'reply_to_msg_id': message.reply_to_msg_id or '',
            'forward_from_id': message.fwd_from.from_id.user_id if message.fwd_from and hasattr(message.fwd_from.from_id, 'user_id') else '',
            'forward_from_name': message.fwd_from.from_name if message.fwd_from else '',
            'views': message.views or 0,
            'forwards': message.forwards or 0,
            'replies': message.replies.replies if message.replies else 0,
            'edit_date': message.edit_date.strftime('%Y-%m-%d %H:%M:%S') if message.edit_date else '',
            'media_type': media_type or '',
            'has_media': bool(message.media),
            'file_name': file_name or '',
            'file_size': file_size or '',
            'txt_content': self.escape_csv_content(txt_content),
            'grouped_id': message.grouped_id or '',
            'post_author': message.post_author or '',
        }
        
        return message_data
    
    async def scrape_group(self):
        """爬取群组消息"""
        await self.client.start(self.phone)
        print(f"已登录 Telegram")
        
        try:
            # 获取群组实体
            entity = await self.client.get_entity(self.group_username)
            print(f"找到群组: {entity.title if hasattr(entity, 'title') else self.group_username}")
            
            # 加载检查点
            checkpoint = self.load_checkpoint()
            start_message_id = checkpoint.get('last_message_id', 0)
            
            if start_message_id:
                print(f"从检查点继续: message_id={start_message_id}")
            else:
                print("从头开始爬取")
            
            # 统计信息
            total_messages = 0
            current_csv_file = None
            csv_writer = None
            csv_file_handle = None
            last_message_id = start_message_id
            
            # 从旧到新遍历消息 (reverse=True)
            async for message in self.client.iter_messages(
                entity,
                reverse=True,
                min_id=start_message_id
            ):
                try:
                    # 处理消息
                    message_data = await self.process_message(message)
                    
                    # 获取对应的CSV文件
                    csv_filename = self.get_csv_filename(message.date)
                    
                    # 如果需要切换CSV文件
                    if current_csv_file != csv_filename:
                        # 关闭之前的文件
                        if csv_file_handle:
                            csv_file_handle.close()
                        
                        # 确保新文件存在
                        self.ensure_csv_exists(csv_filename)
                        
                        # 打开新文件（追加模式）
                        csv_file_handle = open(csv_filename, 'a', newline='', encoding='utf-8-sig')
                        csv_writer = csv.DictWriter(csv_file_handle, fieldnames=self.csv_headers)
                        current_csv_file = csv_filename
                        print(f"切换到文件: {csv_filename}")
                    
                    # 写入CSV
                    csv_writer.writerow(message_data)
                    
                    total_messages += 1
                    last_message_id = message.id
                    
                    # 每100条消息显示进度并保存检查点
                    if total_messages % 100 == 0:
                        print(f"已处理 {total_messages} 条消息 (当前ID: {message.id})")
                        # 刷新文件缓冲区
                        if csv_file_handle:
                            csv_file_handle.flush()
                        # 保存检查点
                        self.save_checkpoint(
                            last_message_id,
                            message.date.strftime('%Y-%m-%d %H:%M:%S')
                        )
                    
                except Exception as e:
                    print(f"处理消息失败 (message_id={message.id}): {e}")
                    continue
            
            # 关闭最后的文件
            if csv_file_handle:
                csv_file_handle.close()
            
            # 保存最终检查点
            if last_message_id > start_message_id:
                self.save_checkpoint(last_message_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            print(f"\n爬取完成！")
            print(f"总共处理: {total_messages} 条消息")
            print(f"数据保存在: {self.data_dir}")
            
        except Exception as e:
            print(f"爬取过程中出错: {e}")
            raise
        finally:
            await self.client.disconnect()


async def main():
    """主函数"""
    scraper = TGGroupScraper()
    await scraper.scrape_group()


if __name__ == '__main__':
    print("=" * 60)
    print("Telegram 群组消息爬虫")
    print("=" * 60)
    asyncio.run(main())
