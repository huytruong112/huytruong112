"""
Subscription Model
"""
from datetime import datetime
from app import db


class Subscription(db.Model):
    """Subscription model for storing VPN service subscriptions"""
    
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    # X-UI/3X-UI Configuration
    uuid = db.Column(db.String(255), unique=True, nullable=False, index=True)
    inbound_id = db.Column(db.Integer, nullable=False, default=1)
    
    # Service Details
    service_name = db.Column(db.String(100))  # e.g., "Basic Plan", "Premium Plan"
    traffic_limit_gb = db.Column(db.Integer, default=0)  # 0 = unlimited
    traffic_used_gb = db.Column(db.Float, default=0.0)
    
    # Dates
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_expired = db.Column(db.Boolean, default=False)
    
    # Metadata
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Subscription {self.uuid} for customer {self.customer_id}>'
    
    def to_dict(self):
        """Convert subscription to dictionary"""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'uuid': self.uuid,
            'inbound_id': self.inbound_id,
            'service_name': self.service_name,
            'traffic_limit_gb': self.traffic_limit_gb,
            'traffic_used_gb': self.traffic_used_gb,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'is_active': self.is_active,
            'is_expired': self.is_expired,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def check_expiry(self):
        """Check if subscription has expired"""
        if self.expiry_date and datetime.utcnow() > self.expiry_date:
            self.is_expired = True
            self.is_active = False
            return True
        return False
    
    def remaining_traffic_gb(self):
        """Calculate remaining traffic in GB"""
        if self.traffic_limit_gb == 0:
            return float('inf')  # Unlimited
        return max(0, self.traffic_limit_gb - self.traffic_used_gb)
    
    def remaining_days(self):
        """Calculate remaining days until expiry"""
        if not self.expiry_date:
            return None
        delta = self.expiry_date - datetime.utcnow()
        return max(0, delta.days)
