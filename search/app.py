import os
from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from transcriber.app import Transcription  # share model definition

app = Flask(__name__)
engine = create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)

@app.route('/search', methods=['GET'])
def search():
    user_id = request.args.get('user_id')
    db = Session()
    rows = db.query(Transcription).filter_by(user_id=user_id)\
             .order_by(Transcription.timestamp).all()
    convo = [r.text for r in rows]
    return jsonify({'conversation': convo})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
