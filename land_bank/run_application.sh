#!/bin/bash

#alembic revision --autogenerate -m 'initial'
alembic upgrade aba570fb9950

gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000