from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime, timezone

db = SQLAlchemy()

class Transcription(db.Model):
    __tablename__ = 'transcriptions'

    id                = db.Column(db.Integer,  primary_key=True)
    first_name        = db.Column(db.String,   nullable=False)
    last_name         = db.Column(db.String,   nullable=False)
    conversation_name = db.Column(db.String,   nullable=False)
    text              = db.Column(db.Text,     nullable=False)
    created_at        = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )