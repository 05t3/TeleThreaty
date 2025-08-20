#!/usr/bin/env python3
"""
threaty_bot - Advanced Telegram message fetcher with permission management
"""

import argparse
import requests
import os
import time
import pprint
import multiprocessing
import mimetypes
import json
from datetime import datetime
import sys
from pathlib import Path

class ThreatyBot:
    def __init__(self, token, timeout=30, download_dir="downloads"):
        self.token = token
        self.timeout = timeout
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        
        # File type categories for better organization
        self.file_categories = {
            'archive': ['.zip', '.7z', '.rar', '.tar', '.gz', '.gzip', '.bz2', '.xz', '.lzh', '.iso'],
            'document': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages'],
            'code': ['.py', '.js', '.java', '.cpp', '.c', '.html', '.css', '.php', '.rb', '.go', '.rs'],
            'spreadsheet': ['.xls', '.xlsx', '.csv', '.ods', '.numbers'],
            'presentation': ['.ppt', '.pptx', '.key', '.odp'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'],
            'audio': ['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac'],
            'video': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'],
            'executable': ['.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm', '.apk'],
            'config': ['.json', '.xml', '.yaml', '.yml', '.ini', '.conf', '.cfg']
        }
    
    def get_bot_info(self):
        """Get bot information"""
        try:
            response = requests.get(f"{self.base_url}/getMe", timeout=self.timeout)
            return response.json()
        except Exception as e:
            return {'ok': False, 'error': str(e)}
    
    def get_chat_info(self, chat_id):
        """Get detailed chat information"""
        url = f"{self.base_url}/getChat"
        data = {"chat_id": chat_id}
        try:
            response = requests.post(url, data=data, timeout=self.timeout)
            return response.json()
        except Exception as e:
            return {'ok': False, 'error': str(e)}
    
    def get_chat_member(self, chat_id, user_id):
        """Get chat member info including permissions"""
        url = f"{self.base_url}/getChatMember"
        data = {"chat_id": chat_id, "user_id": user_id}
        try:
            response = requests.post(url, data=data, timeout=self.timeout)
            return response.json()
        except Exception as e:
            return {'ok': False, 'error': str(e)}
    
    def get_chat_administrators(self, chat_id):
        """Get chat administrators"""
        url = f"{self.base_url}/getChatAdministrators"
        data = {"chat_id": chat_id}
        try:
            response = requests.post(url, data=data, timeout=self.timeout)
            return response.json()
        except Exception as e:
            return {'ok': False, 'error': str(e)}
    
    def get_chat_member_count(self, chat_id):
        """Get chat member count"""
        url = f"{self.base_url}/getChatMemberCount"
        data = {"chat_id": chat_id}
        try:
            response = requests.post(url, data=data, timeout=self.timeout)
            return response.json()
        except Exception as e:
            return {'ok': False, 'error': str(e)}
    
    def get_my_commands(self, chat_id):
        """Get bot commands"""
        url = f"{self.base_url}/getMyCommands"
        data = {"chat_id": chat_id}
        try:
            response = requests.get(url, data=data, timeout=self.timeout)
            return response.json()
        except Exception as e:
            return {'ok': False, 'error': str(e)}
    
    def get_my_default_admin_rights(self, chat_id):
        """Get default admin rights"""
        url = f"{self.base_url}/getMyDefaultAdministratorRights"
        data = {"chat_id": chat_id}
        try:
            response = requests.get(url, data=data, timeout=self.timeout)
            return response.json()
        except Exception as e:
            return {'ok': False, 'error': str(e)}
    
    def check_bot_permissions(self, chat_id):
        """Check what permissions the bot has"""
        print("\n" + "="*50)
        print("          BOT PERMISSION CHECK")
        print("="*50)
        
        # Check bot global capabilities
        bot_info = self.get_bot_info()
        if bot_info.get('ok'):
            bot_data = bot_info['result']
            print("🤖 Bot Global Capabilities:")
            print(f"   ✅ Can join groups: {bot_data.get('can_join_groups', False)}")
            print(f"   🔓 Can read all group messages: {bot_data.get('can_read_all_group_messages', False)}")
            print(f"   📱 Supports inline queries: {bot_data.get('supports_inline_queries', False)}")
            
            if not bot_data.get('can_read_all_group_messages', False):
                print("\n⚠️  CRITICAL: Privacy mode is ENABLED!")
                print("💡 To fix this, message @BotFather and run:")
                print("   /setprivacy -> Select your bot -> Disable")
                print("   This allows the bot to read ALL messages in groups")
            
            # Check chat-specific permissions
            chat_member = self.get_chat_member(chat_id, bot_data['id'])
            if chat_member.get('ok'):
                member_data = chat_member['result']
                print(f"\n💬 Chat-specific Permissions:")
                print(f"   🆔 Status: {member_data.get('status', 'unknown')}")
                
                if 'can_send_messages' in member_data:
                    print(f"   💬 Can send messages: {member_data.get('can_send_messages')}")
                if 'can_send_media_messages' in member_data:
                    print(f"   📷 Can send media: {member_data.get('can_send_media_messages')}")
                if 'can_send_other_messages' in member_data:
                    print(f"   📦 Can send other messages: {member_data.get('can_send_other_messages')}")
                if 'can_add_web_page_previews' in member_data:
                    print(f"   🌐 Can add web previews: {member_data.get('can_add_web_page_previews')}")
                
                # Check if bot is admin with proper permissions
                if member_data.get('status') in ['administrator', 'creator']:
                    print("   ✅ Bot is administrator in this chat")
                else:
                    print("   ⚠️  Bot is NOT an administrator")
                    print("   💡 Make the bot an admin for full functionality")
        
        print("="*50 + "\n")
    
    def get_chat_type(self, chat_id):
        """Determine if chat is private, group, or channel"""
        chat_info = self.get_chat_info(chat_id)
        if chat_info.get('ok'):
            return chat_info['result'].get('type')
        return None
    
    def get_all_updates(self, limit=100, offset=0):
        """Get ALL available updates including historical ones"""
        url = f"{self.base_url}/getUpdates"
        all_updates = []
        
        # Check permissions first
        bot_info = self.get_bot_info()
        can_read_all = bot_info.get('result', {}).get('can_read_all_group_messages', False)
        
        if not can_read_all:
            print("⚠️  Warning: Bot privacy mode is enabled")
            print("📝 The bot can only see:")
            print("   - Commands (starting with /)")
            print("   - Replies to its messages")
            print("   - Messages in private chats")
            print("💡 Use /setprivacy -> Disable with @BotFather to see all messages")
        
        try:
            while True:
                params = {
                    'offset': offset,
                    'limit': min(100, limit - len(all_updates)),
                    'timeout': 5
                }
                
                response = requests.get(url, params=params, timeout=self.timeout)
                data = response.json()
                
                if not data['ok'] or not data['result']:
                    break
                
                batch_updates = data['result']
                all_updates.extend(batch_updates)
                offset = batch_updates[-1]['update_id'] + 1
                
                if len(all_updates) >= limit or len(batch_updates) < 100:
                    break
                    
        except Exception as e:
            print(f"Error fetching updates: {e}")
        
        return all_updates
    
    def get_complete_message_history(self, chat_id=None, limit=1000):
        """Get complete message history with permission awareness"""
        all_updates = self.get_all_updates(limit=limit)
        messages = []
        
        bot_info = self.get_bot_info()
        can_read_all = bot_info.get('result', {}).get('can_read_all_group_messages', False)
        
        for update in all_updates:
            message = update.get('message', {}) or update.get('channel_post', {})
            if not message:
                continue
            
            if chat_id and str(message['chat']['id']) != str(chat_id):
                continue
            
            # Check if this is a message the bot can actually see
            if not can_read_all:
                # Bot can only see specific types of messages
                is_visible = (
                    message.get('text', '').startswith('/') or  # Commands
                    'reply_to_message' in message or  # Replies
                    message['chat']['type'] == 'private'  # Private chats
                )
                if not is_visible:
                    continue
            
            messages.append({
                'update_id': update['update_id'],
                'message': message,
                'timestamp': message['date'],
                'is_bot': message.get('from', {}).get('is_bot', False),
                'direction': 'SENT' if message.get('from', {}).get('is_bot', False) else 'RECEIVED'
            })
        
        return messages
    
    def get_latest_message_id(self, chat_id):
        """Get the latest message ID by sending a test message"""
        test_response = self.send_message(chat_id, ".")
        if test_response.get("ok"):
            message_id = test_response['result']['message_id']
            self.delete_message(chat_id, message_id)
            return message_id
        return None
    
    def send_message(self, chat_id, text):
        """Send a message to a chat"""
        url = f"{self.base_url}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        try:
            response = requests.post(url, data=data, timeout=self.timeout)
            return response.json()
        except Exception as e:
            return {'ok': False, 'error': str(e)}
    
    def delete_message(self, chat_id, message_id):
        """Delete a message"""
        url = f"{self.base_url}/deleteMessage"
        data = {"chat_id": chat_id, "message_id": message_id}
        try:
            response = requests.post(url, data=data, timeout=self.timeout)
            return response.json()
        except Exception as e:
            return {'ok': False, 'error': str(e)}
    
    def delete_messages_bulk(self, chat_id, start_message_id, count):
        """Delete multiple messages"""
        processes = []
        for i in range(count):
            message_id = start_message_id - i
            p = multiprocessing.Process(target=self._delete_single_message, 
                                      args=(chat_id, message_id))
            p.start()
            processes.append(p)
        
        for p in processes:
            p.join()
    
    def _delete_single_message(self, chat_id, message_id):
        """Helper method for bulk deletion"""
        result = self.delete_message(chat_id, message_id)
        if result.get("ok"):
            print(f"✓ Deleted message {message_id}")
        elif result.get("description") == "Bad Request: message can't be deleted for everyone":
            print(f"✗ Message {message_id} is too old (>48 hours)")
        else:
            print(f"✗ Failed to delete message {message_id}")
    
    def spam_messages(self, chat_id, message, count=10):
        """Spam messages to a chat"""
        processes = []
        for _ in range(count):
            p = multiprocessing.Process(target=self.send_message, 
                                      args=(chat_id, message))
            p.start()
            processes.append(p)
        
        for p in processes:
            p.join()
    
    def get_file_download_url(self, file_id):
        """Get download URL for a file"""
        url = f"{self.base_url}/getFile"
        params = {'file_id': file_id}
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            data = response.json()
            
            if data['ok']:
                file_path = data['result']['file_path']
                return f"https://api.telegram.org/file/bot{self.token}/{file_path}"
            return None
        except Exception as e:
            print(f"Error getting file URL: {e}")
            return None
    
    def get_file_category(self, filename):
        """Get file category based on extension"""
        if not filename:
            return "unknown"
        
        ext = os.path.splitext(filename)[1].lower()
        for category, extensions in self.file_categories.items():
            if ext in extensions:
                return category
        return "other"
    
    def download_file(self, file_id, filename=None):
        """Download a file from Telegram"""
        download_url = self.get_file_download_url(file_id)
        if not download_url:
            return None
        
        try:
            response = requests.get(download_url, stream=True, timeout=self.timeout)
            if response.status_code == 200:
                if not filename:
                    content_disposition = response.headers.get('content-disposition', '')
                    if 'filename=' in content_disposition:
                        filename = content_disposition.split('filename=')[1].strip('"\'')
                    else:
                        extension = mimetypes.guess_extension(response.headers.get('content-type', '')) or '.bin'
                        filename = f"file_{file_id[:8]}{extension}"
                
                safe_filename = "".join(c for c in filename if c.isalnum() or c in '._- ').rstrip()
                
                # Create category subdirectory
                category = self.get_file_category(safe_filename)
                category_dir = os.path.join(self.download_dir, category)
                os.makedirs(category_dir, exist_ok=True)
                
                filepath = os.path.join(category_dir, safe_filename)
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                return filepath
        except Exception as e:
            print(f"Error downloading file: {e}")
        
        return None
    
    def send_file(self, chat_id, file_path, caption=""):
        """Send a file to a chat"""
        try:
            mime_type = mimetypes.guess_type(file_path)[0]
            file_type = 'document'
            
            if mime_type:
                if 'audio' in mime_type:
                    file_type = 'audio'
                elif 'video' in mime_type:
                    file_type = 'video'
                elif 'image' in mime_type:
                    file_type = 'photo'
            
            file_type_methods = {
                'document': 'sendDocument',
                'photo': 'sendPhoto',
                'audio': 'sendAudio',
                'video': 'sendVideo',
                'animation': 'sendAnimation',
                'voice': 'sendVoice',
                'video_note': 'sendVideoNote'
            }
            
            url = f"{self.base_url}/{file_type_methods[file_type]}"
            with open(file_path, 'rb') as file:
                files = {file_type: file}
                data = {'chat_id': chat_id, 'caption': caption}
                response = requests.post(url, files=files, data=data, timeout=self.timeout)
                return response.json()
        except Exception as e:
            return {'ok': False, 'error': str(e)}
    
    def format_timestamp(self, timestamp):
        """Convert Unix timestamp to readable format"""
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    def parse_dict(self, title, dictionary):
        """Pretty print dictionary"""
        result = f"{title}:\n"
        for key, value in dictionary.items():
            if isinstance(value, dict):
                result += '\n'.join(f"  {k}: {v}" for k, v in value.items())
            else:
                result += f"  {key}: {value}\n"
        return result + "\n"
    
    def display_info(self, chat_id):
        """Display comprehensive bot and chat information"""
        info = {
            "Bot Information": self.get_bot_info(),
            "Chat Information": self.get_chat_info(chat_id),
            "Chat Administrators": self.get_chat_administrators(chat_id),
            "Default Admin Rights": self.get_my_default_admin_rights(chat_id),
            "Bot Commands": self.get_my_commands(chat_id),
            "Member Count": self.get_chat_member_count(chat_id)
        }
        
        for title, data in info.items():
            if data.get('ok'):
                print(self.parse_dict(title, data['result']))
            else:
                print(f"{title}: Error - {data.get('error', 'Unknown error')}")
    
    def display_received_messages(self, chat_id=None, download_files=False, limit=1000):
        """Display received messages with enhanced file information"""
        messages = self.get_complete_message_history(chat_id, limit)
        received_messages = [msg for msg in messages if msg['direction'] == 'RECEIVED']
        
        print(f"\n{' RECEIVED MESSAGES ':=^60}")
        print(f"📊 Total messages found: {len(received_messages)}")
        
        # Check permissions and warn user
        bot_info = self.get_bot_info()
        can_read_all = bot_info.get('result', {}).get('can_read_all_group_messages', False)
        if not can_read_all:
            print("⚠️  Limited visibility: Privacy mode is enabled")
            print("📝 Only showing commands, replies, and private messages")
        
        print("=" * 60)
        
        if not received_messages:
            print("❌ No received messages found.")
            if not can_read_all:
                print("💡 Try disabling privacy mode with @BotFather to see all messages")
            return
        
        for msg_data in received_messages:
            message = msg_data['message']
            user = message.get('from', {})
            timestamp = self.format_timestamp(message['date'])
            
            print(f"🕒 {timestamp}")
            if user:
                print(f"👤 From: {user.get('first_name', '')} {user.get('last_name', '')}")
                if user.get('username'):
                    print(f"   Username: @{user['username']}")
                print(f"   User ID: {user['id']}")
            print(f"   Chat ID: {message['chat']['id']}")
            print(f"   Message ID: {message['message_id']}")
            
            # Handle different content types with enhanced information
            file_info = None
            if 'text' in message:
                print(f"💬 Text: {message['text']}")
            elif 'document' in message:
                doc = message['document']
                file_ext = os.path.splitext(doc.get('file_name', ''))[1].lower()
                file_category = self.get_file_category(doc.get('file_name'))
                print(f"📄 Document: {doc.get('file_name', 'Unnamed')} ({doc.get('file_size', 0)} bytes)")
                print(f"   🗃️  File type: {file_category.upper()}")
                
                download_url = self.get_file_download_url(doc['file_id'])
                if download_url:
                    print(f"   🔗 Download URL: {download_url}")
                
                if download_files:
                    file_info = self.download_file(doc['file_id'], doc.get('file_name'))
            
            elif 'photo' in message:
                print(f"🖼️  Photo: {len(message['photo'])} sizes available")
                largest_photo = max(message['photo'], key=lambda x: x['file_size'])
                download_url = self.get_file_download_url(largest_photo['file_id'])
                if download_url:
                    print(f"   🔗 Download URL: {download_url}")
                
                if download_files:
                    file_info = self.download_file(largest_photo['file_id'], f"photo_{message['message_id']}.jpg")
            
            if file_info:
                print(f"   📥 Downloaded: {file_info}")
            
            print("-" * 40)
    
    def display_sent_messages(self, chat_id=None, limit=1000):
        """Display messages sent by the bot"""
        messages = self.get_complete_message_history(chat_id, limit)
        sent_messages = [msg for msg in messages if msg['direction'] == 'SENT']
        
        print(f"\n{' SENT MESSAGES ':=^60}")
        print(f"📊 Total messages found: {len(sent_messages)}")
        print("=" * 60)
        
        if not sent_messages:
            print("🤖 No messages sent by the bot found")
            return
        
        for msg_data in sent_messages:
            message = msg_data['message']
            user = message['from']
            timestamp = self.format_timestamp(message['date'])
            
            print(f"🕒 {timestamp}")
            print(f"🤖 Sent by: {user.get('first_name', 'Bot')}")
            print(f"   To Chat ID: {message['chat']['id']}")
            print(f"   Message ID: {message['message_id']}")
            
            if 'text' in message:
                print(f"💬 Text: {message['text']}")
            elif 'photo' in message:
                print(f"🖼️  Photo sent")
            elif 'document' in message:
                doc = message['document']
                print(f"📄 Document: {doc.get('file_name', 'Unnamed')}")
            
            print("-" * 40)
    
    def display_all_messages(self, chat_id=None, limit=1000):
        """Display both received and sent messages in chronological order"""
        messages = self.get_complete_message_history(chat_id, limit)
        
        print(f"\n{' ALL MESSAGES ':=^60}")
        print(f"📊 Total messages: {len(messages)}")
        
        # Check permissions
        bot_info = self.get_bot_info()
        can_read_all = bot_info.get('result', {}).get('can_read_all_group_messages', False)
        if not can_read_all:
            print("⚠️  Limited visibility: Privacy mode is enabled")
        
        print("=" * 60)
        
        if not messages:
            print("❌ No messages found.")
            return
        
        # Sort by timestamp
        sorted_messages = sorted(messages, key=lambda x: x['timestamp'])
        
        for msg_data in sorted_messages:
            message = msg_data['message']
            user = message['from']
            timestamp = self.format_timestamp(message['date'])
            is_bot = msg_data['is_bot']
            
            direction = "➡️ SENT" if is_bot else "⬅️ RECEIVED"
            user_info = f"🤖 {user.get('first_name', 'Bot')}" if is_bot else f"👤 {user.get('first_name', '')}"
            
            print(f"{direction} | 🕒 {timestamp}")
            print(f"   {user_info}")
            if not is_bot and user.get('username'):
                print(f"   Username: @{user['username']}")
            print(f"   Chat ID: {message['chat']['id']}")
            print(f"   Message ID: {message['message_id']}")
            
            if 'text' in message:
                print(f"💬 {message['text']}")
            else:
                content_type = next((key for key in ['photo', 'document', 'audio', 'video', 'sticker'] if key in message), 'unknown')
                print(f"📦 {content_type.capitalize()} content")
            
            print("-" * 40)
    
    def download_all_messages(self, chat_id, output_dir="message_archive"):
        """Download all messages with complete metadata"""
        os.makedirs(output_dir, exist_ok=True)
        messages = self.get_complete_message_history(chat_id, limit=10000)
        
        # Save as JSON
        with open(os.path.join(output_dir, "messages.json"), 'w') as f:
            json.dump(messages, f, indent=2, default=str)
        
        # Save as text
        with open(os.path.join(output_dir, "messages.txt"), 'w') as f:
            for msg in messages:
                f.write(f"Message ID: {msg['message']['message_id']}\n")
                f.write(f"Timestamp: {self.format_timestamp(msg['message']['date'])}\n")
                f.write(f"Direction: {msg['direction']}\n")
                if 'text' in msg['message']:
                    f.write(f"Text: {msg['message']['text']}\n")
                f.write("\n")
        
        print(f"📁 Messages archived to {output_dir}/")
        return len(messages)
    
    def monitor_messages(self, chat_id=None):
        """Real-time message monitoring"""
        offset = None
        print("🔍 Monitoring for new messages... (Ctrl+C to stop)")
        
        # Check permissions
        bot_info = self.get_bot_info()
        can_read_all = bot_info.get('result', {}).get('can_read_all_group_messages', False)
        if not can_read_all:
            print("⚠️  Limited monitoring: Privacy mode is enabled")
            print("📝 Only monitoring commands, replies, and private messages")
        
        try:
            while True:
                url = f"{self.base_url}/getUpdates?timeout=30"
                if offset:
                    url += f"&offset={offset}"
                
                response = requests.get(url, timeout=35)
                data = response.json()
                
                if data.get('ok') and data.get('result'):
                    for update in data['result']:
                        print("New Update:")
                        pprint.pprint(update, indent=2, width=80)
                        offset = update['update_id'] + 1
                
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
    
    def interactive_menu(self, chat_id):
        """Interactive menu system with permission checking"""
        # Check permissions first
        self.check_bot_permissions(chat_id)
        
        while True:
            print("\n" + "="*50)
            print("          THREATY BOT - MAIN MENU")
            print("="*50)
            print("1. 📋 Display Bot & Chat Information")
            print("2. 📥 Show Received Messages")
            print("3. 📤 Show Sent Messages")
            print("4. 📋 Show All Messages")
            print("5. 💾 Download All Messages (Archive)")
            print("6. 🔍 Monitor Messages in Real-time")
            print("7. 📩 Send Message")
            print("8. 🚫 Spam Messages")
            print("9. 🗑️  Delete Messages")
            print("10. 📤 Send File")
            print("11. 📊 Get Message Count")
            print("12. 🔄 Check Permissions Again")
            print("13. ❌ Exit")
            print("="*50)
            
            choice = input("\nEnter your choice (1-13): ").strip()
            
            if choice == '1':
                self.display_info(chat_id)
            
            elif choice == '2':
                limit = input("Limit (default 1000): ").strip() or "1000"
                download = input("Download files? (y/n): ").strip().lower() == 'y'
                self.display_received_messages(chat_id, download, int(limit))
            
            elif choice == '3':
                limit = input("Limit (default 1000): ").strip() or "1000"
                self.display_sent_messages(chat_id, int(limit))
            
            elif choice == '4':
                limit = input("Limit (default 1000): ").strip() or "1000"
                self.display_all_messages(chat_id, int(limit))
            
            elif choice == '5':
                count = self.download_all_messages(chat_id)
                print(f"Downloaded {count} messages to archive")
            
            elif choice == '6':
                self.monitor_messages(chat_id)
            
            elif choice == '7':
                message = input("Enter message to send: ")
                result = self.send_message(chat_id, message)
                pprint.pprint(result)
            
            elif choice == '8':
                message = input("Enter spam message: ")
                count = input("Number of messages (default 10): ").strip() or "10"
                self.spam_messages(chat_id, message, int(count))
                print("Spamming completed!")
            
            elif choice == '9':
                latest_id = self.get_latest_message_id(chat_id)
                if latest_id:
                    count = input(f"Number to delete (latest is {latest_id}): ").strip() or "10"
                    self.delete_messages_bulk(chat_id, latest_id, int(count))
                else:
                    print("Could not get latest message ID")
            
            elif choice == '10':
                file_path = input("Enter file path: ").strip()
                if os.path.exists(file_path):
                    caption = input("Caption (optional): ").strip()
                    result = self.send_file(chat_id, file_path, caption)
                    pprint.pprint(result)
                else:
                    print("File not found!")
            
            elif choice == '11':
                latest_id = self.get_latest_message_id(chat_id)
                if latest_id:
                    print(f"Approximate message count: {latest_id}")
                else:
                    print("Could not get message count")
            
            elif choice == '12':
                self.check_bot_permissions(chat_id)
            
            elif choice == '13':
                print("Goodbye!")
                break
            
            else:
                print("Invalid choice!")

def load_env_file():
    """Load environment variables from .env file"""
    env_vars = {}
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ Error: .env file not found!")
        print("💡 Create a .env file with:")
        print("   TELEGRAM_BOT_TOKEN=your_bot_token_here")
        print("   TELEGRAM_CHAT_ID=your_chat_id_here")
        sys.exit(1)
    
    print("📁 Loading environment from: .env")
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip().strip('"').strip("'")
    
    return env_vars

def main():
    # Load environment variables
    env_vars = load_env_file()
    
    # Get configuration
    token = env_vars.get('TELEGRAM_BOT_TOKEN')
    chat_id = env_vars.get('TELEGRAM_CHAT_ID')
    
    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN is required in .env file")
        sys.exit(1)
    
    if not chat_id:
        print("❌ Error: TELEGRAM_CHAT_ID is required in .env file")
        sys.exit(1)
    
    # Initialize bot
    bot = ThreatyBot(token)
    
    # Test connection
    bot_info = bot.get_bot_info()
    if not bot_info.get('ok'):
        print(f"❌ Error: Invalid bot token")
        sys.exit(1)
    
    print(f"🤖 Connected to: {bot_info['result']['first_name']} (@{bot_info['result']['username']})")
    print(f"💬 Chat ID: {chat_id}")
    
    # Start interactive menu
    bot.interactive_menu(chat_id)

if __name__ == "__main__":
    main()