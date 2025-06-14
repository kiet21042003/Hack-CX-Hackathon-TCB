#!/usr/bin/env python3
"""
TECHNOBOT Startup Script - Safe for Corporate Environment
Tối ưu cho môi trường công ty với Trellix Endpoint Security
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_requirements():
    """Kiểm tra các yêu cầu cần thiết"""
    print("🔍 Kiểm tra môi trường...")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Cần Python 3.11 trở lên")
        return False
    
    # Check required files
    required_files = [
        "technobot_chatbot.py",
        "output/customer_recommendations_output.csv",
        "data/metadata_user.csv"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Không tìm thấy file: {file}")
            return False
    
    print("✅ Môi trường OK")
    return True

def install_dependencies():
    """Cài đặt dependencies nếu cần"""
    print("📦 Kiểm tra dependencies...")
    
    try:
        import gradio
        import pandas
        import requests
        print("✅ Dependencies đã có sẵn")
        return True
    except ImportError:
        print("⚠️ Cần cài đặt dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Đã cài đặt dependencies")
            return True
        except subprocess.CalledProcessError:
            print("❌ Lỗi cài đặt dependencies")
            return False

def find_available_port(start_port=7861):
    """Tìm port khả dụng"""
    import socket
    
    for port in range(start_port, start_port + 10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                print(f"✅ Tìm thấy port khả dụng: {port}")
                return port
        except OSError:
            continue
    
    print("❌ Không tìm thấy port khả dụng")
    return None

def start_technobot_safe():
    """Khởi động TECHNOBOT an toàn cho môi trường công ty"""
    print("🤖 TECHNOBOT - Corporate Safe Startup")
    print("=" * 50)
    
    # Check environment
    if not check_requirements():
        input("Nhấn Enter để thoát...")
        return
    
    # Install dependencies
    if not install_dependencies():
        input("Nhấn Enter để thoát...")
        return
    
    # Find available port
    port = find_available_port()
    if not port:
        input("Nhấn Enter để thoát...")
        return
    
    print(f"🚀 Khởi động TECHNOBOT tại port {port}...")
    print("🔒 Chế độ an toàn cho môi trường công ty")
    print("📍 Chỉ chạy local, không tạo share link")
    print("-" * 50)
    
    # Set environment variables for safe mode
    os.environ['GRADIO_SERVER_PORT'] = str(port)
    os.environ['GRADIO_SERVER_NAME'] = '127.0.0.1'
    os.environ['GRADIO_SHARE'] = 'False'
    
    # Start the application
    try:
        # Import and modify the app for safe startup
        import technobot_chatbot
        
        # Override launch parameters for corporate safety
        original_launch = technobot_chatbot.app.launch
        
        def safe_launch(*args, **kwargs):
            # Force safe parameters
            kwargs.update({
                'server_name': '127.0.0.1',
                'server_port': port,
                'share': False,
                'show_error': True,
                'inbrowser': True,
                'quiet': False
            })
            return original_launch(*args, **kwargs)
        
        technobot_chatbot.app.launch = safe_launch
        
        print(f"✅ TECHNOBOT đang chạy tại: http://127.0.0.1:{port}")
        print("🌐 Trình duyệt sẽ tự động mở...")
        print("⚠️ Để dừng: Nhấn Ctrl+C")
        print("=" * 50)
        
        # Start the app
        technobot_chatbot.app.launch()
        
    except KeyboardInterrupt:
        print("\n🛑 TECHNOBOT đã dừng")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        input("Nhấn Enter để thoát...")

if __name__ == "__main__":
    start_technobot_safe() 