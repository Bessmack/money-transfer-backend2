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

        receiver = User.query.get(receiver_id)
        if not receiver:
            return jsonify({'error': 'Receiver not found'}), 404

        receiver_wallet = Wallet.query.filter_by(user_id=receiver_id).first()
        if not receiver_wallet:
            return jsonify({'error': 'Receiver wallet not found'}), 404

        fee = calculate_fee(amount)
        total_amount = amount + fee

        if sender_wallet.balance < total_amount:
            return jsonify({'error': 'Insufficient balance'}), 400

        sender_wallet.balance -= total_amount
        receiver_wallet.balance += amount
        sender_wallet.updated_at = datetime.utcnow()
        receiver_wallet.updated_at = datetime.utcnow()

        sender = User.query.get(current_user_id)

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

        transaction_data = transaction.to_dict()
        transaction_data.update({
            'sender_name': f"{sender.first_name} {sender.last_name}",
            'receiver_name': f"{receiver.first_name} {receiver.last_name}"
        })

        return jsonify({
            'message': 'Money sent successfully',
            'transaction': transaction_data,
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
        transaction_type = request.args.get('type', 'all')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))

        query = Transaction.query
        if transaction_type == 'sent':
            query = query.filter_by(sender_id=current_user_id)
        elif transaction_type == 'received':
            query = query.filter_by(receiver_id=current_user_id)
        else:
            query = query.filter(
                (Transaction.sender_id == current_user_id) |
                (Transaction.receiver_id == current_user_id)
            )

        transactions = query.order_by(Transaction.created_at.desc()) \
            .limit(limit).offset(offset).all()

        # Get all unique user IDs
        user_ids = set()
        for t in transactions:
            user_ids.add(t.sender_id)
            user_ids.add(t.receiver_id)
        
        # Fetch all users at once
        users = User.query.filter(User.id.in_(user_ids)).all()
        user_dict = {u.id: u for u in users}

        # Build transaction list
        transactions_list = []
        for t in transactions:
            sender = user_dict.get(t.sender_id)
            receiver = user_dict.get(t.receiver_id)

            t_data = t.to_dict()
            t_data.update({
                'sender_name': f"{sender.first_name} {sender.last_name}" if sender else None,
                'receiver_name': f"{receiver.first_name} {receiver.last_name}" if receiver else None
            })
            transactions_list.append(t_data)

        return jsonify({
            'transactions': transactions_list,
            'count': len(transactions_list)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<string:transaction_id>', methods=['GET'])
@jwt_required()
def get_transaction(transaction_id):
    try:
        current_user_id = get_jwt_identity()
        transaction = Transaction.query.filter_by(transaction_id=transaction_id).first()

        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404

        if transaction.sender_id != current_user_id and transaction.receiver_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        sender = User.query.get(transaction.sender_id)
        receiver = User.query.get(transaction.receiver_id)

        transaction_data = transaction.to_dict()
        transaction_data.update({
            'sender_name': f"{sender.first_name} {sender.last_name}" if sender else None,
            'receiver_name': f"{receiver.first_name} {receiver.last_name}" if receiver else None
        })

        return jsonify({'transaction': transaction_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500