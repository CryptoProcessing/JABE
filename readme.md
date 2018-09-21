## Create DB and user

```bash
mysql -u root -p
```

```mysql
CREATE DATABASE jabe;
```
For tests
```mysql
CREATE DATABASE jabe_test;
```

```mysql
GRANT ALL ON jabe.* TO jabe@localhost IDENTIFIED BY 'jabe';
```

```mysql
GRANT ALL ON jabe_test.* TO jabe@localhost IDENTIFIED BY 'jabe';
```

## Virtual environment 
```bash
virtualenv -p python3 venv
source venv/bin/activate
pip3 install -r requirements.txt
```


## Миграции

только один раз
```bash
python manage.py db init
```

при каждом изменении
```bash
python manage.py db migrate
python manage.py db upgrade
```

## start gunicorn
```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn.service
sudo systemctl restart gunicorn.service

sudo systemctl start gunicorn.socket
sudo systemctl restart gunicorn.socket
```

#run celery worker

```bash
celery worker -A celery_worker.celery --loglevel=info

```
or 
## start celery daemon

## nginx

```bash
ln -s /home/melaman/JABE/nginx_jabe.conf /etc/nginx/sites-available/nginx_jabe.conf
```
```bash
python manage.py findprevious -b 250000 -s 25000
```



