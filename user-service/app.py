from flask import Flask, redirect, url_for, request

app = Flask(__name__)





#
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from sqlalchemy import create_engine, Column, Integer, String, Table, ForeignKey
# from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# app = FastAPI()
# engine = create_engine("sqlite:///./data/users.db", connect_args={"check_same_thread": False})
# Session = sessionmaker(bind=engine)
# Base = declarative_base()

# # Models
# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, unique=True)

# class Conversation(Base):
#     __tablename__ = "conversations"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, unique=True)

# class Membership(Base):
#     __tablename__ = "memberships"
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     conv_id = Column(Integer, ForeignKey("conversations.id"))

# Base.metadata.create_all(bind=engine)

# # Schemas
# class UserIn(BaseModel):
#     name: str

# class ConvIn(BaseModel):
#     user_id: int
#     name: str

# @app.post("/api/users")
# def create_user(u: UserIn):
#     db = Session()
#     user = User(name=u.name)
#     db.add(user)
#     try:
#         db.commit()
#         db.refresh(user)
#     except:
#         db.rollback()
#         raise HTTPException(400, "User already exists")
#     return {"id": user.id, "name": user.name}

# @app.post("/api/conversations")
# def create_conv(c: ConvIn):
#     db = Session()
#     conv = Conversation(name=c.name)
#     db.add(conv)
#     db.commit()
#     # add membership
#     mem = Membership(user_id=c.user_id, conv_id=conv.id)
#     db.add(mem)
#     db.commit()
#     return {"id": conv.id, "name": conv.name}



# # Create user-service/app.py
# from fastapi import FastAPI, HTTPException, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from pydantic import BaseModel
# import os
# from datetime import datetime

# app = FastAPI()

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Database setup
# DATABASE_URL = os.environ.get('USER_DB_URL', 'postgresql://user_db_user:user_db_password@user_db:5432/user_db')
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# # Models
# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, index=True)

# class Conversation(Base):
#     __tablename__ = "conversations"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, unique=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"))

# # Pydantic models for request/response
# class UserCreate(BaseModel):
#     username: str

# class UserResponse(BaseModel):
#     id: int
#     username: str

# class ConversationCreate(BaseModel):
#     name: str
#     user_id: int

# class ConversationResponse(BaseModel):
#     id: int
#     name: str
#     user_id: int

# # Create tables
# Base.metadata.create_all(bind=engine)

# @app.post("/api/users", response_model=UserResponse)
# def create_user(user: UserCreate):
#     db = SessionLocal()
#     try:
#         db_user = User(username=user.username)
#         db.add(db_user)
#         db.commit()
#         db.refresh(db_user)
#         return UserResponse(id=db_user.id, username=db_user.username)
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=400, detail=str(e))
#     finally:
#         db.close()

# @app.get("/api/users/{user_id}", response_model=UserResponse)
# def get_user(user_id: int):
#     db = SessionLocal()
#     try:
#         user = db.query(User).filter(User.id == user_id).first()
#         if user is None:
#             raise HTTPException(status_code=404, detail="User not found")
#         return UserResponse(id=user.id, username=user.username)
#     finally:
#         db.close()

# @app.get("/api/users", response_model=list[UserResponse])
# def get_users():
#     db = SessionLocal()
#     try:
#         users = db.query(User).all()
#         return [UserResponse(id=user.id, username=user.username) for user in users]
#     finally:
#         db.close()

# @app.post("/conversations", response_model=ConversationResponse)
# def create_conversation(conversation: ConversationCreate):
#     db = SessionLocal()
#     try:
#         # Verify user exists
#         user = db.query(User).filter(User.id == conversation.user_id).first()
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")
        
#         # Create conversation
#         db_conversation = Conversation(
#             name=conversation.name,
#             user_id=conversation.user_id
#         )
#         db.add(db_conversation)
#         db.commit()
#         db.refresh(db_conversation)
#         return db_conversation
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=400, detail=str(e))
#     finally:
#         db.close()

# @app.get("/conversations/{conversation_id}", response_model=ConversationResponse)
# def get_conversation(conversation_id: int):
#     db = SessionLocal()
#     conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
#     if not conversation:
#         raise HTTPException(status_code=404, detail="Conversation not found")
#     return conversation