from google.appengine.ext import ndb
import webapp2
import json
 
class ARoute(ndb.Model):
	location = ndb.StringProperty(repeated=True);
	date_posted = ndb.DateTimeProperty(indexed=True);

	def addRoute(locations, date_route):
		location = locations
		date_posted = date_route

class CarData(ndb.Model):
	speed = ndb.StringProperty()
	wiper_speed = ndb.StringProperty()
	route = ndb.StructuredProperty(ARoute)
	water_level = ndb.StringProperty(repeated=True)
class StreetCondition(ndb.Model):
	position = ndb.GeoPtProperty()
	#lon = ndb.StringProperty()
	#water_level_area = ndb.StringProperty()
	#car_breakdown_area = ndb.StringProperty()
	#safe_parking_area = ndb.StringProperty()



    

