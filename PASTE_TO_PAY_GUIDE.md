# 📋 HƯỚNG DẪN SỬ DỤNG PASTE TO PAY

## 🎯 Tính năng mới: Paste to Pay

TECHNOBOT giờ đây có thêm tính năng **Paste to Pay** - cho phép bạn chuyển tiền nhanh chóng chỉ bằng cách copy/paste thông tin!

## 🚀 Cách sử dụng

### Bước 1: Copy thông tin chuyển tiền
Copy bất kỳ đoạn text nào chứa thông tin chuyển tiền, ví dụ:
- `"Chuyển khoản 500k qua Vietcombank số tk 1234567890 nội dung thanh toán hóa đơn"`
- `"Chuyển 1.000.000 VND cho Techcombank 9876543210 trả nợ"`
- `"Transfer 2000000 to BIDV account 1111222233 for salary"`

### Bước 2: Nhấn nút Paste to Pay
- Tìm nút **📋 Paste to Pay** ở góc phải trên cùng (bên cạnh logo TECHNOBOT)
- Click vào nút này

### Bước 3: Xác nhận giao dịch
- Nếu thông tin hợp lệ → Popup xác nhận sẽ xuất hiện
- Kiểm tra thông tin: Ngân hàng, Số TK, Số tiền, Nội dung
- Click **✅ Xác nhận chuyển tiền** hoặc **❌ Hủy giao dịch**

## 📊 Các trường hợp xử lý

### ✅ Case 1: Thành công
```json
{
    "raw_output": {
        "bank_name": "Vietcombank",
        "bank_acc_number": "1234567890", 
        "amount": "500000",
        "content": "thanh toan"
    },
    "time_s": 1.0
}
```
→ Hiển thị popup xác nhận chuyển tiền

### ⚠️ Case 2: Không nhận diện được
```json
{
    "raw_output": null,
    "time_s": 1.1  
}
```
→ Hiển thị: "TECHNOBOT chưa nhận được thông tin chuyển tiền hợp lệ."

## 🔧 API Integration

- **Endpoint**: `http://54.81.13.123/extract`
- **Method**: POST
- **Payload**: `{"text": "clipboard_content"}`
- **Timeout**: 10 giây

## 🎨 UI/UX Features

- **Nút Paste to Pay**: Màu xanh lá gradient, hover effect
- **Popup xác nhận**: Dark theme, Techcombank branding
- **Thông báo lỗi**: Hiển thị rõ ràng, dễ hiểu
- **Format số tiền**: Tự động format với dấu chấm phân cách

## 🔒 Bảo mật

- Chỉ truy cập clipboard khi user click nút
- Không lưu trữ thông tin clipboard
- API call có timeout để tránh treo
- Xác nhận 2 bước trước khi chuyển tiền

## 🧪 Test

Chạy file test để kiểm tra:
```bash
python test_paste_to_pay.py
```

---
**🤖 TECHNOBOT - Ngân hàng số thông minh** 