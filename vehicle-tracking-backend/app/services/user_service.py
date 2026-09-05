from typing import List
from sqlalchemy.orm import Session

from app.models.models import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse

class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        users = self.user_repo.get_all(skip=skip, limit=limit)
        return [UserResponse.model_validate(u) for u in users]

    def get_user_by_id(self, user_id: int) -> UserResponse:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            from app.exceptions.custom_exceptions import EntityNotFoundException
            raise EntityNotFoundException("User", user_id)
        return UserResponse.model_validate(user)
