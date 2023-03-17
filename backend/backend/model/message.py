from sqlalchemy import Column, Integer, String

from backend.model import db


class Message(db.Model):
    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)

    def to_dict(self):
        return {'text': self.text}
