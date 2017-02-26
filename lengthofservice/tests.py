from django.test import TestCase
from lengthofservice.models import ShopWorkflowFact

EXPECTED = """
------------------------
Rankings for repair: A (oil change)
-----------------------
Bob: A (national average 1 day, 0:00:00 ) - Average 1 day, 0:00:00 (ratio 1.0)
Simone: A (national average 1 day, 0:00:00 ) - Average 1 day, 12:00:00 (ratio 0.6666666666666666)
Rich: A (national average 1 day, 0:00:00 ) - Average 2 days, 0:00:00 (ratio 0.5)
------------------------
Rankings for repair: B (tire repair)
-----------------------
Simone: B (national average 1 day, 0:00:00 ) - Average 1 day, 0:00:00 (ratio 1.0)
------------------------
Rankings for repair: C (engine inspection)
-----------------------
Simone: C (national average 3 days, 0:00:00 ) - Average 5 days, 0:00:00 (ratio 0.6)
------------------------
Rankings for repair: D (tune-up)
-----------------------
Peter: D (national average 2 days, 0:00:00 ) - Average 2 days, 0:00:00 (ratio 1.0)
Rich: D (national average 2 days, 0:00:00 ) - Average 5 days, 8:00:00 (ratio 0.375)
------------------------
Rankings for repair: E (brake service)
-----------------------
Simone: E (national average 3 days, 0:00:00 ) - Average 3 days, 0:00:00 (ratio 1.0)
------------------------
Rankings for repair: F (oil gasket replacement)
-----------------------
Larry: F (national average 2 days, 12:00:00 ) - Average 2 days, 0:00:00 (ratio 1.25)
Peter: F (national average 2 days, 12:00:00 ) - Average 4 days, 0:00:00 (ratio 0.625)
"""

class TestStuff(TestCase):
	fixtures = ['data.json']

	def test_func(self):
		out = [""]
		rankings_for = None
		for x in ShopWorkflowFact.GetRankings():
			if x.repair_type != rankings_for:
				rankings_for = x.repair_type
				out.append("------------------------")
				out.append("Rankings for repair: {} ({})".format(rankings_for, x.repair_name))
				out.append("-----------------------")
			out.append(str(x))
		result = "\n".join(out+[""])
		# self.assertEqual(result, EXPECTED)
		print(result)