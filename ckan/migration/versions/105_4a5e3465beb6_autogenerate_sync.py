"""autogenerate sync models with migrations

Revision ID: 4a5e3465beb6
Revises: 9f33a0280c51
Create Date: 2025-03-06 21:25:57.216365

"""
from alembic import op
from ckan import model
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '4a5e3465beb6'
down_revision = '9f33a0280c51'
branch_labels = None
depends_on = None


def _get_resource_pkg_fk_constraint_name(op) -> str:
    resource_table_name = model.resource_table.name
    resource_column_name = 'package_id'

    package_table_name = model.package_table.name
    package_column_name = 'id'

    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    fkeys = inspector.get_foreign_keys(resource_table_name)
    for fk in fkeys:
        if (
            fk['constrained_columns'] == [resource_column_name] and
            fk['referred_table'] == package_table_name and
            fk['referred_columns'] == [package_column_name]
        ):
            return fk['name']

    raise ValueError(
        'No foreign key constraint found for '
        '{0}.{1} -> {2}'.format(
            resource_table_name,
            resource_column_name,
            package_table_name
        )
    )


def upgrade():
    # removed feature
    op.drop_index('idx_rating_id', table_name='rating')
    op.drop_index('idx_rating_package_id', table_name='rating')
    op.drop_index('idx_rating_user_id', table_name='rating')
    op.drop_table('rating')
    # enforce package/resource relationship
    op.create_foreign_key('resource_package_id_fkey', 'resource',
                          'package', ['package_id'], ['id'])
    # long-forgotten columns
    op.drop_column('resource', 'webstore_last_updated')
    op.drop_column('resource', 'webstore_url')
    # redundant indexes
    op.drop_index('idx_package_group_group_id', table_name='member')
    op.drop_index('idx_package_group_pkg_id', table_name='member')
    op.drop_index('idx_package_group_pkg_id_group_id', table_name='member')
    op.drop_index('idx_pkg_id', table_name='package')
    op.drop_index('idx_pkg_name', table_name='package')
    op.drop_index('idx_pkg_title', table_name='package')
    op.drop_index('idx_package_tag_tag_id', table_name='package_tag')
    op.drop_index('term', table_name='term_translation')


def downgrade():
    op.create_index('term', 'term_translation', ['term'], unique=False)
    op.create_index('idx_package_tag_tag_id', 'package_tag', ['tag_id'],
                    unique=False)
    op.create_index('idx_pkg_title', 'package', ['title'], unique=False)
    op.create_index('idx_pkg_name', 'package', ['name'], unique=False)
    op.create_index('idx_pkg_id', 'package', ['id'], unique=False)
    op.create_index('idx_package_group_pkg_id_group_id', 'member',
                    ['group_id', 'table_id'], unique=False)
    op.create_index('idx_package_group_pkg_id', 'member', ['table_id'],
                    unique=False)
    op.create_index('idx_package_group_group_id', 'member', ['group_id'],
                    unique=False)
    op.add_column('resource', sa.Column('webstore_url', sa.TEXT(),
                  autoincrement=False, nullable=True))
    op.add_column('resource', sa.Column('webstore_last_updated',
                  postgresql.TIMESTAMP(), autoincrement=False,
                  nullable=True))
    op.drop_constraint(_get_resource_pkg_fk_constraint_name(op),
                       'resource', type_='foreignkey')
    op.create_table(
        'rating',
        sa.Column('id', sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column('user_id', sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column('user_ip_address', sa.TEXT(), autoincrement=False,
                  nullable=True),
        sa.Column('rating', postgresql.DOUBLE_PRECISION(precision=53),
                  autoincrement=False, nullable=True),
        sa.Column('created', postgresql.TIMESTAMP(), autoincrement=False,
                  nullable=True),
        sa.Column('package_id', sa.TEXT(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['package_id'], ['package.id'],
                                name='rating_package_id_fkey'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'],
                                name='rating_user_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='rating_pkey')
    )
    op.create_index('idx_rating_user_id', 'rating', ['user_id'], unique=False)
    op.create_index('idx_rating_package_id', 'rating', ['package_id'],
                    unique=False)
    op.create_index('idx_rating_id', 'rating', ['id'], unique=False)
