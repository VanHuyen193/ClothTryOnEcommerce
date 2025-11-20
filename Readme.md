# Cloth Try-On Ecommerce

Dự án website thương mại điện tử bán quần áo, xây dựng bằng **Python 3.12** và **Django**, hỗ trợ quản lý sản phẩm, giỏ hàng, đơn hàng và tài khoản người dùng.

## 🧩 Tính năng chính

- 👤 **Quản lý tài khoản**

  - Đăng ký / đăng nhập / đăng xuất
  - Cập nhật thông tin người dùng

- 🛍️ **Danh mục & sản phẩm**

  - Danh mục sản phẩm quần áo
  - Xem chi tiết sản phẩm

- 🛒 **Giỏ hàng & đặt hàng**

  - Thêm / xóa / cập nhật sản phẩm trong giỏ
  - Tạo đơn hàng từ giỏ hàng

- 📦 **Quản lý đơn hàng**
  - Lưu thông tin đơn hàng
  - Xem lịch sử đặt hàng (tùy triển khai trong project)

> 📌 Một số tính năng chi tiết có thể xem trực tiếp trong các app Django: `store`, `carts`, `orders`, `accounts`, v.v.

---

## 🏗 Công nghệ sử dụng

- [Python 3.12.x](https://www.python.org/)
- [Django](https://www.djangoproject.com/)
- Các thư viện khác được liệt kê trong file **`requirements.txt`**

---

## 📁 Cấu trúc thư mục (chính)

```text
ClothTryOnEcommerce/
├── accounts/        # App quản lý tài khoản người dùng
├── carts/           # App giỏ hàng
├── category/        # App danh mục sản phẩm
├── orders/          # App quản lý đơn hàng
├── store/           # App sản phẩm / cửa hàng
├── templates/       # Templates HTML
├── static/          # File tĩnh (CSS, JS, images)
├── media/photos/    # Ảnh sản phẩm / media upload
├── mysite/          # Cấu hình project Django (settings, urls, wsgi, ...)
├── manage.py        # File chạy lệnh Django
├── requirements.txt # Danh sách dependencies
└── .env-sample      # Mẫu file môi trường
```

---

## 💻 Yêu cầu hệ thống

- Python **3.12.x**
- `pip` (Python package manager)
- Git (để clone repo)
- Hệ điều hành:

  - Windows 10/11 (được hướng dẫn bên dưới)
  - Hoặc macOS / Linux (chạy tương tự, chỉ khác lệnh kích hoạt venv)

---

## 🚀 Hướng dẫn cài đặt & chạy project

### 1. Clone source code

```bash
git clone https://github.com/VanHuyen193/ClothTryOnEcommerce.git
cd ClothTryOnEcommerce
```

---

### 2. Tạo & kích hoạt môi trường ảo

#### Trên **Windows**

```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo
venv\Scripts\activate
```

#### Trên **macOS / Linux** (tham khảo thêm)

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Cài đặt thư viện

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

### 4. Cấu hình biến môi trường

Project sử dụng file `.env`. Bạn cần:

```bash
# Tạo file .env từ file mẫu
cp .env-sample .env   # Trên macOS / Linux

# Hoặc trên Windows (PowerShell)
copy .env-sample .env
```

Sau đó mở file `.env` và chỉnh sửa các giá trị tương ứng (ví dụ: `SECRET_KEY`, `DEBUG`, thông tin database nếu có, v.v.).

---

### 5. Chạy migrate database

```bash
python manage.py migrate
```

(Tùy cấu hình, mặc định thường sử dụng SQLite, không cần cài thêm DB server.)

---

### 6. Tạo tài khoản admin (tùy chọn nhưng nên làm)

```bash
python manage.py createsuperuser
```

Làm theo hướng dẫn trên màn hình để tạo username/password.

---

### 7. Chạy server development

```bash
python manage.py runserver
```

Mặc định server sẽ chạy tại:

- [http://127.0.0.1:8000/](http://127.0.0.1:8000/) hoặc
- [http://localhost:8000/](http://localhost:8000/)

Mở trình duyệt và truy cập để xem website.

---

## 🧪 Chạy test (nếu có)

Nếu trong project đã định nghĩa test:

```bash
python manage.py test
```

---

## ✉️ Liên hệ / Đóng góp

- Gmail: 22010511@st.phenikaa-uni.edu.vn, 22010329@st.phenikaa-uni.edu.vn, 22010033@st.phenikaa-uni.edu.vn
