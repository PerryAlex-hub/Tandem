"""create document snapshots table

Revision ID: edaca1567be4
Revises: 8cacd5bf6562
Create Date: 2026-10-18 21:32:31.598212

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'edaca1567be4'
down_revision: Union[str, None] = '8cacd5bf6562'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('document_snapshots',
    sa.Column('room_code', sa.String(length=8), nullable=False),
    sa.Column('doc_type', sa.String(length=20), nullable=False),
    sa.Column('data', sa.LargeBinary(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('room_code', 'doc_type')
    )


def downgrade() -> None:
    op.drop_table('document_snapshots')
