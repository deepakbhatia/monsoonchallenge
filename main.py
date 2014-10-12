#!/usr/bin/env python
#
#
import webapp2
import json
from models import *
import datetime
from google.appengine.api import taskqueue
from google.appengine.api import search

documents_counter=0
total_docs_counter=0
documents_list=[]
TRUE = 1
FALSE = 0
DEBUG = TRUE
geopoints = []
def geocalc(lat1, lon1, lat2, lon2):
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon1 - lon2

    EARTH_R = 6372.8

    y = sqrt(
        (cos(lat2) * sin(dlon)) ** 2
        + (cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)) ** 2
        )
    x = sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(dlon)
    c = atan2(y, x)
    return EARTH_R * c
def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj
def person_doc(self,counter, body):
        request_body = json.loads(self.request.body)
        lat_val = request_body['lat']
        latitude = float(str(lat_val))
        lon_val = request_body['lon']
        longitude = float(str(lon_val))
        car_breakdown_area = request_body['car_breakdown_area']
        safe_parking_area = request_body['safe_parking_area']
        water_level_area = request_body['water_level_area']
        # if len(geopoints) == 0:
        #     poi = latitude,longitude;
        #     geopoints.extend(poi)
        # else:
        #     for eachpoi in geopoints:
        #         distance = geocalc(latitude,longitude,eachpoi[0],eachpoi[1])
        #         if distance > 1:
        #             geopoints.extend(poi)
        my_document = search.Document(
            # Setting the doc_id is optional. If omitted, the search service will create an identifier.
            doc_id = str(counter),
            fields=[
                search.TextField(name='supplier', value='person'),
                search.NumberField(name='wiper_speed', value=-100.0),
                search.NumberField(name='speed', value=-100.0),
                search.TextField(name='car_break_down', value=str(car_breakdown_area)),
                search.TextField(name='car_parked', value=str(safe_parking_area)),
                search.NumberField(name='water_level_area', value=int(water_level_area)),
                search.GeoField(name='wlocation', value=search.GeoPoint(latitude,longitude))                 
                ])
        documents_list.extend([my_document])
        self.response.write(len(documents_list))
def car_doc(self,counter):
        #body = self.request.body
        #json_body = json.loads(body)
        latitude = self.request.get('lat')
        
        longitude = self.request.get('lon')
        car_speed = self.request.get('car_speed')
        wiper_speed = self.request.get('wiper_speed')
        car_parked = self.request.get('car_parked')
        water_level_area = self.request.get('water_level_area')
        car_breakdown_area = self.request.get('car_breakdown_area')
        #self.response.write(float(car_speed)*2)
        #self.response.write(float(water_level_area)*2)
        my_document = search.Document(
            # Setting the doc_id is optional. If omitted, the search service will create an identifier.
            doc_id = str(counter),
            fields=[
                search.TextField(name='supplier', value='car'),
                search.NumberField(name='speed', value=float(car_speed)),
                search.TextField(name='car_break_down', value=str(car_breakdown_area)),
                search.NumberField(name='wiper_speed', value=float(wiper_speed)),
                search.TextField(name='car_parked', value=str(car_parked)),
                search.NumberField(name='water_level_area', value=int(water_level_area)),
                search.GeoField(name='wlocation', value=search.GeoPoint(float(latitude),float(longitude)))
                ])
        documents_list.extend([my_document])
        s = '%s, %s' % (len(documents_list), counter)
        self.response.write(s)
def query_result(self, index, query_string):
    try:
        # val = 2
        # val_1 = 15.7979
        # result_string="{'results':["
        # result_string +="{"
        # result_string+="'location':{ 'lat': '%s' , 'lon': '%s' }, " % (38.76817681, -9.864823)
        # #result_string+="'water_level':'%s', " % val

        # result_string+="'water_level':'%s'," % val
        # result_string+="'car_parked':'%s'," % "yes"
        # result_string+="'wiper_speed':'%s'," % val_1
        # result_string +="}"
        # result_string+="]}"

        results = index.search(query_string)
        self.response.write('In local 2')
        total_matches = results.number_found
        print total_matches
        self.response.write(total_matches)
        #document;
        # Iterate over the documents in the results
        result_string="{'results':[";
        counter=0;
        for scored_document in results:
          # handle results
          #document = scored_document
          if counter > 0:
            result_string +=","
          result_string +="{"
          result_string+="'location':{ 'lat': '%s' , 'lon': '%s' }, " % (scored_document.field('wlocation').value.latitude, scored_document.field('wlocation').value.longitude)
          result_string+="'water_level':'%s', " % (scored_document.field('water_level_area').value)
          result_string+="'car_parked':'%s', " % (scored_document.field('car_parked').value)
          result_string+="'wiper_speed':'%s', " % (scored_document.field('wiper_speed').value)
          result_string+="'supplier':'%s', " % (scored_document.field('supplier').value)
          result_string+="'car_break_down':'%s', " % (scored_document.field('car_break_down').value)
          result_string+="'speed':'%s', " % (scored_document.field('speed').value)

          result_string +="}"
          counter = counter+1

        result_string="]}"
        self.response.write(json.dumps(result_string))

        #   self.response.write(scored_document.field('wlocation').value.latitude)
    except search.Error:
        self.response.write('Search failed')
class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')
class QueryHandler(webapp2.RequestHandler):
    def get(self):
        query_type = self.request.get('query_type')

        index = search.Index(name="crowdsourced_mumbai_monsoon")
        if query_type == "NEAR_BY":
            latitude = self.request.get('lat')
            longitude = self.request.get('lon')

            geostring = "geopoint(%s,%s)" % (latitude,longitude)
            query_string = "distance(wlocation, %s) < 1000" % geostring
            query = search.Query(query_string = query_string)
            query_result(self,index, query)
            #self.response.write('NEAR_BY = %s' % geostring)
        elif query_type == "CAR_DATA":
         
            query_options = search.QueryOptions(    
                    returned_fields=['wlocation', 'water_level', 'wiper_speed', 'speed', 'car_break_down','supplier','car_parked'],
                    )
            self.response.write('WATER_LEVEL')
            self.response.write('Query Handler')
            query_string = "water_level > 1 AND supplier = car"
            query = search.Query(query_string = query_string, options = query_options)
        elif query_type == "HIGH_FLOODING":
        
            query_options = search.QueryOptions(    
                    returned_fields=['wlocation', 'water_level', 'wiper_speed', 'speed', 'car_break_down','supplier','car_parked'],
                    )
            self.response.write('WATER_LEVEL')
            self.response.write('Query Handler')
            for point_of_interest in high_flooding_areas:
                latitude = point_of_interest[0]
                longitude = point_of_interest[1]
                geostring = "geopoint(%s,%s)" % (latitude,longitude)
                query_string = "distance(wlocation, %s) < 5000"  % geostring
                query = search.Query(query_string = query_string, options = query_options)
        elif query_type == "DIVERSION":
             
            query_options = search.QueryOptions(    
                    returned_fields=['wlocation', 'water_level', 'wiper_speed', 'speed', 'car_break_down','supplier','car_parked'],
                    )
            self.response.write('WATER_LEVEL')
            self.response.write('Query Handler')
            for point_of_interest in diversion_areas:
                latitude = point_of_interest[0]
                longitude = point_of_interest[1]
                geostring = "geopoint(%s,%s)" % (latitude,longitude)
                query_string = "distance(wlocation, %s) < 5000"  % geostring
                query = search.Query(query_string = query_string, options = query_options)
class PersonMonsoonHandler(webapp2.RequestHandler):  
    def post(self):
        global documents_counter
        global total_docs_counter
        global documents_list
        documents_counter+=1   	
        total_docs_counter+=1
        request_body = self.request.body

    	person_doc(self, total_docs_counter, request_body)
        if documents_counter >= 1:
            try:
                documents_counter = 0

                index = search.Index(name="crowdsourced_mumbai_monsoon")
                index.put(documents_list)
                if DEBUG == TRUE:
                    self.response.write("PERSON CAR location objects")
                    documents_list=[]
            except search.Error:
                if DEBUG == TRUE:
                    self.response.write('Put failed')
class CarMonsoonDataHandler(webapp2.RequestHandler):
    def post(self):
        global documents_counter
        global total_docs_counter
        global documents_list
        documents_counter+=1    
        total_docs_counter+=1
        car_doc(self, total_docs_counter)
        if documents_counter >= 20:
            try:
                documents_counter = 0
                index = search.Index(name="crowdsourced_mumbai_monsoon")
                index.put(documents_list)
                if DEBUG == TRUE:
                    self.response.write("CAR DATA location objects")
                    documents_list=[]
            except search.Error:
                if DEBUG == TRUE:
                    self.response.write('Put failed')
        #query_string = "distance(job_location, geopoint(38.7234211,-9.1873166)) < 10" 

        #index = search.Index(name="index_monsoon")

class GetMyCarHandler(webapp2.RequestHandler):
    def get(self):
        car_key = ndb.Key(CarData, self.request.get('car_id'))

        query = "select * from CarData order by ARoute.date_posted desc limit 10"
        cardatasets = CarData.query(CarData._key == car_key).order(-CarData.route.date_posted).fetch(10)
        #self.response.headers['Content-Type'] = 'application/json'
        for everydata in cardatasets:
            response_value = "{'speed':%s, 'wiper_speed': %s, 'date': %s, 'water_levels': %s, 'position': %s}" % (json.dumps(everydata.speed), json.dumps(everydata.wiper_speed), json.dumps(date_handler(everydata.route.date_posted)), json.dumps(everydata.water_level), json.dumps(everydata.route.location))
            self.response.out.write(response_value)

        self.response.write('Hello world!')
class CarDataHandler(webapp2.RequestHandler):
    def post(self):
        routes_list=[]
        water_level_list=[]
        car_id = self.request.get('car_id')
        car_speed = self.request.get('speed')
        car_wiper_speed = self.request.get('wiper_speed')
        date_today = self.request.get('date')
        date_val = float(long(date_today))
        route = self.request.get('route')
        json_route = json.loads(route)
        routes = json_route['routes']
        for each_route in routes:
            position = each_route['position']
            #lon = each_route['lon']
            #position = ndb.GeoPt(float(lat), float(lon))
            routes_list.extend([position])

        aroute = ARoute(location = routes_list, date_posted = datetime.datetime.fromtimestamp(date_val))
        water_levels = self.request.get('level')
        json_water_levels = json.loads(water_levels)['water_levels']
        for each_level in json_water_levels:
            l = each_level['level']
            water_level_list.extend([l])
        car_data_trip = CarData(id = car_id, speed = car_speed, 
            wiper_speed = car_wiper_speed, route = aroute, water_level = water_level_list)
        car_data_trip.put()

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/fromcar', CarDataHandler),
    ('/getrecentcardata', GetMyCarHandler),
    ('/crowddata', PersonMonsoonHandler),
    ('/carcrowddata', CarMonsoonDataHandler),
    ('/givemedata', QueryHandler)
], debug=True)
