from sqlalchemy.orm import Session
from app.models import ImageTask
from datetime import datetime

def create_image_task(db: Session, task_id: str, img_link: str, user_id: str) -> ImageTask:
    """
    Создать новую задачу для изображения
    """
    db_task = ImageTask(
        task_id=task_id,
        img_link=img_link,
        user_id=user_id,
        created_at=datetime.now(),
        status=False
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_image_task(db: Session, task_id: str) -> ImageTask:
    """
    Получить задачу по ID
    """
    return db.query(ImageTask).filter(ImageTask.task_id == task_id).first()

def get_image_tasks_by_user(db: Session, user_id: str) -> ImageTask:
    """
    Получить все задачи пользователя
    """
    return db.query(ImageTask).filter(ImageTask.user_id == user_id).all()

def update_image_task_status(db: Session, task_id: str, status: bool) -> ImageTask:
    """
    Обновляет статус задачи в базе данных
    """
    task = db.query(ImageTask).filter(ImageTask.task_id == task_id).first()
    if not task:
        raise ValueError(f"Задача {task_id} не найдена.")
    
    task.status = status
    db.commit()
    db.refresh(task)
    return task