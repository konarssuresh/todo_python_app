
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException,Path,Request,status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from models import Todos
from .auth import get_current_user
from database import SessionLocal
router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)
templates = Jinja2Templates(directory="templates")

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description:str= Field(min_length=3,max_length=100)
    priority:int= Field(gt=0,lt=6)
    complete:bool= Field(default=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def redirect_to_login():
    rediret_response = RedirectResponse(url="/auth/login-page",status_code=status.HTTP_302_FOUND)
    rediret_response.delete_cookie(key="access_token")
    return rediret_response

db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict,Depends(get_current_user)]

### pages
@router.get("/todo-page")
async def render_todo_page(request: Request,db: db_dependency):
    try:
        print('cookieValue ',request.cookies.get("access_token"))
        user= await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()

        todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()
        return templates.TemplateResponse(request,name="todos.html" ,context={"todos":todos,"user":user})
    except:
        return redirect_to_login()

@router.get("/add-todo-page")
async def render_todo_page(request:Request,db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()
        return templates.TemplateResponse(request,name="add-todo.html",context={"request":request,"user":user})
    except:
        return redirect_to_login()

@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request:Request,db: db_dependency,todo_id:int=Path(gt=0)):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()
        todo = db.query(Todos).filter(Todos.id == todo_id).first()
        return templates.TemplateResponse(request,name="edit-todo.html", context={"request":request,"user":user,"todo":todo})
    except:
        return redirect_to_login()

### endpoints
@router.get("/",status_code=status.HTTP_200_OK)
async def read_all(user:user_dependency,db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Error")
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()

@router.get("/{todo_id}",status_code=status.HTTP_200_OK)
async def read_one( user:user_dependency,db: db_dependency,todo_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Error")
    todo_model = db.query(Todos).filter(Todos.id == todo_id and Todos.owner_id == user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404,detail="Todo not found")
    return todo_model

@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_one(user:user_dependency,db: db_dependency,todo_req :TodoRequest):
    try:
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication Error")
        todo_model = Todos(**todo_req.model_dump(),owner_id=user.get("id"))
        db.add(todo_model)
        db.commit()
        return
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.put("/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_one(user:user_dependency,db:db_dependency, todo_req: TodoRequest,todo_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Error")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id==user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    todo_model.title = todo_req.title
    todo_model.description = todo_req.description
    todo_model.priority = todo_req.priority
    todo_model.complete = todo_req.complete
    db.add(todo_model)
    db.commit()

@router.delete("/{todo_id}",status_code = status.HTTP_204_NO_CONTENT)
async def  delete_one(user:user_dependency,db:db_dependency,todo_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Error")
    todo_model = db.query(Todos).filter(Todos.id ==todo_id).filter(Todos.owner_id == user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()