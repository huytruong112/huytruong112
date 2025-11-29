# 🔧 TROUBLESHOOTING GUIDE

## ❓ Bạn gặp lỗi gì?

Để tôi giúp bạn, hãy cho biết **CHỦ THỂ** lỗi gì:

### Option 1: Lỗi khi chạy app?

**Nếu chạy `./run_app.sh` hoặc `streamlit run ...` bị lỗi:**

```bash
# Copy TOÀN BỘ error message và paste vào chat:
./run_app.sh 2>&1 | tee error.log
cat error.log
```

**Paste toàn bộ error vào đây!**

### Option 2: App chạy nhưng có lỗi trong UI?

**Nếu app mở được nhưng có lỗi đỏ trong trang:**

1. Screenshot error message màu đỏ
2. Paste vào chat

### Option 3: Operations không hoạt động?

**Nếu click buttons (🔄⏱️⏸️✏️) không work:**

1. Mở **🔍 Debug Info** expander
2. Mở **🔍 Debug Response** expander
3. Screenshot CẢ 2 expanders
4. Paste vào chat

### Option 4: Không chạy được app?

**Test từng bước:**

```bash
# Bước 1: Check Python
python3 --version
# → Cần Python 3.8+

# Bước 2: Check dependencies
python3 -c "import streamlit; print('Streamlit OK')"
# → Nếu lỗi: pip3 install streamlit

# Bước 3: Check file
ls -lh vpn_admin_pro_multiserver.py
# → File có tồn tại không?

# Bước 4: Check syntax
python3 -m py_compile vpn_admin_pro_multiserver.py
# → Có syntax error không?

# Bước 5: Try run
export PATH="$HOME/.local/bin:$PATH"
python3 -m streamlit run vpn_admin_pro_multiserver.py
# → Lỗi gì?
```

**Paste output của từng bước!**

---

## 🔍 Quick Diagnostics

### Test 1: Dependencies

```bash
python3 << 'PYEOF'
import sys
try:
    import streamlit
    print(f"✓ streamlit {streamlit.__version__}")
except Exception as e:
    print(f"✗ streamlit: {e}")

try:
    import requests
    print(f"✓ requests {requests.__version__}")
except Exception as e:
    print(f"✗ requests: {e}")

try:
    import pandas
    print(f"✓ pandas {pandas.__version__}")
except Exception as e:
    print(f"✗ pandas: {e}")

try:
    import qrcode
    print("✓ qrcode OK")
except Exception as e:
    print(f"✗ qrcode: {e}")

try:
    from PIL import Image
    print("✓ PIL OK")
except Exception as e:
    print(f"✗ PIL: {e}")

try:
    import psutil
    print("✓ psutil OK")
except Exception as e:
    print(f"✗ psutil: {e}")
PYEOF
```

**Paste output!**

### Test 2: App Load

```bash
cd /workspace
python3 -c "
with open('vpn_admin_pro_multiserver.py', 'r') as f:
    code = f.read()
compile(code, 'vpn_admin_pro_multiserver.py', 'exec')
print('✓ App syntax OK')
"
```

**Paste output!**

### Test 3: Run Test

```bash
cd /workspace
timeout 5 python3 -m streamlit run vpn_admin_pro_multiserver.py --server.headless true 2>&1 | head -30
```

**Paste output!**

---

## 📋 Common Errors & Solutions

### Error 1: "streamlit: command not found"

**Solution:**

```bash
export PATH="$HOME/.local/bin:$PATH"
# Or
python3 -m streamlit run vpn_admin_pro_multiserver.py
```

### Error 2: "No module named 'streamlit'"

**Solution:**

```bash
pip3 install streamlit requests pandas qrcode pillow psutil
```

### Error 3: "Address already in use"

**Solution:**

```bash
# Kill existing streamlit
pkill -f streamlit
# Or use different port
streamlit run vpn_admin_pro_multiserver.py --server.port 8502
```

### Error 4: "Permission denied"

**Solution:**

```bash
chmod +x run_app.sh
./run_app.sh
```

### Error 5: Syntax Error in code

**Check:**

```bash
python3 -m py_compile vpn_admin_pro_multiserver.py
```

If error, paste the line number and I'll fix it!

---

## ❓ Still Not Working?

**I NEED THIS INFO:**

1. **What command did you run?**
   ```
   Example: ./run_app.sh
   ```

2. **What error message appeared?**
   ```
   Copy EXACT error text here
   ```

3. **What happened?**
   - App won't start?
   - App starts but error in UI?
   - Operations don't work?
   - Other?

4. **Screenshots (if UI error):**
   - Error message
   - Debug expanders (if operations fail)

---

## 🚀 Quick Start (If Nothing Works)

**Fresh install:**

```bash
# 1. Go to workspace
cd /workspace

# 2. Install dependencies
pip3 install --user streamlit requests pandas qrcode pillow psutil

# 3. Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# 4. Run
streamlit run vpn_admin_pro_multiserver.py

# If still fails, copy ENTIRE output and paste to chat!
```

---

**PLEASE PROVIDE:**

1. ✅ Exact command you ran
2. ✅ Exact error message
3. ✅ Output of diagnostic tests above
4. ✅ Screenshots (if UI error)

**With these, I can fix the EXACT issue!**

---

**Version:** v2.3.3  
**Status:** Troubleshooting  
**Date:** 29/11/2024
