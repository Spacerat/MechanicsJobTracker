from django.contrib import admin

from .models import Mechanic, RepairType, ShopWorkflowFact

admin.site.register([Mechanic, RepairType, ShopWorkflowFact])

# Register your models here.
