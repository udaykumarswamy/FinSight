#!/bin/bash
# Start the FinSight Web UI

echo "Starting FinSight Web UI..."
echo "The UI will be available at http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Check if running with uv
if command -v uv &> /dev/null; then
    uv run python -m finsight.web
else
    python -m finsight.web
fi

