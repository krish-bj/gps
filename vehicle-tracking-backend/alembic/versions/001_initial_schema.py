"""initial schema

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
        sa.Column('route_code', sa.String(100), nullable=False),
        sa.Column('route_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_location', sa.String(255), nullable=False),
        sa.Column('end_location', sa.String(255), nullable=False),
        sa.Column('waypoints_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bus_routes_id'), 'bus_routes', ['id'], unique=False)
    op.create_index(op.f('ix_bus_routes_route_code'), 'bus_routes', ['route_code'], unique=True)

    # 2. vehicles table
    op.create_table(
        'vehicles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vehicle_code', sa.String(100), nullable=False),
        sa.Column('license_plate', sa.String(100), nullable=False),
        sa.Column('model_name', sa.String(255), nullable=True),
        sa.Column('status', sa.String(50), nullable=True),
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

    # 3. users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('role', sa.String(50), nullable=True),
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

    # 4. gps_telemetry table
    op.create_table(
        'gps_telemetry',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vehicle_id', sa.Integer(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('speed_kmh', sa.Float(), nullable=True),
        sa.Column('heading', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_gps_telemetry_id'), 'gps_telemetry', ['id'], unique=False)
    op.create_index(op.f('ix_gps_telemetry_timestamp'), 'gps_telemetry', ['timestamp'], unique=False)
    op.create_index(op.f('ix_gps_telemetry_vehicle_id'), 'gps_telemetry', ['vehicle_id'], unique=False)

def downgrade() -> None:
    op.drop_table('gps_telemetry')
    op.drop_table('users')
    op.drop_table('vehicles')
    op.drop_table('bus_routes')
