from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from app.database import SessionDep
from app.models import *
from app.auth import encrypt_password, verify_password, create_access_token, AuthDep
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import status

todo_router = APIRouter(tags=["Todo Management"])


@todo_router.get('/todos', response_model=list[TodoResponse])
def get_todos(db:SessionDep, user:AuthDep):
    return user.todos

@todo_router.get('/todo/{id}', response_model=TodoResponse)
def get_todo_by_id(id:int, db:SessionDep, user:AuthDep):
    todo = db.exec(select(Todo).where(Todo.id==id, Todo.user_id==user.id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return todo

@todo_router.post('/todos', response_model=TodoResponse)
def create_todo(db:SessionDep, user:AuthDep, todo_data:TodoCreate):
    todo = Todo(text=todo_data.text, user_id=user.id)
    try:
        db.add(todo)
        db.commit()
        db.refresh(todo)
        return todo
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while creating an item",
        )

@todo_router.put('/todo/{id}', response_model=TodoResponse)
def update_todo(id:int, db:SessionDep, user:AuthDep, todo_data:TodoUpdate):
    todo = db.exec(select(Todo).where(Todo.id==id, Todo.user_id==user.id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    if todo_data.text:
        todo.text = todo_data.text
    if todo_data.done:
        todo.done = todo_data.done
    try:
        db.add(todo)
        db.commit()
        return todo
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while updating an item",
        )

@todo_router.delete('/todo/{id}', status_code=status.HTTP_200_OK)
def update_todo(id:int, db:SessionDep, user:AuthDep):

    todo = db.exec(select(Todo).where(Todo.id==id, Todo.user_id==user.id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    try:
        db.delete(todo)
        db.commit()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while deleting an item",
        )

##EXERCISES:
##Allows users to create a new category-POST 
@todo_router.post('/category', status_code=status.HTTP_201_CREATED)
def create_category(category:Category, db:SessionDep, user:AuthDep):
    new_category=Category(text=category.text, user_id=user.id)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

##Add category to todo.categories, given a todo and category-POST
@todo_router.post("/todo/{todo_id}/category/{category_id}", status_code=status.HTTP_200_OK)
def add_category_to_todo(todo_id: int, category_id: int, db:SessionDep, user: AuthDep):
    todo=db.exec(select(Todo).where(Todo.id==todo_id)).one_or_none()
    if not todo:
        print("Todo not found")
    category=db.exec(select(Category).where(Category.id==category_id)).one_or_none()
    if not category:
        print("Category not found")


    #check if category is already in todo
    if category in todo.categories:
        return {
            "message": "Category already assigned to this todo."
        }
    todo.categories.append(category)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return{"message": "Category was successfully added to Todo"}

##Delete a todo from a todo.categories-DELETE
@todo_router.delete("/todo/{todo_id}/category/{category_id}", status_code=status.HTTP_200_OK)
def remove_category_to_todo(todo_id: int, category_id: int, db:SessionDep, user: AuthDep):
    todo=db.exec(select(Todo).where(Todo.id==todo_id)).one_or_none()
    if not todo:
        print("Todo not found")
    category=db.exec(select(Category).where(Category.id==category_id)).one_or_none()
    if not category:
        print("Category not found")


    #check if category is already in todo
    if category not in todo.categories:
        return {
            "message": "Category not in this todo."
        }
    todo.categories.remove(category)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return{"message": "Category was successfully removed to Todo"}


##get todos for category-GET
@todo_router.get("/category/{category_id}/todos", status_code=status.HTTP_200_OK)
def get_todos_from_category(category_id: int, db:SessionDep, user: AuthDep):
    category=db.exec(select(Category).where(Category.id==category_id)).one_or_none()
    if not category:
        print("Category does not exist")
    todos=category.todos
    return todos
  