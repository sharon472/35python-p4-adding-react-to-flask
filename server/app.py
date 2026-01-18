from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

# ----------------- App Setup -----------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app, supports_credentials=True)  # React fetch with credentials
db.init_app(app)
migrate = Migrate(app, db)

# ----------------- Routes -----------------
@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at).all()
        return make_response(jsonify([m.to_dict() for m in messages]), 200)

    elif request.method == 'POST':
        data = request.get_json()
        message = Message(body=data['body'], username=data['username'])
        db.session.add(message)
        db.session.commit()
        return make_response(jsonify(message.to_dict()), 201)

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.get_or_404(id)

    if request.method == 'PATCH':
        data = request.get_json()
        for key, value in data.items():
            setattr(message, key, value)
        db.session.commit()
        return make_response(jsonify(message.to_dict()), 200)

    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        return make_response(jsonify({'deleted': True}), 200)

# ----------------- Run -----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure tables exist before starting
    app.run(port=5555, debug=True)

