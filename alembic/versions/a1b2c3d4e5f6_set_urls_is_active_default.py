"""set urls is_active default for legacy data

Revision ID: a1b2c3d4e5f6
Revises: 94b0cb3b951f
Create Date: 2025-02-26

旧版数据迁移：将 is_active 为 NULL 的记录设为 1（启用），保证启用/禁用功能与旧数据兼容。
"""
from typing import Sequence, Union

from alembic import op


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "94b0cb3b951f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE zurl_urls SET is_active = 1 WHERE is_active IS NULL")


def downgrade() -> None:
    pass
