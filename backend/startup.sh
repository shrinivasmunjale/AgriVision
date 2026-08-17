#!/bin/bash
if [ -d "/home/site/wwwroot/.venv" ]; then
    source /home/site/wwwroot/.venv/bin/activate
elif [ -d "antenv" ]; then
    source antenv/bin/activate
fi

gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app
