# 🔧 Troubleshooting: VLESS Deep Link

## 📋 Issue

Nút "Thêm Cấu Hình" không hoạt động / không chuyển sang ứng dụng V2Box

**Page**: `vless_open.php`  
**Version**: 1.0.2  
**Last Updated**: December 1, 2025

---

## 🔍 Quick Diagnosis

### Step 1: Open Browser Console

1. Mở `vless_open.php?id=1`
2. Nhấn **F12** để mở DevTools
3. Chuyển sang tab **Console**
4. Tìm các message có prefix `[VLESS]`

### Expected Console Output:

```
[VLESS] Page initialized successfully
[VLESS] Event listener attached to button
✓ VLESS URI đã được copy vào clipboard
```

### When You Click Button:

```
[VLESS] Button clicked, calling openV2Box()
[VLESS] openV2Box() called
[VLESS] VLESS URI: vless://...
[VLESS] Device: iOS (or Android or Other)
[VLESS] Button disabled, processing...
```

---

## ⚠️ Common Issues & Solutions

### Issue 1: Console Shows Nothing

**Symptom**: Không có message `[VLESS]` nào trong console

**Cause**: JavaScript file không load được

**Solution**:
```bash
# Check if file exists
curl https://your-domain.com/js/vless_open.min.js

# Expected: JavaScript code returned

# If 404 or 403:
# 1. Check file uploaded correctly
# 2. Check file permissions (chmod 644)
# 3. Check .htaccess allows .min.js files
```

---

### Issue 2: "openV2Box function not available"

**Symptom**: Console shows error: `[VLESS] openV2Box function not available!`

**Cause**: Function không được định nghĩa

**Solution**:
```javascript
// Test in console:
typeof window.openV2Box
// Expected: "function"

// If "undefined":
// 1. Clear browser cache (Ctrl+Shift+Delete)
// 2. Hard reload (Ctrl+F5)
// 3. Check js/vless_open.min.js file size > 0
```

---

### Issue 3: "VLESS URI not defined"

**Symptom**: Console shows: `[VLESS] VLESS URI not defined`

**Cause**: PHP không set `window.vlessUri`

**Solution**:
```javascript
// Test in console:
window.vlessUri
// Expected: "vless://uuid@server:port?..."

// If undefined:
// 1. Check vless_open.php has this code in <head>:
//    <script>
//      window.vlessUri = <?= json_encode($vlessUri) ?>;
//    </script>
// 2. Check $vlessUri variable in PHP has value
// 3. Check database has vless_configs data
```

---

### Issue 4: Button Click Does Nothing (Desktop)

**Symptom**: Click button, shows warning "V2Box chỉ khả dụng trên iOS và Android"

**Cause**: Đây là BEHAVIOR ĐÚNG trên desktop!

**Explanation**:
- Deep linking chỉ hoạt động trên **mobile devices** (iOS/Android)
- Trên desktop: Button chỉ hiển thị warning
- User phải test trên điện thoại thật hoặc emulator

**Solution**: Test trên thiết bị mobile thật!

---

### Issue 5: Button Click Does Nothing (Mobile)

**Symptom**: Trên mobile, click button nhưng không có gì xảy ra

**Console Check**:
```
[VLESS] Button clicked, calling openV2Box()
[VLESS] openV2Box() called
[VLESS] VLESS URI: vless://...
[VLESS] Device: iOS
[VLESS] Redirecting to: vless://...
```

**Causes & Solutions**:

#### A) V2Box App Not Installed
- **Expected**: Sau 2.5s sẽ redirect đến App Store/Play Store
- **Solution**: Cài đặt V2Box app trước

#### B) Deep Link Blocked by Browser
- **Symptom**: `window.location.href` không hoạt động
- **Solution**: 
  ```javascript
  // Some browsers block redirects from button click
  // Try different browser:
  // - iOS: Safari (best support)
  // - Android: Chrome (best support)
  ```

#### C) VLESS URI Invalid Format
- **Check URI format**:
  ```
  vless://UUID@SERVER:PORT?encryption=none&security=reality&type=tcp#NAME
  ```
- **Test manually**: Copy URI và paste vào V2Box app

---

### Issue 6: Redirects to Wrong Page

**Symptom**: Click button → redirects to wrong URL

**Debug**:
```javascript
// Check in console:
window.vlessUri
// Should be: vless://...

// Check deep link:
// iOS: Should be same as vlessUri
// Android: Should be intent://...#Intent;scheme=vless;package=...;end
```

**Solution**: Check PHP code generates correct URI

---

## 🧪 Testing Procedure

### Test 1: Basic Functionality (Desktop)

```
1. Open vless_open.php?id=1
2. Open console (F12)
3. Expected console logs:
   ✓ [VLESS] Page initialized successfully
   ✓ [VLESS] Event listener attached to button
4. Click "Thêm Cấu Hình"
5. Expected:
   ✓ Console: [VLESS] Button clicked
   ✓ Console: [VLESS] Device: Other
   ✓ Warning message appears
6. Result: ✅ PASS
```

### Test 2: Mobile iOS

```
1. Open vless_open.php?id=1 on iPhone (Safari)
2. Click "Thêm Cấu Hình"
3. If V2Box installed:
   Expected: App opens and imports config
   Result: ✅ PASS
4. If V2Box NOT installed:
   Expected: After 2.5s, redirect to App Store
   Result: ✅ PASS
```

### Test 3: Mobile Android

```
1. Open vless_open.php?id=1 on Android (Chrome)
2. Click "Thêm Cấu Hình"
3. If V2Box installed:
   Expected: App opens and imports config
   Result: ✅ PASS
4. If V2Box NOT installed:
   Expected: After 2.5s, redirect to Play Store
   Result: ✅ PASS
```

---

## 📱 Mobile Testing Tips

### iOS Safari:

1. **Enable Web Inspector**:
   - Settings → Safari → Advanced → Web Inspector
   - Connect iPhone to Mac
   - Safari (Mac) → Develop → [iPhone] → Select page
   - Now can see console logs!

2. **Test Deep Link**:
   - Copy VLESS URI
   - Paste directly in Safari address bar
   - Should open V2Box app

### Android Chrome:

1. **Remote Debugging**:
   - Enable Developer Options on Android
   - Enable USB Debugging
   - Connect to computer
   - Chrome (PC) → More tools → Remote devices
   - Select device and inspect page
   - Now can see console logs!

2. **Test Intent**:
   ```
   adb shell am start -a android.intent.action.VIEW \
     -d "intent://uuid@server:port?encryption=none#Intent;scheme=vless;package=dev.hexasoftware.v2box;end"
   ```

---

## 🔧 Advanced Debugging

### Check Event Listener:

```javascript
// In console, run:
const btn = document.getElementById('openAppBtn');
getEventListeners(btn);

// Expected: { click: [Function] }
```

### Manual Test openV2Box:

```javascript
// In console, run:
window.openV2Box();

// Watch console for logs and behavior
```

### Check Page Ready Flag:

```javascript
// In console, run:
window.vlessPageReady

// Expected: true
```

### Check V2Box App Detection:

```javascript
// In console, run:
let appOpened = false;
window.addEventListener('blur', () => {
  console.log('Window blur detected!');
  appOpened = true;
});

document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    console.log('Document hidden! App might have opened.');
  }
});

// Then try to open any app (e.g., Maps, Settings)
// Console should log blur/visibilitychange
```

---

## 📊 Comparison: Old vs New Code

### Old Code (Inline):

```html
<button onclick="openV2Box()">Thêm Cấu Hình</button>
<script>
  function openV2Box() {
    // Logic here
  }
</script>
```

**Problem**: Không bảo mật, code dễ đọc

---

### New Code (External):

```html
<button id="openAppBtn">Thêm Cấu Hình</button>
<script src="/js/vless_open.min.js"></script>
```

**Benefits**:
- ✅ Code được bảo mật (minified + obfuscated)
- ✅ Source file protected (.htaccess)
- ✅ Better caching
- ✅ Easier maintenance

**Trade-off**: Cần debug console để troubleshoot

---

## 🎯 Expected Behavior Summary

| Device | V2Box Installed | Expected Behavior |
|--------|----------------|-------------------|
| iOS | ✅ Yes | Open V2Box → Import config |
| iOS | ❌ No | Wait 2.5s → Redirect App Store |
| Android | ✅ Yes | Open V2Box → Import config |
| Android | ❌ No | Wait 2.5s → Redirect Play Store |
| Desktop | N/A | Show warning message |

---

## 🔄 If Still Not Working

### Solution A: Revert to Inline (Temporary Debug)

For debugging ONLY, temporarily add inline onclick:

```html
<button id="openAppBtn" onclick="if(typeof openV2Box==='function') openV2Box(); else alert('Function not loaded!');">
    Thêm Cấu Hình
</button>
```

This helps identify if issue is:
- Function not loading ← Fix JS file
- Function not working ← Fix logic

---

### Solution B: Use Test Page

Open `test_vless_deep_link.html`:
- Full debug logging
- Device detection display
- Step-by-step execution log
- Prevents actual redirects (for testing)

---

### Solution C: Check Server Logs

```bash
# Check Apache/Nginx error log
tail -f /var/log/apache2/error.log
tail -f /var/log/nginx/error.log

# Check PHP error log
tail -f /var/log/php/error.log

# Look for:
# - 404 errors (file not found)
# - 403 errors (permission denied)
# - PHP errors (syntax, database)
```

---

## 📝 Checklist

Before reporting "not working":

- [ ] Tested on actual mobile device (not just desktop)
- [ ] Opened browser console and checked for `[VLESS]` logs
- [ ] Verified `window.vlessUri` is defined
- [ ] Verified `window.openV2Box` is a function
- [ ] Verified button has event listener attached
- [ ] Cleared browser cache
- [ ] Tested on correct browser (Safari iOS, Chrome Android)
- [ ] V2Box app is actually installed (for app open test)
- [ ] VLESS URI format is correct

---

## 💡 Pro Tips

1. **Always test on mobile device** - Desktop behavior is different!
2. **Use browser DevTools** - Console is your friend
3. **Test with V2Box installed first** - Verify app opens
4. **Then test without V2Box** - Verify store redirect
5. **Check console logs** - `[VLESS]` prefix shows execution flow
6. **Manual URI test** - Copy URI, paste in V2Box directly

---

## 📞 Support

If still not working after following this guide:

1. **Capture console logs** (screenshot or copy text)
2. **Note device info** (iOS 16? Android 13? Desktop Chrome?)
3. **Describe exact behavior** (nothing happens? wrong redirect? error message?)
4. **Share VLESS URI format** (without sensitive data)

---

**Version**: 1.0.2  
**Last Updated**: December 1, 2025  
**Status**: Active Support  

---

*Deep linking works when properly configured. Most "not working" issues are due to testing on desktop or console logs not checked.*
