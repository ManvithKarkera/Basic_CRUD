from datetime import datetime, timezone
from typing import Dict, Any
from app.extensions import db


class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='TODO')
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'sno': self.sno,
            'title': self.title,
            'desc': self.desc,
            'status': self.status,
            'date_created': self.date_created.isoformat() if self.date_created else None
        }
