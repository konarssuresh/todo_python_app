from fastapi import APIRouter,HTTPException,Depends,Path
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status

from database import SessionLocal
from .auth import get_current_user
from models import Todos, Users

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict,Depends(get_current_user)]



@router.get("/todos",status_code=status.HTTP_200_OK)
async def read_all(user:user_dependency,db:db_dependency):
    if user is None or user.get("user_role") != 'Admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication Failed")
    return db.query(Todos).all()


@router.delete("/todos/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_one(user:user_dependency,db:db_dependency,todo_id:int = Path(gt=0)):
    if user is None or user.get("user_role") != 'Admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication Failed")
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Todo not found")
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()

@router.get("/users",status_code=status.HTTP_200_OK)
async def read_all_users(db:db_dependency,user: user_dependency):
    if user is None or user.get("user_role") != 'Admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    return db.query(Users).all()

@router.get("/users/{user_id}",status_code=status.HTTP_200_OK)
async def read_one_user(db:db_dependency,user: user_dependency,user_id:int=Path(gt=0)):
    if user is None or user.get("user_role")!= "Admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication Failed")
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    return user_model