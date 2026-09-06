#!/bin/bash
set -e

# Start FastAPI Uvicorn Server in background
echo "Starting FastAPI Uvicorn server on port ${PORT:-8000}..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} &
UVICORN_PID=$!

# Wait for FastAPI server startup and DB initialization
echo "Waiting for API server startup and database seeding..."
sleep 3
for i in $(seq 1 15); do
  if curl -s http://127.0.0.1:${PORT:-8000}/health | grep -q "healthy"; then
    echo "API server is ready and healthy."
    break
  fi
  sleep 2
done

# Start GPS Simulator targeting local REST API
if [ "${ENABLE_SIMULATOR:-true}" = "true" ]; then
    echo "Starting background GPS Telemetry Simulator..."
    export REST_API_URL="http://127.0.0.1:${PORT:-8000}/api/v1/gps"
    export VEHICLE_CODES="${VEHICLE_CODES:-BUS-001,BUS-002}"
    python simulator/gps_simulator.py &
fi

# Wait for main uvicorn process
wait $UVICORN_PID
