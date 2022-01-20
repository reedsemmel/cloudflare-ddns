FROM docker.io/python:3.10-slim
WORKDIR /script
COPY requirements.txt .
RUN pip install --user -r requirements.txt
COPY update-record.py .
ENTRYPOINT ["/script/update-record.py"]
LABEL org.opencontainers.image.source https://github.com/reedsemmel/cloudflare-ddns
LABEL version=0.1.1
LABEL maintainer="Reed Semmel <reed@eperm.dev>"
