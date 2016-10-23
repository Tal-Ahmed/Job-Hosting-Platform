#!/usr/bin/env bash

sudo echo

ENV=$1

configure_virtualenv(){
    if [ ! -d "$HOME/.virtualenv" ]; then
        mkdir -p $HOME/.virtualenv
    fi

    virtualenv $HOME/.virtualenv/Nomad
}

configure_nginx(){
    sudo killall nginx 2>/dev/null

    sudo rm -f /etc/nginx/sites-enabled/default
    sudo rm -f /etc/nginx/sites-available/default
    sudo rm -f /etc/nginx/sites-enabled/nomad
    sudo rm -f /etc/nginx/sites-available/nomad

    sudo cp ./server_setup/etc/nginx/sites-available/nomad /etc/nginx/sites-available/nomad
    sudo ln -sfnv /etc/nginx/sites-available/nomad /etc/nginx/sites-enabled/nomad
}

configure_mongodb(){
    sudo killall mongod 2>/dev/null
    sudo rm -f /etc/mongod.conf

    sudo addgroup --quiet mongod 2>/dev/null
    sudo adduser --quiet --system --no-create-home --ingroup redis --disabled-login --disabled-password mongod

    sudo rm -f /etc/systemd/system/mongod.service
    sudo rm -f /lib/systemd/system/mongod.service

    case "$ENV" in
        dev)
            sudo cp ./config/mongodb_dev.conf /etc/mongod.conf
            ;;
        prod)
            sudo mkdir -p /home/Nomad/logs/mongo/
            sudo mkdir -p /home/Nomad/data/mongo/

            sudo cp ./config/mongodb_prod.conf /etc/mongod.conf
            ;;
    esac

    sudo cp ./server_setup/etc/systemd/system/mongod.service /etc/systemd/system/mongod.service

    sudo chmod 755 /etc/systemd/system/mongod.service
}

configure_redis(){
    sudo killall redis 2>/dev/null
    sudo killall redis-server 2>/dev/null

    sudo rm -f /etc/redis/redis.conf
    sudo rm -f /etc/redis/redis-server.conf
    sudo rm -f /etc/init.d/redis-server
    sudo rm -f /etc/systemd/system/redis-server.service
    sudo rm -f /lib/systemd/system/redis-server.service

    sudo mkdir -p /etc/redis/
    sudo mkdir -p /var/log/redis/
    sudo mkdir -p /var/run/redis/

    sudo addgroup --quiet redis 2>/dev/null
    sudo adduser --quiet --system --no-create-home --ingroup redis --disabled-login --disabled-password redis

    sudo chown -R redis:redis /var/log/redis
    sudo chown -R redis:redis /etc/redis
    sudo chown -R redis:redis /var/run/redis

    case "$ENV" in
    dev)
        sudo cp ./config/redis_dev.conf /etc/redis/redis.conf
        ;;
    prod)
        sudo cp ./config/redis_prod.conf /etc/redis/redis.conf
        ;;
    esac

    sudo cp ./server_setup/etc/systemd/system/redis-server.service /etc/systemd/system/redis-server.service
}

configure_uwsgi(){
    sudo rm -f /tmp/uwsgi.ini
    sudo rm -f /etc/systemd/system/nomad.service

    sudo cp ./config/uwsgi.ini /tmp/uwsgi.ini

    sudo touch /etc/systemd/system/nomad.service
    sudo /bin/sh -c "sed \"/\[Service\]/a User=$USER\" ./server_setup/etc/systemd/system/nomad.service > /etc/systemd/system/nomad.service"

    sudo chmod 755 /etc/systemd/system/nomad.service
}

echo "Configuring Virtualenv"
configure_virtualenv

echo "Configuring Nginx"
configure_nginx

echo "Configuring MongoDB"
configure_mongodb

echo "Configuring Redis"
configure_redis

echo "Configuring uWSGI"
configure_uwsgi

sudo systemctl daemon-reload

echo "Starting Nginx"
sudo systemctl start nginx

echo "Starting MongoDB"
sudo systemctl start mongod

echo "Starting Redis"
sudo systemctl start redis-server

echo "Starting Virtualenv"
source $HOME/.virtualenv/Nomad/bin/activate

echo "Installing Python dependencies"
pip install -r requirements.txt

echo "Installing NPM dependencies"
npm install

echo "Starting Nomad"
sudo systemctl start nomad