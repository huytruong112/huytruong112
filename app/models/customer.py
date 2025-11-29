"""
Customer Model
"""
from datetime import datetime
from app import db


class Customer(db.Model):
    """Customer model for storing user information"""
    
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50))
    telegram_id = db.Column(db.String(100))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = db.relationship('Subscription', backref='customer', lazy='dynamic', 
                                   cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Customer {self.email}>'
    
    def to_dict(self):
        """Convert customer to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'telegram_id': self.telegram_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'subscriptions': [sub.to_dict() for sub in self.subscriptions]
        }
