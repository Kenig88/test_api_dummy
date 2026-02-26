FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apk add --no-cache \
    tzdata \
    ca-certificates \
    bash \
 && update-ca-certificates

WORKDIR /usr/workspace

COPY requirements.txt /usr/workspace/requirements.txt

RUN python -m pip install --no-cache-dir --upgrade pip \
 && python -m pip install --no-cache-dir -r /usr/workspace/requirements.txt

COPY . /usr/workspace

CMD ["pytest"]