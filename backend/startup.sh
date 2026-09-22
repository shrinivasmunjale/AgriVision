#!/bin/bash
set -e

# Run evidence seed script to ensure database has all latest records
python seed_evidence.py || echo "Warning: Seed script completed or skipped"

# Start application server
gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app
