from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class SearchQuery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_term = db.Column(db.String(255), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    products = db.relationship('Product', backref='search_query', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_term = db.Column(db.String(255), db.ForeignKey('search_query.search_term'))
    title = db.Column(db.String(255))
    price = db.Column(db.String(50))
    link = db.Column(db.String(255))
    image = db.Column(db.String(255))
    source = db.Column(db.String(50))  # 'flipkart' or 'amazon'
    specs = db.Column(db.Text)  # JSON string of specifications

    def get_specs(self) -> dict:
        try:
            return json.loads(self.specs) if self.specs else {}
        except:
            return {}

    def set_specs(self, specs: dict):
        self.specs = json.dumps(specs)