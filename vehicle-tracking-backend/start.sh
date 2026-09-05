#!/bin/bash
set -e

# Start FastAPI Uvicorn Server in background
echo "Starting FastAPI Uvicorn server on port ${PORT:-8000}..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} &
UVICORN_PID=$!

# Wait briefly for FastAPI server to initialize
sleep 3

# Start GPS Simulator targeting local REST API
if [ "${ENABLE_SIMULATOR:-true}" = "true" ]; then
    echo "Starting background GPS Telemetry Simulator..."
    export REST_API_URL="http://127.0.0.1:${PORT:-8000}/api/v1/gps"
    python simulator/gps_simulator.py &
fi

# Wait for main uvicorn process
wait $UVICORN_PID
