from __init__ import db
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(50), unique=True, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    fee = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(50))  # 'transfer', 'add_funds', etc.
    status = db.Column(db.String(20), default='completed')  # 'pending', 'completed', 'failed'
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'sender_id': self.sender_id,
            'sender_name': f"{self.sender.first_name} {self.sender.last_name}" if self.sender else None,
            'receiver_id': self.receiver_id,
            'receiver_name': f"{self.receiver.first_name} {self.receiver.last_name}" if self.receiver else None,
            'amount': round(self.amount, 2),
            'fee': round(self.fee, 2),
            'total_amount': round(self.total_amount, 2),
            'type': self.type,
            'status': self.status,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }