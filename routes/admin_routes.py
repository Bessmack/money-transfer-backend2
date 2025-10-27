from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from __init__ import db
from models import User, Wallet, Transaction
from utils.decorators import admin_required
from datetime import datetime

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@bp.route('/users', methods=['GET'])
@admin_required
def admin_get_users():
    try:
        users = User.query.all()
        return jsonify({
            'users': [u.to_dict() for u in users],
            'count': len(users)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@admin_required
def admin_user_detail(user_id):
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if request.method == 'GET':
            return jsonify({
                'user': user.to_dict(),
                'wallet': user.wallet.to_dict() if user.wallet else None
            }), 200
        
        elif request.method == 'PUT':
            data = request.get_json()
            
            if 'status' in data:
                user.status = data['status']
            if 'role' in data:
                user.role = data['role']
            
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'message': 'User updated successfully',
                'user': user.to_dict()
            }), 200
        
        elif request.method == 'DELETE':
            db.session.delete(user)
            db.session.commit()
            
            return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/wallets', methods=['GET'])
@admin_required
def admin_get_wallets():
    try:
        wallets = Wallet.query.all()
        return jsonify({
            'wallets': [w.to_dict() for w in wallets],
            'count': len(wallets)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/wallets/<int:wallet_id>/adjust', methods=['POST'])
@admin_required
def admin_adjust_wallet(wallet_id):
    try:
        wallet = Wallet.query.get(wallet_id)
        
        if not wallet:
            return jsonify({'error': 'Wallet not found'}), 404
        
        data = request.get_json()
        action = data.get('action')  # 'add' or 'deduct'
        amount = float(data.get('amount', 0))
        
        if amount <= 0:
            return jsonify({'error': 'Invalid amount'}), 400
        
        if action == 'add':
            wallet.balance += amount
        elif action == 'deduct':
            if wallet.balance < amount:
                return jsonify({'error': 'Insufficient balance'}), 400
            wallet.balance -= amount
        else:
            return jsonify({'error': 'Invalid action'}), 400
        
        wallet.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': f'Wallet {action}ed successfully',
            'wallet': wallet.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/transactions', methods=['GET'])
@admin_required
def admin_get_transactions():
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        transactions = Transaction.query\
            .order_by(Transaction.created_at.desc())\
            .limit(limit).offset(offset).all()
        
        return jsonify({
            'transactions': [t.to_dict() for t in transactions],
            'count': len(transactions)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/stats', methods=['GET'])
@admin_required
def admin_stats():
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(status='active').count()
        total_transactions = Transaction.query.count()
        total_revenue = db.session.query(db.func.sum(Transaction.fee)).scalar() or 0
        total_wallet_balance = db.session.query(db.func.sum(Wallet.balance)).scalar() or 0
        
        return jsonify({
            'total_users': total_users,
            'active_users': active_users,
            'total_transactions': total_transactions,
            'total_revenue': round(total_revenue, 2),
            'total_wallet_balance': round(total_wallet_balance, 2)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500