from datetime import datetime, timezone
from app.models.models import User
from app.schemas.user import UserResponse, UserCreate
from app.core.security import get_password_hash, verify_password

def test_user_model_and_password_security():
    hashed = get_password_hash("mysecretpassword")
    user = User(
        id=1,
        email="testuser@example.com",
        full_name="Test User",
        password_hash=hashed,
        is_active=True,
        role="user",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    assert user.password_hash != "mysecretpassword"
    assert verify_password("mysecretpassword", user.password_hash)
    assert not verify_password("wrongpassword", user.password_hash)

def test_user_response_pydantic_schema_excludes_password():
    user = User(
        id=10,
        email="john@example.com",
        full_name="John Doe",
        password_hash="secret_hashed_string",
        is_active=True,
        role="user",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    response_schema = UserResponse.model_validate(user)
    data_dict = response_schema.model_dump()

    assert "email" in data_dict
    assert "full_name" in data_dict
    assert "password" not in data_dict
    assert "password_hash" not in data_dict
    assert "hashed_password" not in data_dict
    assert data_dict["email"] == "john@example.com"
