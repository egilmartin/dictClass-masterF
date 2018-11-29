# DictClass
description here


## Deploy a model using dockers
- Step 1: Upload the code to DockerHub by running docker.sh
- Step 2: SSH to the server, pull and run the new image.

The server will be executing *wsgi.py* which hosts a flask server using gunicorn with 2 workers (can be more).
