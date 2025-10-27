from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from __init__ import db
from models import User, Wallet, Transaction
from utils.helpers import generate_unique_id, calculate_fee
from datetime import datetime

bp = Blueprint('transaction', __name__, url_prefix='/api/transactions')

@bp.route('/send', methods=['POST'])
@jwt_required()
def send_money():
    try:
        current_user_id = get_jwt_identity()
        sender_wallet = Wallet.query.filter_by(user_id=current_user_id).first()
        
        if not sender_wallet:
            return jsonify({'error': 'Sender wallet not found'}), 404
        
        data = request.get_json()
        receiver_id = data.get('receiver_id')
        amount = float(data.get('amount', 0))
        
        if amount <= 0:
            return jsonify({'error': 'Invalid amount'}), 400
        
        # Get receiver
        receiver = User.query.get(receiver_id)
        if not receiver:
            return jsonify({'error': 'Receiver not found'}), 404
        
        receiver_wallet = Wallet.query.filter_by(user_id=receiver_id).first()
        if not receiver_wallet:
            return jsonify({'error': 'Receiver wallet not found'}), 404
        
        # Calculate fee and total
        fee = calculate_fee(amount)
        total_amount = amount + fee
        
        # Check if sender has sufficient balance
        if sender_wallet.balance < total_amount:
            return jsonify({'error': 'Insufficient balance'}), 400
        
        # Process transaction
        sender_wallet.balance -= total_amount
        receiver_wallet.balance += amount
        
        sender_wallet.updated_at = datetime.utcnow()
        receiver_wallet.updated_at = datetime.utcnow()
        
        # Create transaction record
        transaction = Transaction(
            transaction_id=generate_unique_id('TXN', 7),
            sender_id=current_user_id,
            receiver_id=receiver_id,
            amount=amount,
            fee=fee,
            total_amount=total_amount,
            type='transfer',
            status='completed',
            note=data.get('note', '')
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Money sent successfully',
            'transaction': transaction.to_dict(),
            'wallet': sender_wallet.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('', methods=['GET'])
@jwt_required()
def get_transactions():
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        transaction_type = request.args.get('type', 'all')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Build query
        if transaction_type == 'sent':
            transactions = Transaction.query.filter_by(sender_id=current_user_id)\
                .order_by(Transaction.created_at.desc())\
                .limit(limit).offset(offset).all()
        elif transaction_type == 'received':
            transactions = Transaction.query.filter_by(receiver_id=current_user_id)\
                .order_by(Transaction.created_at.desc())\
                .limit(limit).offset(offset).all()
        else:
            transactions = Transaction.query.filter(
                (Transaction.sender_id == current_user_id) | 
                (Transaction.receiver_id == current_user_id)
            ).order_by(Transaction.created_at.desc())\
             .limit(limit).offset(offset).all()
        
        return jsonify({
            'transactions': [t.to_dict() for t in transactions],
            'count': len(transactions)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:transaction_id>', methods=['GET'])
@jwt_required()
def get_transaction(transaction_id):
    try:
        current_user_id = get_jwt_identity()
        transaction = Transaction.query.get(transaction_id)
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        # Check if user is authorized to view this transaction
        if transaction.sender_id != current_user_id and transaction.receiver_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify({'transaction': transaction.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500