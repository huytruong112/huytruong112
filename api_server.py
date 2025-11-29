"""
API Server để nhận đăng ký từ khách hàng và tự động tạo cấu hình
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import json
import logging
from datetime import datetime

from vpn_service import VPNService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Khởi tạo FastAPI app
app = FastAPI(
    title="VPN Auto-Provisioning API",
    description="API để tự động tạo cấu hình VPN khi khách hàng đăng ký",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load config
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    logger.error("Không tìm thấy config.json, vui lòng tạo từ config.example.json")
    config = {}

# Khởi tạo VPN service
vpn_service = VPNService(config) if config else None

# API Key authentication
API_KEY = config.get('api', {}).get('api_key', 'default_api_key')


def verify_api_key(x_api_key: str = Header(...)):
    """Xác thực API key"""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key


# Pydantic models
class CustomerRegistration(BaseModel):
    """Model cho đăng ký khách hàng mới"""
    email: EmailStr
    name: str
    plan: str = "basic"  # basic, premium, enterprise
    phone: Optional[str] = None
    custom_config: Optional[Dict[str, Any]] = None


class CustomerUsageQuery(BaseModel):
    """Model để truy vấn usage"""
    email: EmailStr
    panel_name: Optional[str] = None


class CustomerRenewal(BaseModel):
    """Model để gia hạn"""
    email: EmailStr
    panel_name: str
    days: int = 30


class CustomerDeletion(BaseModel):
    """Model để xóa khách hàng"""
    email: EmailStr
    panel_name: str
    inbound_id: Optional[int] = None


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "VPN Auto-Provisioning API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Kiểm tra trạng thái service"""
    if not vpn_service:
        raise HTTPException(status_code=500, detail="VPN Service chưa được khởi tạo")
    
    return {
        "status": "healthy",
        "xui_panels": len(vpn_service.xui_clients),
        "threexui_panels": len(vpn_service.threexui_clients),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v1/customer/register", dependencies=[Depends(verify_api_key)])
async def register_customer(customer: CustomerRegistration):
    """
    Đăng ký khách hàng mới và tự động tạo cấu hình VPN
    
    Requires:
    - Header: X-API-Key
    
    Body:
    - email: Email khách hàng
    - name: Tên khách hàng
    - plan: Gói dịch vụ (basic, premium, enterprise)
    - phone: Số điện thoại (optional)
    - custom_config: Cấu hình tùy chỉnh (optional)
    
    Returns:
    - Thông tin cấu hình đã tạo
    """
    if not vpn_service:
        raise HTTPException(status_code=500, detail="VPN Service chưa được khởi tạo")
    
    try:
        customer_data = {
            'email': customer.email,
            'name': customer.name,
            'plan': customer.plan,
            'phone': customer.phone,
            'custom_config': customer.custom_config
        }
        
        result = vpn_service.create_customer_config(customer_data)
        
        if result:
            logger.info(f"Đã tạo cấu hình thành công cho khách hàng: {customer.email}")
            return {
                "success": True,
                "message": "Đã tạo cấu hình VPN thành công",
                "data": result
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Không thể tạo cấu hình VPN, vui lòng thử lại"
            )
            
    except Exception as e:
        logger.error(f"Lỗi khi đăng ký khách hàng: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/customer/usage", dependencies=[Depends(verify_api_key)])
async def get_customer_usage(query: CustomerUsageQuery):
    """
    Lấy thông tin sử dụng của khách hàng
    
    Requires:
    - Header: X-API-Key
    
    Body:
    - email: Email khách hàng
    - panel_name: Tên panel (optional)
    
    Returns:
    - Thông tin sử dụng data và thời gian hết hạn
    """
    if not vpn_service:
        raise HTTPException(status_code=500, detail="VPN Service chưa được khởi tạo")
    
    try:
        usage = vpn_service.get_customer_usage(query.email, query.panel_name)
        
        if usage:
            return {
                "success": True,
                "data": usage
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy thông tin cho email: {query.email}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi lấy usage: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/customer/renew", dependencies=[Depends(verify_api_key)])
async def renew_customer(renewal: CustomerRenewal):
    """
    Gia hạn dịch vụ cho khách hàng
    
    Requires:
    - Header: X-API-Key
    
    Body:
    - email: Email khách hàng
    - panel_name: Tên panel
    - days: Số ngày gia hạn (mặc định 30)
    
    Returns:
    - Xác nhận gia hạn thành công
    """
    if not vpn_service:
        raise HTTPException(status_code=500, detail="VPN Service chưa được khởi tạo")
    
    try:
        success = vpn_service.renew_customer(renewal.email, renewal.panel_name, renewal.days)
        
        if success:
            return {
                "success": True,
                "message": f"Đã gia hạn {renewal.days} ngày cho {renewal.email}"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Không thể gia hạn, vui lòng thử lại"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi gia hạn: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/customer/delete", dependencies=[Depends(verify_api_key)])
async def delete_customer(deletion: CustomerDeletion):
    """
    Xóa cấu hình của khách hàng
    
    Requires:
    - Header: X-API-Key
    
    Body:
    - email: Email khách hàng
    - panel_name: Tên panel
    - inbound_id: ID của inbound (optional, cần cho 3x-ui)
    
    Returns:
    - Xác nhận xóa thành công
    """
    if not vpn_service:
        raise HTTPException(status_code=500, detail="VPN Service chưa được khởi tạo")
    
    try:
        success = vpn_service.delete_customer(
            deletion.email,
            deletion.panel_name,
            deletion.inbound_id
        )
        
        if success:
            return {
                "success": True,
                "message": f"Đã xóa cấu hình cho {deletion.email}"
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy khách hàng để xóa"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi xóa khách hàng: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/plans", dependencies=[Depends(verify_api_key)])
async def get_plans():
    """
    Lấy danh sách các gói dịch vụ có sẵn
    
    Requires:
    - Header: X-API-Key
    
    Returns:
    - Danh sách plans với thông tin chi tiết
    """
    if not config:
        raise HTTPException(status_code=500, detail="Config chưa được load")
    
    return {
        "success": True,
        "plans": config.get('plans', {})
    }


if __name__ == "__main__":
    import uvicorn
    
    host = config.get('api', {}).get('host', '0.0.0.0')
    port = config.get('api', {}).get('port', 8000)
    
    logger.info(f"Starting API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
