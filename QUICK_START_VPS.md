# ⚡ QUICK START - CHẠY TRÊN VPS UBUNTU

## 🎯 3 Cách Chạy

### ✨ CÁCH 1: TỰ ĐỘNG (KHUYẾN NGHỊ)

```bash
# 1. Kết nối VPS
ssh root@YOUR_VPS_IP

# 2. Tải script
cd /root
wget YOUR_REPO/install_ubuntu.sh
chmod +x install_ubuntu.sh

# 3. Chạy
./install_ubuntu.sh

# 4. Truy cập
# http://YOUR_VPS_IP:8501
```

**→ XONG!** Script tự động cài tất cả!

---

### 🔧 CÁCH 2: THỦ CÔNG (5 PHÚT)

```bash
# 1. Kết nối VPS
ssh root@YOUR_VPS_IP

# 2. Cài Python & packages
apt update
apt install python3 python3-pip -y
pip3 install streamlit requests pandas qrcode pillow

# 3. Upload file
# Từ máy local:
scp vless_config_manager.py root@YOUR_VPS_IP:/root/
scp run_config_manager.sh root@YOUR_VPS_IP:/root/

# 4. Chạy (trên VPS)
cd /root
chmod +x run_config_manager.sh
./run_config_manager.sh

# 5. Truy cập
# http://YOUR_VPS_IP:8501
```

---

### 🐳 CÁCH 3: SCREEN (CHẠY NỀN)

```bash
# 1-2. Giống cách 2

# 3. Cài screen
apt install screen -y

# 4. Tạo session & chạy
screen -S vless
cd /root
./run_config_manager.sh

# 5. Detach: Ctrl+A, D

# 6. Reattach khi cần
screen -r vless

# 7. Truy cập
# http://YOUR_VPS_IP:8501
```

---

## 🔥 ONE-LINER (SIÊU NHANH!)

```bash
ssh root@YOUR_VPS_IP "apt update && apt install -y python3 python3-pip && pip3 install streamlit requests pandas qrcode pillow" && scp vless_config_manager.py run_config_manager.sh root@YOUR_VPS_IP:/root/ && ssh root@YOUR_VPS_IP "cd /root && chmod +x run_config_manager.sh && screen -dmS vless ./run_config_manager.sh"
```

**Sau đó truy cập:** `http://YOUR_VPS_IP:8501`

---

## 🌐 MỞ PORT (QUAN TRỌNG!)

```bash
# Ubuntu Firewall
sudo ufw allow 8501/tcp
sudo ufw reload

# Hoặc iptables
sudo iptables -A INPUT -p tcp --dport 8501 -j ACCEPT
```

**Cloud Provider:**
- AWS: Security Groups → Add rule: TCP 8501
- Google Cloud: Firewall Rules → New rule: TCP 8501
- DigitalOcean: Networking → Firewall → Add rule: TCP 8501
- Vultr: Firewall → Add rule: TCP 8501

---

## ✅ CHECKLIST

- [ ] Kết nối VPS: `ssh root@YOUR_VPS_IP`
- [ ] Cài Python: `apt install python3 python3-pip -y`
- [ ] Cài packages: `pip3 install streamlit requests pandas qrcode pillow`
- [ ] Upload file: `vless_config_manager.py`
- [ ] Mở port: `ufw allow 8501/tcp`
- [ ] Chạy app: `./run_config_manager.sh`
- [ ] Truy cập: `http://YOUR_VPS_IP:8501`

---

## 🔍 KIỂM TRA

```bash
# Check Python
python3 --version

# Check packages
pip3 list | grep streamlit

# Check port
netstat -tulpn | grep 8501

# Check process
ps aux | grep streamlit

# Test local
curl http://localhost:8501
```

---

## 🐛 LỖI THƯỜNG GẶP

### Lỗi: Không truy cập được

**Fix:**
1. Check firewall: `ufw status`
2. Check port: `netstat -tulpn | grep 8501`
3. Check app binding: `0.0.0.0` (not `127.0.0.1`)

```bash
streamlit run vless_config_manager.py --server.address 0.0.0.0
```

### Lỗi: Module not found

**Fix:**
```bash
pip3 install streamlit requests pandas qrcode pillow
```

### Lỗi: Permission denied

**Fix:**
```bash
chmod +x run_config_manager.sh
```

---

## 🎯 TRUY CẬP

```
http://YOUR_VPS_IP:8501
```

**VD:**
- `http://45.76.123.45:8501`
- `http://192.168.1.100:8501`

---

## 🚀 DONE!

**Đã chạy xong, giờ có thể:**
1. Tạo VLESS configs
2. Chọn templates
3. Export links & QR codes
4. Backup/restore

**Enjoy!** 🎉
