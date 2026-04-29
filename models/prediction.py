# models/prediction.py
from datetime import datetime
from extensions.db import db

class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
    image_path = db.Column(db.String(200), nullable=False)
    image_filename = db.Column(db.String(200), nullable=True)
    disease_name = db.Column(db.String(100), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    def __repr__(self):
        return f"<Prediction {self.id}: {self.disease_name} ({self.confidence:.2f})>"
    def to_dict(self):
        """Convert prediction to dictionary for API responses"""
        return {
            "id": self.id,
            "disease_name": self.disease_name,
            "display_name": self.get_display_name(),
            "confidence": round(self.confidence * 100, 2),
            "confidence_raw": self.confidence,
            "image_path": self.image_path,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "date": self.created_at.strftime("%d %b %Y"),
            "time": self.created_at.strftime("%I:%M %p"),
            "is_healthy": self.disease_name == "Healthy",
            "badge_class": self.get_badge_class(),
            "confidence_class": self.get_confidence_class()
        }
    def get_display_name(self):
        """Get display name for disease"""
        if self.disease_name == "Healthy":
            return "🌿 Healthy Plant"
        elif self.disease_name == "Rice_blast":
            return "🔥 Leaf Blast"
        elif self.disease_name == "Rice_brown_spot":
            return "🟤 Brown Spot"
        elif self.disease_name == "Rice_bacterial_blight":
            return "🦠 Bacterial Blight"
        else:
            return self.disease_name.replace("_", " ").title()
    def get_badge_class(self):
        """Get badge class for disease type"""
        if self.disease_name == "Healthy":
            return "healthy"
        else:
            return "disease"


    def get_confidence_class(self):
        """Get CSS class based on confidence level"""
        if self.confidence > 0.8:
            return "text-green-600"
        elif self.confidence > 0.6:
            return "text-yellow-600"
        else:
            return "text-red-600"
    @staticmethod
    def get_user_predictions(user_id, limit=5):
        """Get recent predictions of a user"""
        return (
            Prediction.query
            .filter_by(user_id=user_id)
            .order_by(Prediction.created_at.desc())
            .limit(limit)
            .all()
        )
    @staticmethod
    def get_count(user_id):
        """Get prediction count for a user"""
        return Prediction.query.filter_by(user_id=user_id).count()