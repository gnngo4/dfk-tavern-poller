FROM python:3.8.8

RUN pip install argparse requests

WORKDIR /app
COPY query.py query.py
COPY utils.py utils.py
COPY variables.py variables.py

ENTRYPOINT [ "python", "query.py" ]
