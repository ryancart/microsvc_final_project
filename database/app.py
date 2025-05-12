from flask import Flask, request, jsonify
from datetime import datetime
from models import db, Transcription

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI']   = 'sqlite:///transcriptions.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)


    with app.app_context():
        db.create_all()


    @app.route('/transcriptions', methods=['POST'])
    def add_transcription():
        data = request.get_json()
        rec = Transcription(
            first_name        = data['first_name'],
            last_name         = data['last_name'],
            conversation_name = data['conversation_name'],
            text              = data['text'],
            created_at        = datetime.fromisoformat(data['created_at'])
        )
        db.session.add(rec)
        db.session.commit()
        return jsonify({"id": rec.id}), 201

    @app.route('/transcriptions', methods=['GET'])
    def list_transcriptions():
        results = Transcription.query.all()
        return jsonify([
            {
                "id": r.id,
                "first_name": r.first_name,
                "last_name": r.last_name,
                "conversation_name": r.conversation_name,
                "text": r.text,
                "created_at": r.created_at.isoformat()
            } for r in results
        ])

    return app

# for gunicorn: point at "app:create_app()"

if __name__ == '__main__':
    create_app().run(host='0.0.0.0', port=8004)
