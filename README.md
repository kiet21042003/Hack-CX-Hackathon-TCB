# 🤖 TECHNOBOT - Hệ thống Phân tích Tín dụng Thông minh

## 📋 Giới thiệu

TECHNOBOT là một chatbot AI thông minh được phát triển cho Techcombank, tích hợp khả năng phân tích khách hàng và đưa ra khuyến nghị sản phẩm tài chính phù hợp.

## ✨ Tính năng chính

- 🔍 **Phân tích SHAP**: Giải thích chi tiết các yếu tố ảnh hưởng đến quyết định
- 🤖 **AI Chatbot**: Tư vấn thông minh với Gemini AI và ChatGPT  
- 📊 **Giao diện trực quan**: Dễ sử dụng cho cả chuyên gia và khách hàng
- 🔒 **Minh bạch**: Mỗi quyết định đều được giải thích rõ ràng
- 🎯 **Khuyến nghị sản phẩm**: Đề xuất sản phẩm tài chính phù hợp cho từng khách hàng

## 🚀 Cài đặt

### 1. Clone repository
```bash
git clone <repository-url>
cd technobot-chatbot
```

### 2. Cài đặt Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Chuẩn bị dữ liệu
Đảm bảo các file sau tồn tại:
- `output/customer_recommendations_output.csv`: Dữ liệu khách hàng và khuyến nghị
- `data/metadata_user.csv`: Metadata mô tả các trường dữ liệu
- `logo.png`: Logo TECHNOBOT (tùy chọn)

### 4. Chạy ứng dụng
```bash
python technobot_chatbot.py
```

Ứng dụng sẽ chạy tại `http://localhost:7860`

## 📚 Hướng dẫn sử dụng

### 1. Chọn khách hàng
- Sử dụng dropdown để chọn khách hàng từ danh sách 46 hồ sơ
- Thông tin khách hàng sẽ hiển thị bên trái

### 2. Xem khuyến nghị sản phẩm
- 3 sản phẩm được đề xuất sẽ hiển thị dưới dạng nút bấm
- Click vào nút để bắt đầu tư vấn về sản phẩm đó

### 3. Chat với TECHNOBOT
- Nhập câu hỏi vào ô chat
- Bot sẽ trả lời dựa trên API text2action
- Hỗ trợ 2 loại phản hồi:
  - **ask**: Trả lời thông thường
  - **transfer_money**: Thực hiện giao dịch chuyển tiền

## 🎨 Thiết kế

### Màu sắc thương hiệu
- **TECH**: #E30613 (Đỏ Techcombank)
- **NOBOT**: #000000 (Đen)
- **Background**: Gradient tối hiện đại

### Font chữ
- **Header**: Futura (hoặc fallback)
- **Body**: Nunito (Google Font)

## 🔧 API Integration

### Text2Action API
- **URL**: `http://54-87-106-218.compute-1.amazonaws.com/api/text2action`
- **Method**: POST
- **Headers**: 
  - `Content-Type: application/json`
  - `accept: application/json`

#### Request Format
```json
{
  "text": "Chào bạn",
  "message_history": ["User: ...", "Assistant: ..."] // Optional
}
```

#### Response Format
```json
{
  "action": "ask|transfer_money",
  "payload": {
    "answer": "...",  // For ask action
    "amount": 50000,  // For transfer_money action
    "recipient_account": "...",
    "bank_name": "...",
    "recipient_name": "...",
    "memo": "..."
  }
}
```

## 📊 Cấu trúc dữ liệu

### Customer Data (customer_recommendations_output.csv)
- `user_id`: ID khách hàng
- `age`: Tuổi
- `occupation`: Nghề nghiệp  
- `marital_status`: Tình trạng hôn nhân
- `recommended_product_name_1/2/3`: Tên sản phẩm được đề xuất
- `recommendation_success`: Trạng thái khuyến nghị
- `adopted_products_count`: Số sản phẩm đã sử dụng

## 🛠️ Technical Stack

- **Frontend**: Gradio
- **Backend**: Python
- **Data Processing**: Pandas
- **API Calls**: Requests
- **Styling**: Custom CSS with Techcombank branding

## 📝 Yêu cầu hệ thống

- **Python**: 3.11+
- **RAM**: 2GB+
- **Disk**: 1GB+
- **Internet**: Cần kết nối để gọi API

## 🐛 Troubleshooting

### Lỗi thường gặp

1. **ModuleNotFoundError**: Chạy `pip install -r requirements.txt`
2. **FileNotFoundError**: Kiểm tra đường dẫn file dữ liệu
3. **API Timeout**: Kiểm tra kết nối internet và trạng thái API

### Debug mode
Chạy với debug để xem chi tiết lỗi:
```bash
python technobot_chatbot.py --debug
```

## 📞 Hỗ trợ

Nếu gặp vấn đề, vui lòng liên hệ:
- Email: support@techcombank.com
- Phone: 1800 588 822

## 📜 License

© 2024 Vietnam Technological and Commercial Joint-Stock Bank. All rights reserved. 