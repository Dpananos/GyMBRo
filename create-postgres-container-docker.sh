docker run \
  --name postgres-db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USERNAME=postgres \
  -d \
  -v ${PWD}/postgres-docker:/var/lib/postgresql/data \
  -p 5432:5432 postgres 
