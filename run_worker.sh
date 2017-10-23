#!/usr/bin/env bash

celery worker -A app.celery_worker.celery -E \
    --without-gossip \
    --without-mingle \
    --without-heartbeat \
    --concurrency=3 \
    --autoscale=10,3 \
    --loglevel=INFO