#!/bin/bash
cd /opt/render/project/src
exec gunicorn --bind 0.0.0.0:$PORT config.wsgi:application 