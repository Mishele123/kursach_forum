# 🧪 Hướng dẫn Test Backend API

## 🚀 Khởi động Server

1. Mở terminal và chạy:
```powershell
cd backend
python -m uvicorn main:get_app --host 0.0.0.0 --port 8000 --reload
```

2. Server sẽ chạy tại: `http://localhost:8000`

## 📚 Xem API Documentation

### 🎯 Cách 1: Swagger UI (Khuyên dùng)
Mở trình duyệt và truy cập:
```
http://localhost:8000/docs
```

**Tính năng:**
- ✅ Xem tất cả endpoints
- ✅ Test API trực tiếp từ trình duyệt
- ✅ Xem request/response models
- ✅ Thử nghiệm mà không cần viết code

**Cách sử dụng:**
1. Chọn một endpoint (ví dụ: `POST /auth/register`)
2. Click "Try it out"
3. Nhập dữ liệu JSON vào Request body
4. Click "Execute"
5. Xem kết quả ở phần Response

### 📖 Cách 2: ReDoc
```
http://localhost:8000/redoc
```
- Giao diện đẹp, dễ đọc
- Phù hợp để đọc documentation

### 🏠 Cách 3: Root Endpoint
```
http://localhost:8000/
```
- Xem thông tin tổng quan
- Danh sách tất cả endpoints

### 🔧 Cách 4: OpenAPI JSON
```
http://localhost:8000/openapi.json
```
- Schema API đầy đủ
- Dùng để tích hợp với tools khác

## 📝 Test bằng HTML Interface

Mở file `test_browser.html` trong trình duyệt để xem giao diện đẹp với:
- Links nhanh đến tất cả documentation
- Danh sách endpoints với mô tả
- Hướng dẫn sử dụng

## 🧪 Các Endpoints Chính

### 👤 Authentication & Profile

#### Đăng ký user mới (US1)
```http
POST /auth/register
Content-Type: application/json

{
  "username": "cyclist123",
  "password": "securepass123"
}
```

#### Đăng nhập (US1)
```http
POST /auth/login
Content-Type: application/json

{
  "username": "cyclist123",
  "password": "securepass123"
}
```

#### Xem profile (US2)
```http
GET /auth/me
```

#### Cập nhật profile (US2)
```http
PUT /auth/me
Content-Type: application/json

{
  "city": "Moscow",
  "discipline": "MTB",
  "interests": "Downhill, Cross-country",
  "bio": "Passionate mountain biker"
}
```

### 📝 Posts

#### Tạo bài viết (US3)
```http
POST /posts
Content-Type: application/json

{
  "title": "My first mountain ride",
  "text": "Today I conquered a 50km trail!",
  "category": "ride_report",
  "photo_url": "https://example.com/photo.jpg"
}
```

#### Lấy danh sách bài viết (US4)
```http
GET /posts?limit=20&offset=0
```

#### Xem chi tiết bài viết
```http
GET /posts/1
```

### 🚲 Bikes

#### Thêm xe đạp (US5)
```http
POST /bikes
Content-Type: application/json

{
  "brand": "Trek",
  "model": "Fuel EX 9.8",
  "year": 2024
}
```

#### Xem danh sách xe của mình (US5)
```http
GET /bikes/my-bikes
```

## ✅ Kết quả Test

### ✅ Các chức năng hoạt động tốt:
- ✅ User registration (POST /auth/register) - 201 Created
- ✅ User login (POST /auth/login) - 200 OK
- ✅ Get profile (GET /auth/me) - 200 OK
- ✅ Update profile (PUT /auth/me) - 200 OK
- ✅ Get posts (GET /posts) - 200 OK
- ✅ Add bike (POST /bikes) - 201 Created
- ✅ Get bikes (GET /bikes/my-bikes) - 200 OK

### ⚠️ Các vấn đề đã biết:
- ⚠️ POST /posts đôi khi trả về 422 (validation error) - cần kiểm tra DTO validation
- ⚠️ Authentication hiện tại dùng hardcoded user_id=1 (cần implement JWT sau)
- ⚠️ Password chưa được hash (cần implement password hashing)

## 🛠️ Kiến trúc Backend

### Clean Architecture
```
backend/
├── auth/           # Authentication & User module
│   ├── http.py           # HTTP endpoints
│   ├── user_entity.py    # Domain model
│   ├── user_dto.py       # Data Transfer Objects
│   ├── user_interactor.py # Business logic
│   ├── user_interfaces.py # Repository interface
│   ├── in_memory.py      # In-memory storage
│   └── user_mapper.py    # DTO <-> Entity mapping
├── posts/          # Posts module
│   ├── http.py
│   ├── post_entity.py
│   ├── post_dto.py
│   └── post_storage.py
├── bikes/          # Bikes module
│   ├── http.py
│   ├── bike_entity.py
│   ├── bike_dto.py
│   └── bike_storage.py
├── ioc.py          # Dependency Injection (Dishka)
└── main.py         # FastAPI application
```

### Technologies
- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **Dishka**: Dependency injection
- **Pydantic**: Data validation
- **Python 3.14**: Language

## 🎯 Sprint 1 User Stories

- ✅ **US1**: Регистрация и аутентификация пользователей
- ✅ **US2**: Редактирование профиля пользователя
- ✅ **US3**: Создание публикаций
- ✅ **US4**: Просмотр ленты публикаций
- ✅ **US5**: Добавление велосипедов в профиль

## 📊 Server Logs

Server logs hiển thị các requests thành công:
```
INFO: 127.0.0.1 - "POST /auth/register HTTP/1.1" 201 Created
INFO: 127.0.0.1 - "POST /auth/login HTTP/1.1" 200 OK
INFO: 127.0.0.1 - "GET /auth/me HTTP/1.1" 200 OK
INFO: 127.0.0.1 - "PUT /auth/me HTTP/1.1" 200 OK
INFO: 127.0.0.1 - "GET /posts?limit=5 HTTP/1.1" 200 OK
INFO: 127.0.0.1 - "POST /bikes HTTP/1.1" 201 Created
INFO: 127.0.0.1 - "GET /bikes/my-bikes HTTP/1.1" 200 OK
```

## 🔍 Debug & Troubleshooting

### Server không khởi động được?
```powershell
# Kiểm tra port 8000 có bị chiếm không
netstat -ano | findstr :8000

# Cài đặt lại dependencies
pip install -r requirements.txt
```

### API trả về lỗi 422?
- Kiểm tra request body có đúng format không
- Xem chi tiết lỗi trong response body
- Kiểm tra required fields trong DTO

### Không connect được tới server?
- Đảm bảo server đang chạy
- Kiểm tra URL: `http://localhost:8000` (không phải https)
- Kiểm tra firewall settings

## 📞 Support

Nếu gặp vấn đề, kiểm tra:
1. Server logs trong terminal
2. Response body từ API
3. Swagger UI để xem request/response schema
