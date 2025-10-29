from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from __init__ import db
from models import User, Wallet, Transaction
from utils.helpers import generate_unique_id
from datetime import datetime

bp = Blueprint('wallet', __name__, url_prefix='/api/wallet')


@bp.route('', methods=['GET'])
@jwt_required()
def get_wallet():
    try:
        print("🔍 Wallet endpoint called")  # ADD THIS
        current_user_id = get_jwt_identity()
        print(f"👤 Current user ID: {current_user_id}")  # ADD THIS
        
        wallet = Wallet.query.filter_by(user_id=current_user_id).first()

        if not wallet:
            print(f"❌ No wallet found for user {current_user_id}")  # ADD THIS
            return jsonify({'error': 'Wallet not found'}), 404

        print(f"✅ Wallet found: {wallet.wallet_id}")  # ADD THIS
        return jsonify({'wallet': wallet.to_dict()}), 200

    except Exception as e:
        print(f"❌ Error in get_wallet: {str(e)}")  # ADD THIS
        return jsonify({'error': str(e)}), 500

@bp.route('/add-funds', methods=['POST'])
@jwt_required()
def add_funds():
    try:
        current_user_id = get_jwt_identity()
        wallet = Wallet.query.filter_by(user_id=current_user_id).first()

        if not wallet:
            return jsonify({'error': 'Wallet not found'}), 404

        data = request.get_json()
        amount = float(data.get('amount', 0))

        if amount <= 0:
            return jsonify({'error': 'Invalid amount'}), 400

        wallet.balance = max(wallet.balance + amount, 0)
        wallet.updated_at = datetime.utcnow()

        transaction = Transaction(
            transaction_id=generate_unique_id('TXN', 7),
            sender_id=current_user_id,
            receiver_id=current_user_id,
            amount=amount,
            fee=0.0,
            total_amount=amount,
            type='add_funds',
            status='completed',
            note=data.get('note', 'Added funds to wallet')
        )

        db.session.add(transaction)
        db.session.commit()

        return jsonify({
            'message': 'Funds added successfully',
            'wallet': wallet.to_dict(),
            'transaction': transaction.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
