"""SQLAlchemy ORM models.

Import all models here so Alembic can discover them via ``Base.metadata``.
"""

from app.database import Base

from app.models.user import User, Role, Permission, user_roles, role_permissions
from app.models.data_source import DataSource
from app.models.sync_job import SyncJob, SyncJobRun
from app.models.data_mapping import FieldMapping
from app.models.raw_record import RawApiRecord
from app.models.dashboard import Dashboard, DashboardWidget
from app.models.component import CustomComponent, CustomComponentVersion
from app.models.audit_log import AuditLog

__all__ = [
    "Base",
    "User", "Role", "Permission", "user_roles", "role_permissions",
    "DataSource",
    "SyncJob", "SyncJobRun",
    "FieldMapping",
    "RawApiRecord",
    "Dashboard", "DashboardWidget",
    "CustomComponent", "CustomComponentVersion",
    "AuditLog",
]
