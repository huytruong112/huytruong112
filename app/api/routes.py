"""
API Routes for Customer and Subscription Management
"""
from flask import request, jsonify
from datetime import datetime, timedelta
from app import db
from app.api import bp
from app.models import Customer, Subscription
from app.integrations.panel_manager import PanelManager
import logging

logger = logging.getLogger(__name__)
panel_manager = PanelManager()


@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'API is running'}), 200


@bp.route('/customers', methods=['GET'])
def get_customers():
    """Get all customers"""
    try:
        customers = Customer.query.all()
        return jsonify({
            'success': True,
            'customers': [customer.to_dict() for customer in customers]
        }), 200
    except Exception as e:
        logger.error(f"Error getting customers: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get a specific customer by ID"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        return jsonify({
            'success': True,
            'customer': customer.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error getting customer: {e}")
        return jsonify({'success': False, 'error': str(e)}), 404


@bp.route('/customers', methods=['POST'])
def create_customer():
    """
    Create a new customer
    
    Request body:
    {
        "email": "customer@example.com",
        "name": "Customer Name",
        "phone": "+1234567890",
        "telegram_id": "@username"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Email and name are required'
            }), 400
        
        # Check if customer already exists
        existing = Customer.query.filter_by(email=data['email']).first()
        if existing:
            return jsonify({
                'success': False,
                'error': 'Customer with this email already exists'
            }), 400
        
        # Create new customer
        customer = Customer(
            email=data['email'],
            name=data['name'],
            phone=data.get('phone'),
            telegram_id=data.get('telegram_id')
        )
        
        db.session.add(customer)
        db.session.commit()
        
        logger.info(f"Created new customer: {customer.email}")
        
        return jsonify({
            'success': True,
            'customer': customer.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating customer: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """
    Update customer information
    
    Request body:
    {
        "name": "Updated Name",
        "phone": "+1234567890",
        "telegram_id": "@username",
        "is_active": true
    }
    """
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            customer.name = data['name']
        if 'phone' in data:
            customer.phone = data['phone']
        if 'telegram_id' in data:
            customer.telegram_id = data['telegram_id']
        if 'is_active' in data:
            customer.is_active = data['is_active']
        
        db.session.commit()
        
        logger.info(f"Updated customer: {customer.email}")
        
        return jsonify({
            'success': True,
            'customer': customer.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating customer: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """Delete a customer and all their subscriptions"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        
        # Delete all subscriptions from panel
        for subscription in customer.subscriptions:
            try:
                panel_manager.delete_client_config(
                    subscription.inbound_id,
                    subscription.uuid
                )
            except Exception as e:
                logger.warning(f"Failed to delete subscription {subscription.uuid} from panel: {e}")
        
        db.session.delete(customer)
        db.session.commit()
        
        logger.info(f"Deleted customer: {customer.email}")
        
        return jsonify({
            'success': True,
            'message': 'Customer deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting customer: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/subscriptions', methods=['POST'])
def create_subscription():
    """
    Create a new subscription for a customer
    
    Request body:
    {
        "customer_id": 1,
        "service_name": "Basic Plan",
        "traffic_limit_gb": 100,
        "expiry_days": 30,
        "inbound_id": 1
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('customer_id'):
            return jsonify({
                'success': False,
                'error': 'customer_id is required'
            }), 400
        
        # Get customer
        customer = Customer.query.get_or_404(data['customer_id'])
        
        # Get parameters
        traffic_limit_gb = data.get('traffic_limit_gb', 100)
        expiry_days = data.get('expiry_days', 30)
        inbound_id = data.get('inbound_id', 1)
        service_name = data.get('service_name', 'Standard Plan')
        
        # Create client config in panel
        config = panel_manager.create_client_config(
            email=customer.email,
            inbound_id=inbound_id,
            traffic_gb=traffic_limit_gb,
            expiry_days=expiry_days,
            enable=True
        )
        
        if not config:
            return jsonify({
                'success': False,
                'error': 'Failed to create client configuration in panel'
            }), 500
        
        # Calculate expiry date
        expiry_date = None
        if expiry_days > 0:
            expiry_date = datetime.utcnow() + timedelta(days=expiry_days)
        
        # Create subscription in database
        subscription = Subscription(
            customer_id=customer.id,
            uuid=config['uuid'],
            inbound_id=inbound_id,
            service_name=service_name,
            traffic_limit_gb=traffic_limit_gb,
            expiry_date=expiry_date,
            is_active=True
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        logger.info(f"Created subscription {subscription.uuid} for customer {customer.email}")
        
        return jsonify({
            'success': True,
            'subscription': subscription.to_dict(),
            'message': 'Subscription created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating subscription: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/subscriptions/<int:subscription_id>', methods=['GET'])
def get_subscription(subscription_id):
    """Get a specific subscription by ID"""
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        
        # Update traffic usage from panel
        try:
            customer = Customer.query.get(subscription.customer_id)
            traffic = panel_manager.get_client_traffic(customer.email)
            if traffic:
                # Convert bytes to GB
                traffic_used_bytes = traffic.get('down', 0) + traffic.get('up', 0)
                subscription.traffic_used_gb = traffic_used_bytes / (1024 ** 3)
                db.session.commit()
        except Exception as e:
            logger.warning(f"Failed to update traffic usage: {e}")
        
        return jsonify({
            'success': True,
            'subscription': subscription.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting subscription: {e}")
        return jsonify({'success': False, 'error': str(e)}), 404


@bp.route('/subscriptions/<int:subscription_id>', methods=['PUT'])
def update_subscription(subscription_id):
    """
    Update subscription
    
    Request body:
    {
        "service_name": "Premium Plan",
        "traffic_limit_gb": 200,
        "expiry_days": 60,
        "is_active": true
    }
    """
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        customer = Customer.query.get(subscription.customer_id)
        data = request.get_json()
        
        # Update fields
        if 'service_name' in data:
            subscription.service_name = data['service_name']
        
        traffic_limit_gb = data.get('traffic_limit_gb', subscription.traffic_limit_gb)
        expiry_days = data.get('expiry_days')
        is_active = data.get('is_active', subscription.is_active)
        
        # Calculate expiry date
        if expiry_days is not None:
            if expiry_days > 0:
                subscription.expiry_date = datetime.utcnow() + timedelta(days=expiry_days)
            else:
                subscription.expiry_date = None
        
        subscription.traffic_limit_gb = traffic_limit_gb
        subscription.is_active = is_active
        
        # Update in panel
        if expiry_days is not None:
            panel_manager.update_client_config(
                uuid=subscription.uuid,
                inbound_id=subscription.inbound_id,
                email=customer.email,
                traffic_gb=traffic_limit_gb,
                expiry_days=expiry_days if expiry_days > 0 else 0,
                enable=is_active
            )
        
        db.session.commit()
        
        logger.info(f"Updated subscription {subscription.uuid}")
        
        return jsonify({
            'success': True,
            'subscription': subscription.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating subscription: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/subscriptions/<int:subscription_id>', methods=['DELETE'])
def delete_subscription(subscription_id):
    """Delete a subscription"""
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        
        # Delete from panel
        try:
            panel_manager.delete_client_config(
                subscription.inbound_id,
                subscription.uuid
            )
        except Exception as e:
            logger.warning(f"Failed to delete from panel: {e}")
        
        db.session.delete(subscription)
        db.session.commit()
        
        logger.info(f"Deleted subscription {subscription.uuid}")
        
        return jsonify({
            'success': True,
            'message': 'Subscription deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting subscription: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/subscriptions/<int:subscription_id>/traffic', methods=['GET'])
def get_subscription_traffic(subscription_id):
    """Get traffic statistics for a subscription"""
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        customer = Customer.query.get(subscription.customer_id)
        
        traffic = panel_manager.get_client_traffic(customer.email)
        
        if traffic:
            # Convert bytes to GB
            down_gb = traffic.get('down', 0) / (1024 ** 3)
            up_gb = traffic.get('up', 0) / (1024 ** 3)
            total_gb = down_gb + up_gb
            
            # Update subscription
            subscription.traffic_used_gb = total_gb
            db.session.commit()
            
            return jsonify({
                'success': True,
                'traffic': {
                    'download_gb': round(down_gb, 2),
                    'upload_gb': round(up_gb, 2),
                    'total_gb': round(total_gb, 2),
                    'limit_gb': subscription.traffic_limit_gb,
                    'remaining_gb': round(subscription.remaining_traffic_gb(), 2)
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to get traffic statistics'
            }), 500
            
    except Exception as e:
        logger.error(f"Error getting traffic: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/subscriptions/<int:subscription_id>/reset-traffic', methods=['POST'])
def reset_subscription_traffic(subscription_id):
    """Reset traffic statistics for a subscription (3X-UI only)"""
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        customer = Customer.query.get(subscription.customer_id)
        
        success = panel_manager.reset_client_traffic(
            subscription.inbound_id,
            customer.email
        )
        
        if success:
            subscription.traffic_used_gb = 0.0
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Traffic reset successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to reset traffic'
            }), 500
            
    except Exception as e:
        logger.error(f"Error resetting traffic: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/inbounds', methods=['GET'])
def get_inbounds():
    """Get list of all inbounds from panel"""
    try:
        inbounds = panel_manager.get_inbounds()
        
        if inbounds is not None:
            return jsonify({
                'success': True,
                'inbounds': inbounds
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to get inbounds'
            }), 500
            
    except Exception as e:
        logger.error(f"Error getting inbounds: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/register', methods=['POST'])
def register_customer_and_subscription():
    """
    Complete registration: Create customer and subscription in one request
    
    Request body:
    {
        "email": "customer@example.com",
        "name": "Customer Name",
        "phone": "+1234567890",
        "telegram_id": "@username",
        "service_name": "Basic Plan",
        "traffic_limit_gb": 100,
        "expiry_days": 30,
        "inbound_id": 1
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Email and name are required'
            }), 400
        
        # Check if customer already exists
        customer = Customer.query.filter_by(email=data['email']).first()
        
        if not customer:
            # Create new customer
            customer = Customer(
                email=data['email'],
                name=data['name'],
                phone=data.get('phone'),
                telegram_id=data.get('telegram_id')
            )
            db.session.add(customer)
            db.session.flush()  # Get customer ID
            
            logger.info(f"Created new customer: {customer.email}")
        
        # Get parameters
        traffic_limit_gb = data.get('traffic_limit_gb', 100)
        expiry_days = data.get('expiry_days', 30)
        inbound_id = data.get('inbound_id', 1)
        service_name = data.get('service_name', 'Standard Plan')
        
        # Create client config in panel
        config = panel_manager.create_client_config(
            email=customer.email,
            inbound_id=inbound_id,
            traffic_gb=traffic_limit_gb,
            expiry_days=expiry_days,
            enable=True
        )
        
        if not config:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Failed to create client configuration in panel'
            }), 500
        
        # Calculate expiry date
        expiry_date = None
        if expiry_days > 0:
            expiry_date = datetime.utcnow() + timedelta(days=expiry_days)
        
        # Create subscription in database
        subscription = Subscription(
            customer_id=customer.id,
            uuid=config['uuid'],
            inbound_id=inbound_id,
            service_name=service_name,
            traffic_limit_gb=traffic_limit_gb,
            expiry_date=expiry_date,
            is_active=True
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        logger.info(f"Registration complete for {customer.email} with subscription {subscription.uuid}")
        
        return jsonify({
            'success': True,
            'customer': customer.to_dict(),
            'subscription': subscription.to_dict(),
            'message': 'Registration completed successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during registration: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
