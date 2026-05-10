from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, require_admin
from common_lib.infrastructure.db.session import get_db
from common_lib.utils.jwt_utils import CurrentUser
from data.repositories.implemetations.category_repository import CategoryRepository
from domain.models.db.category import Category
from domain.models.schemas.category import CreateCategoryDto, ReadCategoryDto, UpdateCategoryDto

router = APIRouter(tags=["categories"])


def get_repo(session: AsyncSession = Depends(get_db)):
    return CategoryRepository(session)


@router.get("/", response_model=List[ReadCategoryDto])
async def get_categories(
    user: CurrentUser = Depends(get_current_user),
    repo: CategoryRepository = Depends(get_repo),
):
    categories = await repo.get_all()
    return [ReadCategoryDto.model_validate(c) for c in categories]


@router.post("/", response_model=ReadCategoryDto, status_code=201)
async def create_category(
    dto: CreateCategoryDto,
    user: CurrentUser = Depends(require_admin),
    repo: CategoryRepository = Depends(get_repo),
):
    category = Category(name=dto.name, description=dto.description)
    category = await repo.create(category)
    return ReadCategoryDto.model_validate(category)


@router.put("/{category_id}", response_model=ReadCategoryDto)
async def update_category(
    category_id: UUID,
    dto: UpdateCategoryDto,
    user: CurrentUser = Depends(require_admin),
    repo: CategoryRepository = Depends(get_repo),
):
    category = await repo.get(category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    if dto.name is not None:
        category.name = dto.name
    if dto.description is not None:
        category.description = dto.description

    category = await repo.update(category)
    return ReadCategoryDto.model_validate(category)


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: UUID,
    user: CurrentUser = Depends(require_admin),
    repo: CategoryRepository = Depends(get_repo),
):
    category = await repo.get(category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    await repo.delete(category)
