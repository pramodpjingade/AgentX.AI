from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel

from database.connection import get_db
from database.models import PluginVersion
from authentication.jwt_handler import get_current_user
from database.models import User

router = APIRouter()

# Schema validations
class PluginInstallSchema(BaseModel):
    plugin_name: str
    version: str
    dependencies: Optional[List[str]] = []
    min_agentx_version: Optional[str] = "1.0.0"
    package_url: Optional[str] = None

class PluginResponseSchema(BaseModel):
    id: UUID
    plugin_name: str
    version: str
    dependencies: List[str]
    min_agentx_version: Optional[str]
    package_url: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True

@router.post("/", response_model=PluginResponseSchema, status_code=status.HTTP_201_CREATED)
async def install_plugin(
    payload: PluginInstallSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Installs or registers a new plugin in the marketplace registry."""
    # Ensure current user is developer or admin
    if current_user.role not in ["admin", "developer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Only admins or developers can install plugins."
        )

    # Check if this specific version is already registered
    stmt = select(PluginVersion).where(
        PluginVersion.plugin_name == payload.plugin_name,
        PluginVersion.version == payload.version
    )
    result = await db.execute(stmt)
    existing_plugin = result.scalars().first()

    if existing_plugin:
        if existing_plugin.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Plugin '{payload.plugin_name}' version {payload.version} is already installed."
            )
        else:
            # Reactivate previously disabled plugin
            existing_plugin.is_active = True
            await db.commit()
            await db.refresh(existing_plugin)
            return existing_plugin

    # Create new plugin registry record
    new_plugin = PluginVersion(
        plugin_name=payload.plugin_name,
        version=payload.version,
        dependencies=payload.dependencies,
        min_agentx_version=payload.min_agentx_version,
        package_url=payload.package_url,
        is_active=True
    )
    
    db.add(new_plugin)
    await db.commit()
    await db.refresh(new_plugin)
    return new_plugin

@router.delete("/{plugin_name}", status_code=status.HTTP_200_OK)
async def uninstall_plugin(
    plugin_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Disables/uninstalls a registered plugin by setting its state to inactive."""
    if current_user.role not in ["admin", "developer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Only admins or developers can uninstall plugins."
        )

    stmt = select(PluginVersion).where(
        PluginVersion.plugin_name == plugin_name,
        PluginVersion.is_active == True
    )
    result = await db.execute(stmt)
    plugins = result.scalars().all()

    if not plugins:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active plugin found with name '{plugin_name}'"
        )

    # Disable all active version entries for this plugin
    for plugin in plugins:
        plugin.is_active = False
        
    await db.commit()
    return {"message": f"Plugin '{plugin_name}' uninstalled successfully from the registry."}

@router.get("/", response_model=List[PluginResponseSchema])
async def list_plugins(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists all active plugins in the marketplace registry."""
    stmt = select(PluginVersion).where(PluginVersion.is_active == True)
    result = await db.execute(stmt)
    return list(result.scalars().all())
