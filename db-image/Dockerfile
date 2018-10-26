FROM python:3.6-alpine3.6
RUN apk add --no-cache util-linux

ADD download-db.py /usr/local/bin/download-db.py

CMD /usr/local/bin/download-db.py
