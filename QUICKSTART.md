# Quick Start Guide - VLESS Manager All-in-One

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install Flask
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python app.py
```

Or if using Python 3:
```bash
python3 app.py
```

### Step 3: Open Your Browser
Navigate to: **http://127.0.0.1:5000**

That's it! 🎉

---

## 🎯 First Time Usage

### Explore the Mock Data
The application runs in **Mock Mode** by default, which means:
- ✅ No real server needed
- ✅ Works on Windows, Mac, Linux
- ✅ Perfect for testing and learning
- ✅ All features are fully functional

### Pre-loaded Data
When you first open the app, you'll see:
- **2 Inbounds** (WebSocket and GRPC servers)
- **3 Sample Clients** with different states
- **Dashboard Statistics** with simulated data

---

## 📱 Main Interface

### 🏠 Dashboard
View at a glance:
- Total inbounds and clients
- Traffic usage statistics
- CPU and RAM usage (simulated)
- Active vs disabled clients

### 🖥️ Inbounds Management
**To Add an Inbound:**
1. Click "Add Inbound" button
2. Fill in the form:
   - **Remark**: Friendly name (e.g., "Main Server")
   - **Port**: Port number (e.g., 443)
   - **Network**: TCP, WebSocket, or GRPC
   - **Path**: For WebSocket (must start with `/`)
   - **Service Name**: For GRPC
   - **Security**: TLS, Reality, or None
3. Click "Create"

**To Delete an Inbound:**
- Click the trash icon in the actions column

### 👥 Clients Management
**To Add a Client:**
1. Click "Add Client" button
2. Fill in the form:
   - **Email**: User identifier (e.g., user@example.com)
   - **UUID**: Auto-generated or custom
   - **Inbound**: Select from dropdown
   - **Total GB**: Traffic limit
   - **Limit IP**: Max simultaneous connections
   - **Expiry Date**: When access expires
3. Click "Create"

**To Manage a Client:**
Click the dropdown menu (⋮) for each client to:
- ✏️ **Edit Info**: Update email, UUID, traffic, IP limit
- 📅 **Renew/Extend**: Extend subscription
- 🔄 **Reset Traffic**: Clear usage counters
- 📱 **Share**: Generate QR code and link
- 🗑️ **Delete**: Remove client

---

## ⭐ Special Features

### 📅 Renew/Extend Client
**Three ways to extend a client:**

1. **Quick Extend 30 Days**
   - Click "Extend 30 Days"
   - Adds 30 days to current expiry
   - If expired, adds from today

2. **Quick Extend 90 Days**
   - Click "Extend 90 Days"
   - Adds 90 days to current expiry
   - If expired, adds from today

3. **Custom Date**
   - Select specific expiry date
   - Click "Set Specific Date"
   - Overrides current expiry

**Smart Logic:**
- ✅ If client is active → Extends from current expiry date
- ✅ If client is expired → Extends from today's date

### 📱 Share Configuration
**To share with a client:**
1. Click "Share" in dropdown menu
2. A popup will show:
   - **QR Code**: Scan with mobile app
   - **Link**: Copy for desktop clients
3. Click "Copy" to copy the VLESS link

**VLESS Link Format:**
```
vless://UUID@server:port?type=ws&path=/path&security=tls&encryption=none#email
```

### 🌓 Dark/Light Mode
- Click the moon/sun icon in the sidebar
- Theme is saved in browser storage
- Persists across sessions

---

## 🎨 User Interface Tips

### Navigation
- **Dashboard**: Overview and statistics
- **Inbounds**: Manage server configurations
- **Clients**: Manage users and subscriptions

### Status Badges
- 🟢 **Active**: Client is enabled
- ⚫ **Disabled**: Client is disabled

### Traffic Display
- Shows upload and download separately
- Progress bar indicates usage vs limit
- Hover for detailed information

### Toast Notifications
- ✅ Success: Green notification
- ❌ Error: Red notification
- ℹ️ Info: Blue notification
- Appears in top-right corner
- Auto-dismisses after 3 seconds

---

## 🔧 Configuration

### Mock Mode (Default)
```python
MOCK_MODE = True  # Uses simulated data
```
**Perfect for:**
- Testing on Windows without server
- Learning the interface
- Development and debugging
- Demonstrations

### Real API Mode
```python
MOCK_MODE = False  # Connects to actual 3x-ui server
```
**Note:** You'll need to implement the actual API calls in the code.

---

## 📊 Understanding the Dashboard

### Statistics Cards
1. **Total Inbounds**
   - Number of server configurations
   - Each can have multiple clients

2. **Total Clients**
   - All users (active + disabled)
   
3. **Total Traffic**
   - Aggregated upload + download
   - Displayed in GB

4. **Active Clients**
   - Only enabled clients
   - Excludes disabled accounts

### System Metrics
- **CPU Usage**: Simulated (20-60%)
- **RAM Usage**: Simulated (30-70%)
- In real mode, would show actual server stats

---

## 🎓 Common Workflows

### Workflow 1: Add New User
1. Go to **Inbounds** tab
2. Ensure you have at least one inbound (or create one)
3. Go to **Clients** tab
4. Click **Add Client**
5. Fill in details, click **Create**
6. Click **Share** to get QR code/link

### Workflow 2: Extend Expiring Client
1. Go to **Clients** tab
2. Find the client
3. Click dropdown (⋮)
4. Select **Renew/Extend**
5. Choose quick extend or custom date
6. Done! Client can continue using service

### Workflow 3: Reset Traffic for New Month
1. Go to **Clients** tab
2. Click dropdown (⋮) for client
3. Select **Reset Traffic**
4. Confirm
5. Upload/Download counters reset to 0

### Workflow 4: Update Traffic Limit
1. Go to **Clients** tab
2. Click dropdown (⋮)
3. Select **Edit Info**
4. Update **Total GB** field
5. Click **Save Changes**

---

## 🐛 Troubleshooting

### Problem: "Address already in use"
**Solution:** Change port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

### Problem: QR code not showing
**Solution:** 
- Check internet connection (CDN required)
- Check browser console for errors
- Try different browser

### Problem: Changes not persisting
**Solution:** 
- In MOCK_MODE, data resets on restart
- This is normal behavior for testing
- For persistence, use real database

### Problem: Can't access from other devices
**Solution:**
- App binds to `0.0.0.0` (all interfaces)
- Check firewall settings
- Access via: `http://YOUR-IP:5000`

---

## 💡 Pro Tips

1. **Use Browser DevTools**
   - F12 to open developer tools
   - Check Network tab for API calls
   - Check Console for JavaScript errors

2. **Keyboard Shortcuts**
   - Ctrl+R: Refresh page
   - Ctrl+Shift+I: Open DevTools
   - Esc: Close modals

3. **Bookmark Pages**
   - Bookmark the URL for quick access
   - Each page is accessible via hash

4. **Test with Mock Data**
   - Always test changes with MOCK_MODE first
   - Prevents issues on production server
   - Safe experimentation environment

5. **Export Configuration**
   - Copy VLESS links before deleting clients
   - Save important configurations externally

---

## 📱 Mobile Usage

The interface is **fully responsive** and works on:
- 📱 Phones (iOS, Android)
- 📟 Tablets
- 💻 Desktop browsers
- 🖥️ Large monitors

**Mobile tips:**
- Use landscape mode for better table view
- Tap and hold for dropdown menus
- Swipe gestures work naturally

---

## 🔒 Security Notes

⚠️ **Important for Production:**

1. **Change Secret Key**
   ```python
   app.secret_key = "your-random-secret-key-here"
   ```

2. **Add Authentication**
   - Implement login system
   - Use session management
   - Add user roles

3. **Use HTTPS**
   - Never use HTTP in production
   - Get SSL/TLS certificate
   - Enable secure cookies

4. **Validate Inputs**
   - Additional server-side validation
   - Sanitize user inputs
   - Prevent injection attacks

5. **Rate Limiting**
   - Limit API calls per IP
   - Prevent brute force attacks
   - Use Flask-Limiter extension

---

## 🎉 You're Ready!

Explore the application and test all features. Everything works in mock mode, so feel free to:
- ✅ Add and delete inbounds
- ✅ Create test clients
- ✅ Try renewing subscriptions
- ✅ Generate share links
- ✅ Toggle dark/light mode
- ✅ Reset traffic counters

**Have fun managing your VLESS panel!** 🚀

---

## 📚 Additional Resources

- **README.md**: Full documentation
- **TESTING_REPORT.md**: Detailed test results
- **app.py**: Source code with comments

For questions or issues, check the code comments in `app.py` for detailed explanations.
