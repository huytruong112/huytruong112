# 💻 Chạy Admin Panel trên Windows

## 🚀 CÁCH NHANH NHẤT (3 Bước)

### Bước 1: Cài đặt Python
1. Download Python từ: https://www.python.org/downloads/
2. **QUAN TRỌNG:** Check ☑️ "Add Python to PATH"
3. Click "Install Now"

### Bước 2: Cài đặt Dependencies
```batch
Cách 1: Double click file này:
INSTALL_WINDOWS.bat

Cách 2: Hoặc chạy trong Command Prompt:
pip install -r requirements.txt
```

### Bước 3: Chạy Server
```batch
Double click file:
START_WINDOWS.bat
```

Mở browser: **http://localhost:5000**

---

## 📋 YÊU CẦU HỆ THỐNG

- ✅ Windows 10/11 (hoặc Windows 7+)
- ✅ Python 3.8+ 
- ✅ 2GB RAM (tối thiểu)
- ✅ 500MB disk space
- ✅ Internet connection

---

## 🔧 CÀI ĐẶT CHI TIẾT

### Option 1: Dùng Scripts (Khuyến nghị)

#### 1. Cài đặt:
```batch
INSTALL_WINDOWS.bat
```

#### 2. Test:
```batch
TEST_WINDOWS.bat
```

#### 3. Chạy:
```batch
START_WINDOWS.bat
```

### Option 2: Manual Installation

#### 1. Mở Command Prompt (cmd)
```
Nhấn Win+R
Gõ: cmd
Enter
```

#### 2. Navigate đến thư mục
```batch
cd C:\path\to\workspace
```

#### 3. Cài đặt dependencies
```batch
pip install -r requirements.txt
```

#### 4. Chạy server
```batch
python admin_panel.py
```

---

## 🌐 TRUY CẬP

### Từ máy cùng:
```
http://localhost:5000
```

### Từ máy khác trong mạng:
```
http://YOUR_PC_IP:5000
```

**Xem IP của bạn:**
```batch
ipconfig
```
Tìm "IPv4 Address"

---

## 🔥 FIREWALL WINDOWS

Nếu không truy cập được từ máy khác:

### Cách 1: Dùng GUI
1. Mở **Windows Defender Firewall**
2. Click **Advanced settings**
3. **Inbound Rules** → **New Rule**
4. Type: **Port**
5. Port: **5000**
6. Action: **Allow**
7. Name: **Admin Panel**

### Cách 2: Dùng Command (Admin)
```batch
Mở Command Prompt as Administrator:
netsh advfirewall firewall add rule name="Admin Panel" dir=in action=allow protocol=TCP localport=5000
```

---

## 🐛 TROUBLESHOOTING

### Lỗi: "Python not found"
**Fix:**
1. Cài đặt Python từ python.org
2. Check "Add to PATH" khi cài
3. Restart Command Prompt

### Lỗi: "pip not found"
**Fix:**
```batch
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

### Lỗi: "Permission denied"
**Fix:**
- Chạy Command Prompt as Administrator
- Hoặc: `pip install --user -r requirements.txt`

### Lỗi: "Port 5000 already in use"
**Fix:**
```batch
REM Tìm process đang dùng port 5000
netstat -ano | findstr :5000

REM Kill process (thay PID)
taskkill /PID <PID> /F
```

### Trang trắng trong browser
**Fix:**
1. **Clear cache:** Ctrl+Shift+Delete
2. **Incognito mode:** Ctrl+Shift+N
3. Check URL: `http://localhost:5000`
4. Check firewall không block

---

## 📊 CHECK STATUS

### Kiểm tra server đang chạy:
```batch
tasklist | findstr python
```

### Kiểm tra port:
```batch
netstat -ano | findstr :5000
```

### Test connection:
```batch
curl http://localhost:5000
```
Hoặc mở browser vào: http://localhost:5000

---

## 🎯 WINDOWS-SPECIFIC TIPS

### 1. Virtual Environment (Optional)
```batch
REM Tạo venv
python -m venv venv

REM Activate
venv\Scripts\activate

REM Install
pip install -r requirements.txt

REM Run
python admin_panel.py
```

### 2. Run as Service (Advanced)
Dùng **NSSM** (Non-Sucking Service Manager):
```batch
REM Download NSSM from nssm.cc
nssm install AdminPanel "C:\path\to\python.exe" "C:\path\to\admin_panel.py"
nssm start AdminPanel
```

### 3. Auto-start on Boot
Tạo shortcut trong:
```
C:\Users\YourName\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```

### 4. Run in Background
```batch
start /B python admin_panel.py > admin_panel.log 2>&1
```

---

## 📝 BATCH SCRIPTS

### START_WINDOWS.bat
- Kiểm tra Python
- Kiểm tra dependencies
- Start server
- Hiển thị thông tin đăng nhập

### INSTALL_WINDOWS.bat
- Kiểm tra Python
- Cài đặt dependencies
- Tạo .env file

### TEST_WINDOWS.bat
- Test tất cả components
- Kiểm tra 8 tests
- Hiển thị kết quả

---

## 🎨 GUI OPTIONS (Advanced)

### Option 1: PyInstaller (Tạo .exe)
```batch
pip install pyinstaller
pyinstaller --onefile --windowed admin_panel.py
```

### Option 2: Auto-py-to-exe (GUI Tool)
```batch
pip install auto-py-to-exe
auto-py-to-exe
```

---

## 🔒 SECURITY TRÊN WINDOWS

### 1. Windows Defender
- Thêm folder vào exclusions nếu bị scan chậm

### 2. UAC (User Account Control)
- Có thể cần run as Administrator

### 3. Antivirus
- Whitelist folder nếu bị block

---

## 💡 PERFORMANCE TIPS

### 1. Disable Windows Search indexing
```
Folder → Properties → Advanced → 
Uncheck "Allow files in this folder to have contents indexed"
```

### 2. Use SSD
- Chạy nhanh hơn nhiều

### 3. Close unused apps
- Chrome ăn RAM nhiều

---

## 🎯 DEVELOPMENT MODE

### Run with auto-reload:
```batch
set FLASK_ENV=development
python admin_panel.py
```

### Run with debug:
```batch
set DEBUG=True
python admin_panel.py
```

---

## 📱 ACCESS FROM PHONE

1. Get PC IP: `ipconfig`
2. Connect phone to same WiFi
3. Open phone browser
4. Go to: `http://PC_IP:5000`
5. Allow firewall port 5000

---

## 🚀 PRODUCTION ON WINDOWS

### Option 1: Use Waitress (WSGI Server)
```batch
pip install waitress
python -c "from waitress import serve; from admin_panel import app; serve(app, host='0.0.0.0', port=5000)"
```

### Option 2: IIS (Internet Information Services)
1. Install IIS
2. Install Python for IIS
3. Configure web.config
4. Deploy

---

## 📊 MONITORING

### Task Manager
- Check CPU/Memory usage
- Python process

### Resource Monitor
- Network activity
- Disk I/O

### Performance Monitor
- Detailed metrics

---

## 🆘 NEED HELP?

### Test everything:
```batch
TEST_WINDOWS.bat
```

### Check logs:
```batch
type admin_panel.log
```

### Reinstall:
```batch
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

---

## ✅ QUICK START SUMMARY

```batch
1. INSTALL_WINDOWS.bat     (Run once)
2. START_WINDOWS.bat       (Run anytime)
3. Open: http://localhost:5000
4. Login: admin@vpnvietnam.com / Vpnvietnam123@!
```

**That's it!** 🎉

---

## 📚 FILES FOR WINDOWS

```
✅ START_WINDOWS.bat       - Start server
✅ INSTALL_WINDOWS.bat     - Install dependencies
✅ TEST_WINDOWS.bat        - Run tests
✅ RUN_ON_WINDOWS.md       - This guide
✅ WINDOWS_TIPS.md         - Tips & tricks
```

---

## 🎊 ENJOY YOUR ADMIN PANEL ON WINDOWS!

Questions? Check the other .md files or run TEST_WINDOWS.bat

**Happy managing!** 🚀
