# Mechanic Job Tracker

Figure out which mechanics are best at which jobs!

## Installation

### Database a.k.a. you have to use PostgreSQL

I decided to perform the date/time arithmatic in SQL (see notes section).  Since Django [doesn't actually support](https://docs.djangoproject.com/en/1.10/ref/models/fields/#durationfield) this for any databases other than PostgreSQL, you are forced to use it!

#### Installing on a mac

	brew install postgresql

#### Configuring the database

You will have to create a `mechanics` database with a user `myusername`:`mypassword`.

	createdb mechanics
    psql -h localhost mechanics
    
    mechanics=# CREATE ROLE myusername WITH LOGIN PASSWORD 'mypassword';
    mechanics=# GRANT ALL PRIVILEGES ON DATABASE mechanics TO myusername;
    mechanics=# ALTER USER myusername CREATEDB;


### Django app

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
avg_expr = Avg(F('pickup') - F('dropoff') + timedelta(1), output_field=DurationField())

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