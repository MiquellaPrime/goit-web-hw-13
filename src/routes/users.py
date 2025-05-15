import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, UploadFile

from src.dependency import user_dependency, db_dependency
from src.repository import users as user_repository
from src.schemas.users import UserSchema
from src.settings import settings

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: user_dependency):
    return current_user


@router.patch("/avatar", response_model=UserSchema)
async def update_user_avatar(
        file: UploadFile,
        current_user: user_dependency,
        db: db_dependency,
):
    cloudinary.config(
        cloud_name=settings.cloudinary.name,
        api_key=settings.cloudinary.api_key,
        api_secret=settings.cloudinary.api_secret,
        secure=True,
    )
    cloudinary.uploader.upload(
        file.file, public_id=f"AddressBookApp/user/{current_user.id}", overwrite=True,
    )
    src_url = cloudinary.CloudinaryImage(f"AddressBookApp/user/{current_user.id}").build_url(
        width=250, height=250, crop="fill",
    )
    user_model = await user_repository.update_avatar(db, current_user.email, src_url)
    return user_model
