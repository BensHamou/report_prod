FROM python:3.9-alpine


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


WORKDIR /app

# Install postgres client
RUN apk  add --update  postgresql-client


# so th we could avoid installing extra packages to the container
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers \
    && apk add jpeg-dev zlib-dev libjpeg \
    && pip install Pillow

COPY requirements.txt .
RUN pip install  -r requirements.txt
# Remove dependencies
RUN apk del .tmp-build-deps

COPY . .