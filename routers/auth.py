from datetime import timedelta, datetime, timezone

from fastapi import  APIRouter,Depends,HTTPException,Request
from starlette import status
from pydantic import BaseModel,Field
from sqlalchemy.orm import Session
from typing import Annotated
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt

from models import Users
from database import SessionLocal
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

SECRET_KEY = 'secret'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=["bcrypt"],deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def authenticate_user(username:str,password:str,db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    elif not bcrypt_context.verify(password,user.hashed_password):
        return False
    else:
        return user

def create_access_token(username:str,userid:int,role:str,expires_delta:timedelta):
    encode = {'sub':username,'id':userid,'role':role}
    expires = datetime.now(timezone.utc)+expires_delta
    encode['exp']=expires
    return jwt.encode(encode,SECRET_KEY,algorithm='HS256')

async def get_current_user(token: Annotated[str,Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username:str = payload['sub']
        user_id:int= payload['id']
        user_role:str = payload['role']
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="could not validate creds")
        return {'username':username,'id':user_id,'user_role':user_role}
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate creds")

user_dependency = Annotated[dict, Depends(get_current_user)]

class CreateUserRequest(BaseModel):
    username: str
    email:str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number:str

class ChangePasswordRequest(BaseModel):
    old_password:str
    new_password:str

class ChangePhoneNumberRequest(BaseModel):
    phone_number: str

class Token(BaseModel):
    access_token:str
    token_type: str

api_dependencies = Annotated[Session,Depends(get_db)]

templates = Jinja2Templates(directory="templates")

### pages
@router.get("/login-page")
def render_login_page(request:Request):
    return templates.TemplateResponse(name="login.html",request=request)

@router.get("/register-page")
def render_register_page(request:Request):
    return templates.TemplateResponse(name="register.html",request=request)


### apis
@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_user(create_user_req: CreateUserRequest,db:api_dependencies):
    try:
        user_model = Users(
            username=create_user_req.username,
            email=create_user_req.email,
            first_name=create_user_req.first_name,
            last_name=create_user_req.last_name,
            hashed_password=bcrypt_context.hash(create_user_req.password),
            role=create_user_req.role,
            is_active=True,
            phone_number=create_user_req.phone_number
        )
        db.add(user_model)
        db.commit()
        return
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/token",status_code=status.HTTP_200_OK,response_model=Token)
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm, Depends()],db:api_dependencies):
    user = authenticate_user(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="could not validate creds")
    token = create_access_token(user.username,user.id,user.role,timedelta(minutes=20))
    return {'access_token':token,'token_type':'bearer'}

@router.get("/user",status_code=status.HTTP_200_OK)
async def get_current_users(user:user_dependency,db:api_dependencies):
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    return db.query(Users).filter(Users.id == user.get("id")).first()

@router.post("/change_password",status_code=status.HTTP_204_NO_CONTENT)
async def change_password(req:ChangePasswordRequest,db:api_dependencies,user:user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Failed to authenticate user")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if not user_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    elif not bcrypt_context.verify(req.old_password,user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Wrong password")
    else:
        hashed_password = bcrypt_context.hash(req.new_password)
        user_model.hashed_password = hashed_password
        db.commit()

@router.put("/change_phone_number",status_code=status.HTTP_202_ACCEPTED)
async def change_phone_number(req:ChangePhoneNumberRequest,db:api_dependencies,user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Failed to authenticate user")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if not user_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='User not found')
    user_model.phone_number = req.phone_number
    db.commit()
