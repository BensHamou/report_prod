docker rmi -f puma_prod
docker-compose down
docker-compose build --no-cache
docker-compose up -d