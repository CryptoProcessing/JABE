##Create DB and user
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
если еще не установлен supervisor то
```bash
apt-get install supervisor
```
скопровать в /etc/supervisor/conf.d/
конфиг Gunicorn из папки extra/etc/supervisor/conf.d/jabe.conf

команды для supervisor
```bash
supervisorctl reread
supervisorctl update
supervisorctl status jabe
supervisorctl restart jabe
```
проверка
ps xa | grep gunicorn



## start celery deamon

https://github.com/celery/celery/tree/master/extra/generic-init.d

```bash
 Скопировать celeryd в /etc/init.d/celeryd
$ sudo chmod 755 /etc/init.d/celeryd
$ sudo chown root:root /etc/init.d/celeryd

Скопировать конфигурационный файл в /etc/default/celeryd

Запуск
$ sudo /etc/init.d/celeryd start
Статус
$ sudo /etc/init.d/celeryd status
Остановка
$ sudo /etc/init.
```
##nginx

```bash
ln -s /home/melaman/JABE/nginx_jabe.conf /etc/nginx/sites-available/nginx_jabe.conf