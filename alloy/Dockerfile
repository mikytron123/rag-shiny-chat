FROM grafana/alloy:latest

COPY . .

CMD ["run","--server.http.listen-addr=0.0.0.0:12345","--storage.path=/var/lib/alloy/data","--stability.level=experimental","config.alloy"]