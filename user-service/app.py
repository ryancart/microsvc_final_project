# Create user-service/app.py
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

app = FastAPI()
Base = declarative_base()

# Database setup
engine = create_engine(os.environ["USER_DB_URL"])
Session = sessionmaker(bind=engine)

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(engine)

@app.post("/users")
def create_user(username: str):
    db = Session()
    try:
        user = User(username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"user_id": user.id, "username": user.username}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        db.close()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    db = Session()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user.id, "username": user.username}