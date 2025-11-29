const axios = require('axios');

class X3UIService {
  constructor() {
    this.baseURL = process.env.X3UI_PANEL_URL;
    this.username = process.env.X3UI_USERNAME;
    this.password = process.env.X3UI_PASSWORD;
    this.cookie = null;
    this.inboundId = parseInt(process.env.DEFAULT_INBOUND_ID || '1');
  }

  /**
   * Đăng nhập vào 3X-UI panel và lấy cookie
   */
  async login() {
    try {
      const response = await axios.post(
        `${this.baseURL}/login`,
        {
          username: this.username,
          password: this.password
        },
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      );

      // Lấy cookie từ response
      const cookies = response.headers['set-cookie'];
      if (cookies && cookies.length > 0) {
        this.cookie = cookies[0].split(';')[0];
        console.log('✅ Đăng nhập 3X-UI thành công');
        return true;
      }

      throw new Error('Không thể lấy cookie từ 3X-UI');
    } catch (error) {
      console.error('❌ Lỗi đăng nhập 3X-UI:', error.message);
      throw error;
    }
  }

  /**
   * Đảm bảo đã đăng nhập trước khi thực hiện request
   */
  async ensureLoggedIn() {
    if (!this.cookie) {
      await this.login();
    }
  }

  /**
   * Tạo client mới trong 3X-UI
   * @param {Object} clientData - Thông tin client
   * @param {string} clientData.email - Email của client
   * @param {string} clientData.clientId - ID của client (UUID)
   * @param {number} clientData.expiryTime - Thời gian hết hạn (timestamp milliseconds)
   * @param {number} clientData.totalGB - Tổng dung lượng (GB), 0 = không giới hạn
   * @param {number} clientData.limitIp - Số kết nối tối đa
   */
  async createClient(clientData) {
    await this.ensureLoggedIn();

    try {
      // Lấy thông tin inbound hiện tại
      const inbound = await this.getInbound(this.inboundId);
      
      // Parse settings hiện tại
      let settings = JSON.parse(inbound.settings);
      if (!settings.clients) {
        settings.clients = [];
      }

      // Tạo client mới
      const newClient = {
        id: clientData.clientId,
        email: clientData.email,
        enable: true,
        expiryTime: clientData.expiryTime,
        totalGB: clientData.totalGB * 1024 * 1024 * 1024, // Convert GB to bytes
        limitIp: clientData.limitIp || 0,
        subId: this.generateSubId(),
        tgId: '',
        reset: 0
      };

      // Thêm client vào danh sách
      settings.clients.push(newClient);

      // Cập nhật inbound
      const updateData = {
        up: inbound.up,
        down: inbound.down,
        total: inbound.total,
        remark: inbound.remark,
        enable: inbound.enable,
        expiryTime: inbound.expiryTime,
        listen: inbound.listen,
        port: inbound.port,
        protocol: inbound.protocol,
        settings: JSON.stringify(settings),
        streamSettings: inbound.streamSettings,
        sniffing: inbound.sniffing
      };

      const response = await axios.post(
        `${this.baseURL}/panel/api/inbounds/update/${this.inboundId}`,
        updateData,
        {
          headers: {
            'Cookie': this.cookie,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.success) {
        console.log(`✅ Đã tạo client: ${clientData.email}`);
        
        // Lấy URL kết nối
        const connectionUrl = await this.getClientUrl(clientData.clientId);
        
        return {
          success: true,
          clientId: clientData.clientId,
          email: clientData.email,
          connectionUrl: connectionUrl,
          subscriptionUrl: `${this.baseURL}/sub/${newClient.subId}`
        };
      }

      throw new Error(response.data.msg || 'Không thể tạo client');
    } catch (error) {
      console.error('❌ Lỗi tạo client:', error.message);
      throw error;
    }
  }

  /**
   * Lấy thông tin inbound
   */
  async getInbound(inboundId) {
    await this.ensureLoggedIn();

    try {
      const response = await axios.get(
        `${this.baseURL}/panel/api/inbounds/get/${inboundId}`,
        {
          headers: {
            'Cookie': this.cookie
          }
        }
      );

      if (response.data.success) {
        return response.data.obj;
      }

      throw new Error('Không thể lấy thông tin inbound');
    } catch (error) {
      console.error('❌ Lỗi lấy inbound:', error.message);
      throw error;
    }
  }

  /**
   * Lấy danh sách tất cả clients
   */
  async listClients() {
    await this.ensureLoggedIn();

    try {
      const response = await axios.post(
        `${this.baseURL}/panel/api/inbounds/list`,
        {},
        {
          headers: {
            'Cookie': this.cookie
          }
        }
      );

      if (response.data.success) {
        const inbounds = response.data.obj;
        const clients = [];

        inbounds.forEach(inbound => {
          if (inbound.settings) {
            const settings = JSON.parse(inbound.settings);
            if (settings.clients) {
              settings.clients.forEach(client => {
                clients.push({
                  ...client,
                  inboundId: inbound.id,
                  protocol: inbound.protocol
                });
              });
            }
          }
        });

        return clients;
      }

      throw new Error('Không thể lấy danh sách clients');
    } catch (error) {
      console.error('❌ Lỗi lấy danh sách clients:', error.message);
      throw error;
    }
  }

  /**
   * Xóa client
   */
  async deleteClient(clientId) {
    await this.ensureLoggedIn();

    try {
      const response = await axios.post(
        `${this.baseURL}/panel/api/inbounds/delClient/${clientId}`,
        {},
        {
          headers: {
            'Cookie': this.cookie
          }
        }
      );

      if (response.data.success) {
        console.log(`✅ Đã xóa client: ${clientId}`);
        return true;
      }

      throw new Error('Không thể xóa client');
    } catch (error) {
      console.error('❌ Lỗi xóa client:', error.message);
      throw error;
    }
  }

  /**
   * Cập nhật thông tin client
   */
  async updateClient(clientId, updateData) {
    await this.ensureLoggedIn();

    try {
      const response = await axios.post(
        `${this.baseURL}/panel/api/inbounds/updateClient/${clientId}`,
        updateData,
        {
          headers: {
            'Cookie': this.cookie,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.success) {
        console.log(`✅ Đã cập nhật client: ${clientId}`);
        return true;
      }

      throw new Error('Không thể cập nhật client');
    } catch (error) {
      console.error('❌ Lỗi cập nhật client:', error.message);
      throw error;
    }
  }

  /**
   * Lấy URL kết nối của client
   */
  async getClientUrl(clientId) {
    // Giả sử URL có dạng vmess://... hoặc vless://...
    // Bạn cần điều chỉnh theo protocol thực tế của bạn
    const inbound = await this.getInbound(this.inboundId);
    
    // Tạo URL dựa trên protocol
    // Đây là ví dụ đơn giản, bạn cần điều chỉnh theo cấu hình thực tế
    return `${inbound.protocol}://${clientId}@${this.baseURL.replace('http://', '').replace('https://', '')}`;
  }

  /**
   * Generate subscription ID
   */
  generateSubId() {
    return Math.random().toString(36).substring(2, 15) + 
           Math.random().toString(36).substring(2, 15);
  }

  /**
   * Reset traffic của client
   */
  async resetClientTraffic(clientId) {
    await this.ensureLoggedIn();

    try {
      const response = await axios.post(
        `${this.baseURL}/panel/api/inbounds/resetClientTraffic/${clientId}`,
        {},
        {
          headers: {
            'Cookie': this.cookie
          }
        }
      );

      if (response.data.success) {
        console.log(`✅ Đã reset traffic cho client: ${clientId}`);
        return true;
      }

      throw new Error('Không thể reset traffic');
    } catch (error) {
      console.error('❌ Lỗi reset traffic:', error.message);
      throw error;
    }
  }
}

module.exports = new X3UIService();
