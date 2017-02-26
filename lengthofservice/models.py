from django.db import models
from collections import namedtuple
from django.db.models import Avg, F, DurationField
from datetime import datetime, timedelta
from django.conf import settings

def database_timedelta(t):
    """ Since MySQL and PostgreSQL use different datatypes to represent time intervals,
    we have to do this to make sure that we can do our arithmatic in SQL in either database.
    """
    if settings.DATABASES['default']['ENGINE'] == settings.PSQL_DATABASE:
        return t
    else:
        return float(t.total_seconds() * 1e6)

class MechanicJobAnalysis(namedtuple('MechanicJobAnalysis', ['name', 'repair_type', 'repair_name', 'nat_avg', 'avg_time', 'mechanic'])):
    """ A namedtuple for storing mechanic job analysis results """
    __slots__ = ()
    @property
    def ratio(self):
        """ Get the ratio of national-average-time:analysis-time. Higher is better """
        return self.nat_avg / self.avg_time

    def __str__(self):
        """ Get a human readable representation of the report """
        return "{}: {} (national average {} ) - Average {} (ratio {})".format(self.name, self.repair_type, self.nat_avg, self.avg_time, self.ratio)

class Mechanic(models.Model):
    """ Model of a mechanic """
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

    class Meta():
        ordering = ('name',)

class RepairType(models.Model):
    """ Model of a type of repair """
    code = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=30)
    national_average = models.DurationField()

    def __str__(self):
        return "{} - {} (average {})".format(self.code, self.name, self.national_average)

    class Meta():
        ordering = ('code',)

class ShopWorkflowFact(models.Model):
    """ Model of a log of work done by a mechanic, over a certain time and for a certain job type """
    dropoff = models.DateField()
    pickup = models.DateField()
    mechanic = models.ForeignKey(Mechanic, related_name='jobs')
    repair_type = models.ForeignKey(RepairType)

    def __str__(self):
        return "Repair no {}. {} from {} to {}: {} -".format(self.id, self.mechanic, self.dropoff, self.pickup, self.repair_type)


    @classmethod
    def GetRankings(cls):
        """ For each mechanic and job type, get their average time they take to complete that kind of job, and the national average for that job """

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

        # Return the results as MechanicJobAnalysis objects
        return [MechanicJobAnalysis(**r) for r in results]

    class Meta():
        ordering = ('id',)