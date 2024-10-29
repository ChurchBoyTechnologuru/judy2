# app.py
from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models
class Guest(db.Model, SerializerMixin):
    __tablename__ = 'guests'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    occupation = db.Column(db.String)
    
    appearances = db.relationship('Appearance', back_populates='guest')
    serialize_rules = ('-appearances.guest',)
    
    @validates('name')
    def validate_name(self, key, name):
        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string")
        return name

class Episode(db.Model, SerializerMixin):
    __tablename__ = 'episodes'
    
    id = db.Column(db.Integer, primary_key=True)
    air_date = db.Column(db.DateTime, nullable=False)
    episode_number = db.Column(db.Integer, nullable=False)
    
    appearances = db.relationship('Appearance', back_populates='episode')
    serialize_rules = ('-appearances.episode',)

class Appearance(db.Model, SerializerMixin):
    __tablename__ = 'appearances'
    
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)
    guest_id = db.Column(db.Integer, db.ForeignKey('guests.id'))
    episode_id = db.Column(db.Integer, db.ForeignKey('episodes.id'))
    
    guest = db.relationship('Guest', back_populates='appearances')
    episode = db.relationship('Episode', back_populates='appearances')
    serialize_rules = ('-guest.appearances', '-episode.appearances',)
    
    @validates('rating')
    def validate_rating(self, key, rating):
        if rating and (rating < 1 or rating > 10):
            raise ValueError("Rating must be between 1 and 10")
        return rating

# Routes
@app.route('/guests', methods=['GET'])
def get_guests():
    guests = Guest.query.all()
    return jsonify([guest.to_dict() for guest in guests]), 200

@app.route('/guests/<int:id>', methods=['GET'])
def get_guest(id):
    guest = Guest.query.get(id)
    if not guest:
        return make_response(jsonify({"error": "Guest not found"}), 404)
    return jsonify(guest.to_dict()), 200

@app.route('/episodes', methods=['GET'])
def get_episodes():
    episodes = Episode.query.all()
    return jsonify([episode.to_dict() for episode in episodes]), 200

@app.route('/episodes/<int:id>', methods=['GET'])
def get_episode(id):
    episode = Episode.query.get(id)
    if not episode:
        return make_response(jsonify({"error": "Episode not found"}), 404)
    return jsonify(episode.to_dict()), 200

@app.route('/appearances', methods=['GET', 'POST'])
def handle_appearances():
    if request.method == 'GET':
        appearances = Appearance.query.all()
        return jsonify([appearance.to_dict() for appearance in appearances]), 200
    
    data = request.get_json()
    try:
        new_appearance = Appearance(
            rating=data.get('rating'),
            guest_id=data['guest_id'],
            episode_id=data['episode_id']
        )
        db.session.add(new_appearance)
        db.session.commit()
        return jsonify(new_appearance.to_dict()), 201
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)

@app.route('/appearances/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def handle_appearance(id):
    appearance = Appearance.query.get(id)
    if not appearance:
        return make_response(jsonify({"error": "Appearance not found"}), 404)
    
    if request.method == 'GET':
        return jsonify(appearance.to_dict()), 200
    
    elif request.method == 'PATCH':
        data = request.get_json()
        try:
            for attr in data:
                setattr(appearance, attr, data[attr])
            db.session.commit()
            return jsonify(appearance.to_dict()), 200
        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 400)
    
    elif request.method == 'DELETE':
        db.session.delete(appearance)
        db.session.commit()
        return '', 204

if __name__ == '__main__':
    app.run(port=5555, debug=True)
