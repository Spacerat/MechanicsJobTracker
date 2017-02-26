# Mechanic Job Tracker

Figure out which mechanics are best at which jobs!

## Database Installation

### You have to use PostgreSQL or MySQL

I decided to perform the date/time arithmatic in SQL (see notes section). As a result, you can't use sqlite3 since it stores datetimes as strings, and hence doesn't aggregation over time intervals. PostgreSQL has an interval data type and MySQL just uses microseconds, so they work OK.

### Picking a database

In settings.py, you can change `DATABASES['default']['engine']` to select whether to use mysql or postgresql

### PostgreSQL 

#### Installing on a mac

	brew install postgresql
	pg_ctl -D /usr/local/var/postgres start

#### Configuring the database

You will have to create a `mechanics` database with a user `myusername`:`mypassword`, then shell into the database

	createdb mechanics
    psql -h localhost mechanics

And enter some commands

```sql
CREATE ROLE myusername WITH LOGIN PASSWORD 'mypassword';
GRANT ALL PRIVILEGES ON DATABASE mechanics TO myusername;
ALTER USER myusername CREATEDB;
```

### MySQL

#### Installing on a mac

	brew install msql
	mysql.server start
    

#### Configuring the database

Log into the database

	mysql -u root -p

Then enter some commands

``` sql
CREATE DATABASE taskbuster_db;
CREATE USER 'myusername'@'localhost' IDENTIFIED BY 'mypassword';
GRANT ALL PRIVILEGES ON mechanic.* TO 'myusername'@'localhost';
GRANT ALL PRIVILEGES ON test_mechanic.* TO 'myusername'@'localhost';
FLUSH PRIVILEGES;
quit
```

## Django app installation

Simply install the requirements (django and psycopg2); you may wish to use a virtualenv.

	pip install -r requirements.txt
    
Then initialise the database

	python manage.py migrate
    python manage.py loaddata data.json
    
## Testing

	python manage.py test

You can also

	python manage.py createsuperuser
    ...
	python manage.py runserver
    
Then navigate to `http://localhost:8000/admin` to set up more data, and check the output in the shell


```python
(env) joe@Joebook-Pro ~/a/mechanics (master)> python manage.py shell
>>> from lengthofservice.models import ShopWorkflowFact
>>> ShopWorkflowFact.GetRankings()
```

## Notes

Note that all of the ranking logic is performed in a single SQL query using joins and aggregates. The code in models.py: ShopWorkflowFact.GetRankings() contructs it like this:

``` python
# Construct an SQL expression which will calcualte the average time taken over a group of ShopWorkflowFact rows
one_day = database_timedelta(timedelta(1))
avg_expr = Avg(F('pickup') - F('dropoff') + one_day, output_field=DurationField())

# Group by mechanic and repair type, and get the average times.
results = ShopWorkflowFact.objects.values('mechanic', 'repair_type').annotate(
    avg_time=avg_expr, 
    nat_avg=F('repair_type__national_average'), 
    name=F('mechanic__name'),
    repair_name=F('repair_type__name'),
).order_by('repair_type', 'avg_time')
```

To see the SQL query in practice, set `LOG_SQL = True` in settings.py, then run GetRankings as described above.

A bunch of SQL will be printed out. After reformatting, it looks like this: a single query joining the `shopworkflowfact` table to `mechanic` and `repairtype`, grouping by mechanics and repair type, and calculating the average job duration.

```sql
SELECT     "lengthofservice_shopworkflowfact"."mechanic_id",
           "lengthofservice_shopworkflowfact"."repair_type_id",
           "lengthofservice_repairtype"."national_average" AS "nat_avg",
           "lengthofservice_mechanic"."name" AS "name",
           avg((Age("lengthofservice_shopworkflowfact"."pickup", "lengthofservice_shopworkflowfact"."dropoff") + '1 days 0.000000 seconds'::interval)) AS "avg_time",
           "lengthofservice_repairtype"."name" AS "repair_name"
FROM       "lengthofservice_shopworkflowfact"
INNER JOIN "lengthofservice_mechanic"
ON         ("lengthofservice_shopworkflowfact"."mechanic_id" = "lengthofservice_mechanic"."id")
INNER JOIN "lengthofservice_repairtype"
ON         ("lengthofservice_shopworkflowfact"."repair_type_id" = "lengthofservice_repairtype"."code")
GROUP BY   "lengthofservice_shopworkflowfact"."mechanic_id",
           "lengthofservice_shopworkflowfact"."repair_type_id",
           "lengthofservice_mechanic"."name",
           "lengthofservice_repairtype"."code"
ORDER BY   "lengthofservice_repairtype"."code" ASC,
           "avg_time" ASC;args=(datetime.timedelta(1),)
```