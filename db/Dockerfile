FROM "postgis/postgis:16-3.4"

RUN <<EOF
apt-get update
apt-get install -y wget postgis unzip
mkdir -p /gisdata
chown postgres:postgres /gisdata
EOF