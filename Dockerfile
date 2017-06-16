# https://github.com/moby/moby/pull/31352
# ARG FAISS_COMMIT
# FROM plippe/faiss:${FAISS_COMMIT}

FROM plippe/faiss:d3c8456

ENV PYTHONPATH=/opt/faiss

COPY requirements.txt /opt/faiss-web-service/requirements.txt

RUN pip install --upgrade pip && \
    pip install --requirement /opt/faiss-web-service/requirements.txt

COPY . /opt/faiss-web-service

# install sqlite3 for python
RUN echo "update 2017-06-16"
RUN apt-get update -y
RUN apt-get install libsqlite-dev -y

ENTRYPOINT /opt/faiss-web-service/bin/faiss_web_service.sh
