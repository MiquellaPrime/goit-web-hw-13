from typing import Annotated

from fastapi import Depends
from redis import Redis
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import UserORM
from src.database.redis import get_redis
from src.services.auth import get_current_user

db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[UserORM, Depends(get_current_user)]

redis_dependency = Annotated[Redis, Depends(get_redis)]
