"""empty message

Revision ID: 330dab72564a
Revises: 
Create Date: 2024-03-26 15:58:35.140468

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '330dab72564a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('teams')
    op.drop_table('leagues')
    with op.batch_alter_table('payouts', schema=None) as batch_op:
        batch_op.alter_column('pool',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)
        batch_op.alter_column('amount',
               existing_type=sa.NUMERIC(),
               type_=sa.Float(),
               existing_nullable=True,
               existing_server_default=sa.text("'0'::double precision"))
        batch_op.alter_column('week',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=False)
        batch_op.alter_column('venmo_id',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('roles', sa.String(), nullable=True))
        batch_op.alter_column('username',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)
        batch_op.alter_column('venmo_id',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('name',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               nullable=False)
        batch_op.alter_column('user_id',
               existing_type=sa.VARCHAR(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.drop_constraint('users_venmo_id_key', type_='unique')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_unique_constraint('users_venmo_id_key', ['venmo_id'])
        batch_op.alter_column('user_id',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.alter_column('name',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               nullable=True)
        batch_op.alter_column('venmo_id',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('username',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)
        batch_op.drop_column('roles')

    with op.batch_alter_table('payouts', schema=None) as batch_op:
        batch_op.alter_column('venmo_id',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)
        batch_op.alter_column('week',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=False)
        batch_op.alter_column('amount',
               existing_type=sa.Float(),
               type_=sa.NUMERIC(),
               existing_nullable=True,
               existing_server_default=sa.text("'0'::double precision"))
        batch_op.alter_column('pool',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)

    op.create_table('leagues',
    sa.Column('league_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('site', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('season', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.CheckConstraint("site::text = ANY (ARRAY['yahoo'::character varying, 'sleeper'::character varying]::text[])", name='leagues_check'),
    sa.PrimaryKeyConstraint('league_id', name='leagues_pk'),
    postgresql_ignore_search_path=False
    )
    op.create_table('teams',
    sa.Column('team_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('league_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['league_id'], ['leagues.league_id'], name='teams_leagues_fk'),
    sa.PrimaryKeyConstraint('league_id', 'team_name', name='teams_pk')
    )
    # ### end Alembic commands ###
