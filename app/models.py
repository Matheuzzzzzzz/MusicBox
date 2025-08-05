from app import db
from datetime import datetime

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), index=True)
    track_id = db.Column(db.String(100), index=True)
    track_name = db.Column(db.String(250))
    artist_name = db.Column(db.String(250))
    rating_value = db.Column(db.Integer)
    review = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<Rating {self.track_name} by {self.user_id}>'