import os, tempfile, datetime
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from engine import transcribe

app = Flask(__name__)
engine = create_engine(os.environ['DATABASE_URL'])
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Transcription(Base):
    __tablename__ = 'transcriptions'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    text = Column(Text)

Base.metadata.create_all(engine)

@app.route('/transcribe', methods=['POST'])
def do_transcribe():
    user_id = request.form.get('user_id')
    f = request.files['file']
    tmp = tempfile.NamedTemporaryFile(delete=False)
    f.save(tmp.name)
    text = transcribe(tmp.name)
    db = Session()
    rec = Transcription(user_id=user_id, text=text)
    db.add(rec)
    db.commit()
    return jsonify({'ok': True, 'text': text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
