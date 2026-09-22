from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from typing import Annotated, Literal, Optional
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Users, Donors
from jose import jwt
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse


router = APIRouter()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "11453e03ce56cdc2659883aaabf67d4490aa0c108294662ec4d9020d83d57c1f"
ALGORITHM = "HS256"


class CreateUsers(BaseModel):
    name: str
    email: str
    hashed_password: str
    phone_number: str
    role: Literal["donor", "requester", "admin"]
    city: str
    area: str
    is_verified: bool = False
    created_at: str = datetime.now(timezone.utc).isoformat()


class UpdateUsers(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    city: Optional[str] = None
    area: Optional[str] = None




def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]



def authenticate_user(db: Session, name: str, password: str):
    user = db.query(Users).filter(Users.name == name).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expire = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_bearer), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(Users).filter(Users.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/register")
def register(user: CreateUsers, db: db_dependency):
    hashed_password = bcrypt_context.hash(user.hashed_password)
    db_user = Users(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        phone_number=user.phone_number,
        role=user.role,
        city=user.city,
        area=user.area,
        is_verified=user.is_verified,
        created_at=user.created_at
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return JSONResponse(status_code=201, content={"message": "User registered successfully", "user_id": db_user.id})


@router.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency,
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    token = create_access_token(user.name, user.id, timedelta(minutes=30))
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def read_users_me(current_user: user_dependency):
    return {"id": current_user.id, "name": current_user.name, "email": current_user.email, "phone_number": current_user.phone_number, "role": current_user.role, "city": current_user.city, "area": current_user.area, "is_verified": current_user.is_verified, "created_at": current_user.created_at}


@router.put("/update_user")
def update_user(user_update: UpdateUsers, current_user: user_dependency, db: db_dependency):
    user = db.query(Users).filter(Users.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.name is not None:
        user.name = user_update.name
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.phone_number is not None:
        user.phone_number = user_update.phone_number
    if user_update.city is not None:
        user.city = user_update.city
    if user_update.area is not None:
        user.area = user_update.area
    
    db.commit()
    db.refresh(user)   
    return {"message": "User updated successfully"}

@router.put("/forget_password")
def forget_password(email: str, new_password: str, db: db_dependency, current_user: user_dependency):
    user = db.query(Users).filter(Users.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    hashed_password = bcrypt_context.hash(new_password)
    user.hashed_password = hashed_password
    
    db.commit()
    db.refresh(user)   
    return {"message": "Password updated successfully"}





