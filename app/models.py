from . import db
from flask_login import UserMixin
from . import login_manager
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    texts = db.relationship('TextForReading', backref='user', lazy=True)

class TextForReading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(Text(length=4294967295), nullable=True)
    url = db.Column(db.String(500), nullable=True)
    url2 = db.Column(db.String(500), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    training_lists = db.relationship('TrainingList', backref='text', lazy=True)

class TrainingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    text_id = db.Column(db.Integer, db.ForeignKey('text_for_reading.id'), nullable=False)
    lang_from = db.Column(db.String(10, collation="utf8mb4_unicode_ci"), db.ForeignKey('training_lang.lang_code'), default="en")
    lang_to = db.Column(db.String(10, collation="utf8mb4_unicode_ci"), db.ForeignKey('training_lang.lang_code'), default="bg")
    training_items = db.relationship(
        'TrainingItem',
        backref='list',
        lazy=True,
        cascade='all, delete-orphan'
    )

class TrainingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phrase = db.Column(db.String(200), nullable=False)
    translation = db.Column(db.Text, nullable=False)
    context = db.Column(db.Text)
    training_order = db.Column(db.Integer, default=1)
    num_first_attempt = db.Column(db.Integer, default=0)
    num_second_attempt = db.Column(db.Integer, default=0)
    num_extra_attempt = db.Column(db.Integer, default=0)
    num_skipped = db.Column(db.Integer, default=0)
    last_trained_at = db.Column(db.DateTime)
    last_result = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    training_list_id = db.Column(
        db.Integer,
        db.ForeignKey('training_list.id', ondelete='CASCADE'),
        nullable=False
    )

class TrainingLang(db.Model):
    __tablename__ = 'training_lang'

    lang_code = db.Column(db.String(10, collation="utf8mb4_unicode_ci"), primary_key=True)
    lang_name = db.Column(db.String(100, collation="utf8mb4_unicode_ci"), nullable=False)
    native_name = db.Column(db.String(100, collation="utf8mb4_unicode_ci"), nullable=False)

    def __repr__(self):
        return f"<TrainingLang {self.lang_code}>"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
