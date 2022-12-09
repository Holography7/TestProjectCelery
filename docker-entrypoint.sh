#!/bin/sh

uvicorn main:app --reload --host $HOST --port $PORT --use-colors
