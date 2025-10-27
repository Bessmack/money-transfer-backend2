from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from __init__ import db
from models import Beneficiary

bp = Blueprint('beneficiary', __name__, url_prefix='/api/beneficiaries')

@bp.route('', methods=['GET', 'POST'])
@jwt_required()
def beneficiaries():
    try:
        current_user_id = get_jwt_identity()
        
        if request.method == 'GET':
            beneficiaries = Beneficiary.query.filter_by(user_id=current_user_id).all()
            return jsonify({
                'beneficiaries': [b.to_dict() for b in beneficiaries]
            }), 200
        
        # POST - Create new beneficiary
        data = request.get_json()
        
        if not data.get('name') or not data.get('email'):
            return jsonify({'error': 'Name and email are required'}), 400
        
        beneficiary = Beneficiary(
            user_id=current_user_id,
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            relationship=data.get('relationship')
        )
        
        db.session.add(beneficiary)
        db.session.commit()
        
        return jsonify({
            'message': 'Beneficiary added successfully',
            'beneficiary': beneficiary.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:beneficiary_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def beneficiary_detail(beneficiary_id):
    try:
        current_user_id = get_jwt_identity()
        beneficiary = Beneficiary.query.get(beneficiary_id)
        
        if not beneficiary:
            return jsonify({'error': 'Beneficiary not found'}), 404
        
        # Check ownership
        if beneficiary.user_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if request.method == 'GET':
            return jsonify({'beneficiary': beneficiary.to_dict()}), 200
        
        elif request.method == 'PUT':
            data = request.get_json()
            
            if 'name' in data:
                beneficiary.name = data['name']
            if 'email' in data:
                beneficiary.email = data['email']
            if 'phone' in data:
                beneficiary.phone = data['phone']
            if 'relationship' in data:
                beneficiary.relationship = data['relationship']
            
            db.session.commit()
            
            return jsonify({
                'message': 'Beneficiary updated successfully',
                'beneficiary': beneficiary.to_dict()
            }), 200
        
        elif request.method == 'DELETE':
            db.session.delete(beneficiary)
            db.session.commit()
            
            return jsonify({'message': 'Beneficiary deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500