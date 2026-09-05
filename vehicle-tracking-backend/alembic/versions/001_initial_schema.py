"""initial domain schema migration

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-05 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. bus_routes table
    op.create_table(
        'bus_routes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('route_code', sa.String(length=100), nullable=False),
        sa.Column('route_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_location', sa.String(length=255), nullable=False),
        sa.Column('end_location', sa.String(length=255), nullable=False),
        sa.Column('waypoints_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bus_routes_id'), 'bus_routes', ['id'], unique=False)
    op.create_index(op.f('ix_bus_routes_route_code'), 'bus_routes', ['route_code'], unique=True)

    # 2. route_points table
    op.create_table(
        'route_points',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('route_id', sa.Integer(), nullable=False),
        sa.Column('sequence', sa.Integer(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['route_id'], ['bus_routes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_route_points_id'), 'route_points', ['id'], unique=False)
    op.create_index(op.f('ix_route_points_route_id'), 'route_points', ['route_id'], unique=False)

    # 3. vehicles table
    op.create_table(
        'vehicles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vehicle_code', sa.String(length=100), nullable=False),
        sa.Column('license_plate', sa.String(length=100), nullable=False),
        sa.Column('model_name', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('assigned_route_id', sa.Integer(), nullable=True),
        sa.Column('last_latitude', sa.Float(), nullable=True),
        sa.Column('last_longitude', sa.Float(), nullable=True),
        sa.Column('last_speed', sa.Float(), nullable=True),
        sa.Column('last_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['assigned_route_id'], ['bus_routes.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vehicles_id'), 'vehicles', ['id'], unique=False)
    op.create_index(op.f('ix_vehicles_vehicle_code'), 'vehicles', ['vehicle_code'], unique=True)

    # 4. users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=True),
        sa.Column('assigned_route_id', sa.Integer(), nullable=True),
        sa.Column('assigned_vehicle_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['assigned_route_id'], ['bus_routes.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['assigned_vehicle_id'], ['vehicles.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # 5. user_assignments table
    op.create_table(
        'user_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('route_id', sa.Integer(), nullable=False),
        sa.Column('vehicle_id', sa.Integer(), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['route_id'], ['bus_routes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_assignments_id'), 'user_assignments', ['id'], unique=False)
    op.create_index(op.f('ix_user_assignments_is_active'), 'user_assignments', ['is_active'], unique=False)
    op.create_index(op.f('ix_user_assignments_user_id'), 'user_assignments', ['user_id'], unique=False)
    op.create_index('idx_user_active_assignment', 'user_assignments', ['user_id', 'is_active'], unique=False)

    # 6. gps_telemetry table
    op.create_table(
        'gps_telemetry',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vehicle_id', sa.Integer(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('speed', sa.Float(), nullable=True),
        sa.Column('heading', sa.Float(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_gps_telemetry_id'), 'gps_telemetry', ['id'], unique=False)
    op.create_index(op.f('ix_gps_telemetry_recorded_at'), 'gps_telemetry', ['recorded_at'], unique=False)
    op.create_index(op.f('ix_gps_telemetry_vehicle_id'), 'gps_telemetry', ['vehicle_id'], unique=False)
    op.create_index('idx_vehicle_history', 'gps_telemetry', ['vehicle_id', 'recorded_at'], unique=False)

def downgrade() -> None:
    op.drop_index('idx_vehicle_history', table_name='gps_telemetry')
    op.drop_index(op.f('ix_gps_telemetry_vehicle_id'), table_name='gps_telemetry')
    op.drop_index(op.f('ix_gps_telemetry_recorded_at'), table_name='gps_telemetry')
    op.drop_index(op.f('ix_gps_telemetry_id'), table_name='gps_telemetry')
    op.drop_table('gps_telemetry')

    op.drop_index('idx_user_active_assignment', table_name='user_assignments')
    op.drop_index(op.f('ix_user_assignments_user_id'), table_name='user_assignments')
    op.drop_index(op.f('ix_user_assignments_is_active'), table_name='user_assignments')
    op.drop_index(op.f('ix_user_assignments_id'), table_name='user_assignments')
    op.drop_table('user_assignments')

    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

    op.drop_index(op.f('ix_vehicles_vehicle_code'), table_name='vehicles')
    op.drop_index(op.f('ix_vehicles_id'), table_name='vehicles')
    op.drop_table('vehicles')

    op.drop_index(op.f('ix_route_points_route_id'), table_name='route_points')
    op.drop_index(op.f('ix_route_points_id'), table_name='route_points')
    op.drop_table('route_points')

    op.drop_index(op.f('ix_bus_routes_route_code'), table_name='bus_routes')
    op.drop_index(op.f('ix_bus_routes_id'), table_name='bus_routes')
    op.drop_table('bus_routes')
