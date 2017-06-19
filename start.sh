git pull &&
docker build -t "linzuk/faiss-web-service:v2" . &&
docker run --rm -it -p 5000:5000 --name faiss-web-service linzuk/faiss-web-service:v2