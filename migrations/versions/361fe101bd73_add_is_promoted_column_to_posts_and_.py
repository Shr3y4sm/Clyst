"""Add is_promoted column to posts and products tables

Revision ID: 361fe101bd73
Revises: 
Create Date: 2025-10-10 16:20:57.428941

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '361fe101bd73'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Use raw SQL for SQLite-safe column add without temp tables
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == 'sqlite':
        # Add columns as nullable first
        op.execute("ALTER TABLE posts ADD COLUMN is_promoted BOOLEAN")
        op.execute("ALTER TABLE products ADD COLUMN is_promoted BOOLEAN")
        # Backfill NULLs to 0/False
        op.execute("UPDATE posts SET is_promoted = 0 WHERE is_promoted IS NULL")
        op.execute("UPDATE products SET is_promoted = 0 WHERE is_promoted IS NULL")
        # Note: SQLite can't easily add NOT NULL after; we keep it nullable at DB level
    else:
        with op.batch_alter_table('posts') as batch_op:
            batch_op.add_column(sa.Column('is_promoted', sa.Boolean(), nullable=True))
        with op.batch_alter_table('products') as batch_op:
            batch_op.add_column(sa.Column('is_promoted', sa.Boolean(), nullable=True))


def downgrade():
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    if dialect_name == 'sqlite':
        # SQLite cannot drop columns easily; perform no-op downgrade
        pass
    else:
        with op.batch_alter_table('products') as batch_op:
            batch_op.drop_column('is_promoted')
        with op.batch_alter_table('posts') as batch_op:
            batch_op.drop_column('is_promoted')
