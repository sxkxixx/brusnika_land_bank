#!/bin/bash

cd ~/land_bank

alembic revision --autogenerate
alembic upgrade head