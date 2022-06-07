FROM python:3.8.8

RUN pip install web3

WORKDIR /app

ADD abi abi

COPY parse_tavern.py parse_tavern.py
COPY decoder.py decoder.py
COPY abi_parser.py abi_parser.py
COPY utils.py utils.py
COPY variables.py variables.py

ENTRYPOINT [ "python", "-u", "parse_tavern.py" ]
