# VLESS Manager All-in-One

A complete single-file Flask web application for managing VLESS panels (3x-ui compatible).

## Features

### 🎯 Core Features
- **Dashboard Overview**: Real-time statistics for inbounds, clients, traffic, and server resources
- **Inbound Management**: Create and manage VLESS inbounds (TCP/WS/GRPC)
- **Client Management**: Full CRUD operations for clients/users
- **Traffic Monitoring**: Track upload/download usage per client
- **Expiry Management**: Advanced renewal system with multiple options
- **Share Links**: Generate QR codes and VLESS links for easy client setup

### 🎨 UI Features
- Dark/Light mode toggle
- Responsive Bootstrap 5 design
- Toast notifications for user actions
- Modal-based workflows (no page reloads)
- Progress bars for traffic usage
- Dropdown action menus

### 🔧 Technical Features
- **Single File Architecture**: Everything in one `app.py` file
- **Mock Mode**: Test without real server (MOCK_MODE = True)
- **Real API Mode**: Connect to actual 3x-ui panels (MOCK_MODE = False)
- **In-memory Storage**: Mock data stored in RAM during testing
- **CDN-based Assets**: Bootstrap 5, FontAwesome, QRCode.js

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the application:**
```bash
python app.py
```

3. **Access the web interface:**
Open your browser and navigate to: `http://127.0.0.1:5000`

## Usage

### Mock Mode (Default)
The application runs with `MOCK_MODE = True` by default, which means:
- All data is simulated in memory
- Perfect for testing on Windows without a real server
- All CRUD operations work with fake data
- Includes sample inbounds and clients

### Real API Mode
To connect to an actual 3x-ui panel:
1. Edit `app.py` and set `MOCK_MODE = False`
2. Implement the actual API calls in the route handlers
3. Configure your 3x-ui server credentials

## Main Operations

### Dashboard
- View total inbounds, clients, and traffic statistics
- Monitor CPU and RAM usage
- See active vs. total clients

### Inbound Management
- **Add Inbound**: Create new VLESS inbounds with:
  - TCP, WebSocket, or GRPC network types
  - TLS, Reality, or no security
  - Path validation for WebSocket
- **Delete Inbound**: Remove unused inbounds

### Client Management

#### Add Client
- Generate or specify UUID
- Set email, traffic limit, IP limit
- Choose inbound and expiry date

#### Edit Client
- Update email, UUID, traffic limit, IP limit
- Enable/disable client

#### Renew/Extend (Special Feature)
Three renewal options:
1. **Quick Extend**: Add 30 or 90 days to current expiry
2. **Custom Date**: Set specific expiry date
3. **Smart Logic**: If expired, extends from current date; if active, extends from expiry date

#### Reset Traffic
- Reset upload/download counters to zero
- Keep all other settings intact

#### Share Configuration
- Generate QR code for mobile apps
- Copy VLESS link for desktop clients
- Automatic link generation based on inbound settings

#### Delete Client
- Remove client permanently from inbound

## Project Structure

```
/workspace/
├── app.py              # Single-file Flask application (complete)
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap 5
- **Icons**: FontAwesome 6
- **QR Codes**: QRCode.js
- **Architecture**: Single-file application with embedded templates

## Configuration

### Key Variables in `app.py`

```python
MOCK_MODE = True  # Toggle between mock and real API mode
```

### Mock Data
The application includes:
- 2 sample inbounds (WebSocket and GRPC)
- 3 sample clients with various states
- Simulated traffic usage and expiry dates
- Random CPU/RAM statistics

## API Endpoints

All endpoints return JSON responses:

- `GET /` - Main web interface
- `GET /api/dashboard` - Dashboard statistics
- `GET /api/inbounds` - List all inbounds
- `POST /api/inbounds` - Create new inbound
- `DELETE /api/inbounds/<id>` - Delete inbound
- `GET /api/clients` - List all clients
- `POST /api/clients` - Create new client
- `PUT /api/clients/<id>` - Update client
- `POST /api/clients/<id>/renew` - Renew client expiry
- `POST /api/clients/<id>/reset-traffic` - Reset traffic
- `DELETE /api/clients/<id>` - Delete client
- `GET /api/clients/<id>/share` - Get share link and QR

## Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari
- Opera

## Security Notes

- Change the `app.secret_key` in production
- Implement authentication before deploying
- Use HTTPS in production environments
- Validate all user inputs
- Implement rate limiting for API endpoints

## Future Enhancements

- User authentication and authorization
- Multi-panel support
- Real-time traffic monitoring with WebSockets
- Export/import client configurations
- Automated backup system
- Email notifications for expiring clients
- Telegram bot integration

## Troubleshooting

**Issue**: Port 5000 already in use
**Solution**: Change the port in the last line of `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

**Issue**: QR code not displaying
**Solution**: Check browser console for JavaScript errors, ensure CDN is accessible

**Issue**: Changes not saved
**Solution**: In MOCK_MODE, data is stored in RAM and resets on restart

## License

This project is provided as-is for educational and testing purposes.

## Support

For issues and questions, please check the code comments in `app.py` for detailed explanations of each function.

---

**Note**: This is a client UI for managing 3x-ui panels. It requires a 3x-ui server for real operation. The mock mode is perfect for testing and development without needing a real server.
