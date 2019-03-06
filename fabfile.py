from fabric2 import task, Connection
from fabric2.transfer import Transfer
import time
import getpass


HOST = 'ec2-13-53-129-145.eu-north-1.compute.amazonaws.com'
KEY_FILE = '../aws-sk.pem'
DEFAULT_LOGIN = 'demo@demo.com'
DEFAULT_PASS = 'demo'
DEFAULT_USER = 'demo'

host = Connection(host=HOST, 
                  user='ubuntu', 
                  port=22, 
                  connect_kwargs={"key_filename":[KEY_FILE]})

@task
def install_instance(c):
    if True or host.sudo('service docker status', hide='out', warn=True).failed:
        print('Docker not found. Installing it.')
        host.sudo('apt-get update')
        host.sudo('apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common')
        host.sudo('curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -')
        host.sudo('apt-key fingerprint 0EBFCD88')
        host.sudo('add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"')
        host.sudo('apt-get update')
        host.sudo('apt-get install -y docker-ce docker-ce-cli containerd.io')
        host.sudo('usermod -a -G docker $USER')
        host.sudo('docker swarm init')
        print('### KEY ######################################################################')
        host.run('ssh-keygen -t rsa -C "demo@demo.com" -f ~/.ssh/id_rsa -q -N ""')
        host.run('cat ~/.ssh/id_rsa.pub')
        print('### KEY ######################################################################')
        res = 't'
        while res.lower():
            res = getpass.getpass('Update you github account and hit enter.')
        host.run('ssh-keyscan github.com >> ~/.ssh/known_hosts')
        host.run('mkdir awsdemo')
        with host.cd('awsdemo'):
            host.run('git clone https://github.com/creotiv/aws-docker-example.git .')
            host.run('git checkout master')
            host.run('docker build -t awsdemo-app app')
            host.run('docker build -t awsdemo-nginx nginx')
            host.run('docker stack deploy -c docker-compose.yml awsdemo')
            while True:
                res = host.run('docker service ls | grep awsdemo_web.*0/')
                if not res.stdout.strip():
                    break    
                time.sleep(2)
            host.run('''docker exec $(docker ps -q -f name=awsdemo_web) /usr/src/app/manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser(username="%s", email='%s', password='%s')"''' % (DEFAULT_USER, DEFAULT_LOGIN, DEFAULT_PASS))

    else:
        print('Docker already installed.')
        
@task
def set_pass(c):
    host.run('''docker exec $(docker ps -q -f name=awsdemo_web) /usr/src/app/manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser(username="%s", email='%s', password='%s')"''' % (DEFAULT_USER, DEFAULT_LOGIN, DEFAULT_PASS))

@task
def deploy(c):
    with host.cd('awsdemo'):
        host.run('git pull')
        host.run('git checkout AWS')
        host.run('docker build -t awsdemo-app app')
        host.run('docker build -t awsdemo-nginx nginx')
        host.run('docker service update awsdemo_web')

@task
def pgdump(c):
    cid = host.run('docker container ls | grep awsdemo_db | head -c 12').stdout.strip()
    host.run('''docker container exec %s sh -c "pg_dump -U awsdemo awsdemo | gzip > '/var/lib/postgresql/backups/awsdemo.gz'"'''  % cid)
    host.run('docker cp %s:/var/lib/postgresql/backups/awsdemo.gz /tmp/awsdemo.gz' % cid)
    t = Transfer(host)
    t.get('/tmp/awsdemo.gz')
    