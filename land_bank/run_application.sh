#!/bin/bash

alembic revision --autogenerate -m 'initial'
alembic upgrade 07ee6db86693

gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:80