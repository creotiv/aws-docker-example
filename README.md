# Install Docker    
    sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo apt-key fingerprint 0EBFCD88
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    sudo apt-get update
    sudo apt-get install docker-ce docker-ce-cli containerd.io
    sudo usermod -a -G docker $USER
    sudo chmod 0777 /var/run/docker.sock

# Dev Process
## Build image
    docker build -t skyworker-app app
    docker build -t skyworker-nginx nginx 

## Run all services on local machine
Updated code will be automatically reloaded by the gunicorn.
Migrations and collectstatic should be run manually (or just restart compose)

    docker-compose up
    # as a daemon
    docker-compose up -d 

## Exec operation
    docker container ls
    docker-compose exec app_web_1 python manage.py migrate --noinput
    docker-compose exec -it app_web_1 /bin/sh
    
# Deploy
    pip install fabric2
    fab2 -l
    fab2 install-instance

* install-instance - setting up new ubuntu instance
* set-pass - setting default pass for Django (it should be set in install-instance, but not always)
* deploy - deploying updates from gitlab to the server with rebuilding images
* pgdump - dumping db to the local machine
    


# Questions about deploy -> ping me
https://www.facebook.com/anikishaev