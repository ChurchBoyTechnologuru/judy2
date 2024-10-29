from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, Guest, Episode, Appearance

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

# Guest routes
@app.route('/guests', methods=['GET'])
def get_guests():
    guests = Guest.query.all()
    return jsonify([guest.to_dict() for guest in guests])

@app.route('/guests/<int:id>', methods=['GET']) 
def get_guest(id):
    guest = Guest.query.get(id)
    if not guest:
        return make_response(jsonify({'error': 'Guest not found'}), 404)
    return jsonify(guest.to_dict())

@app.route('/guests', methods=['POST'])
def create_guest():
    data = request.get_json()
    try:
        guest = Guest(
            name=data['name'],
            occupation=data.get('occupation'),
            catchphrase=data.get('catchphrase')
        )
        db.session.add(guest)
        db.session.commit()
        return jsonify(guest.to_dict()), 201
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)

# Episode routes
@app.route('/episodes', methods=['GET'])
def get_episodes():
    episodes = Episode.query.all()
    return jsonify([episode.to_dict() for episode in episodes])

@app.route('/episodes/<int:id>', methods=['GET'])
def get_episode(id):
    episode = Episode.query.get(id)
    if not episode:
        return make_response(jsonify({'error': 'Episode not found'}), 404)
    return jsonify(episode.to_dict())

@app.route('/episodes', methods=['POST']) 
def create_episode():
    data = request.get_json()
    try:
        episode = Episode(
            title=data['title'],
            air_date=data.get('air_date'),
            number=data.get('number')
        )
        db.session.add(episode)
        db.session.commit()
        return jsonify(episode.to_dict()), 201
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)

# Appearance routes
@app.route('/appearances', methods=['GET'])
def get_appearances():
    appearances = Appearance.query.all()
    return jsonify([appearance.to_dict() for appearance in appearances])

@app.route('/appearances/<int:id>', methods=['GET'])
def get_appearance(id):
    appearance = Appearance.query.get(id)
    if not appearance:
        return make_response(jsonify({'error': 'Appearance not found'}), 404)
    return jsonify(appearance.to_dict())

@app.route('/appearances', methods=['POST'])
def create_appearance():
    data = request.get_json()
    try:
        appearance = Appearance(
            rating=data['rating'],
            guest_id=data['guest_id'],
            episode_id=data['episode_id']
        )
        db.session.add(appearance)
        db.session.commit()
        return jsonify(appearance.to_dict()), 201
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
