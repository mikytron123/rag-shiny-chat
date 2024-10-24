FROM prom/prometheus:latest

COPY . .

CMD [ "--config.file=prometheus.yml", "--web.enable-remote-write-receiver"]