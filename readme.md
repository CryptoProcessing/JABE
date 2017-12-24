Create DB and user
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
