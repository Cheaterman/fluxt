FROM cheaterman/flask
COPY . /code
RUN su uwsgi -c 'pip install --no-cache-dir -U -r /code/requirements.txt'
