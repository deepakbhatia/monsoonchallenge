#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj
def doc(self,counter, body):
        request_body = json.loads(self.request.body)
        lat_val = request_body['lat']
        latitude = float(str(lat_val))
        lon_val = request_body['lon']
        longitude = float(str(lon_val))
        car_breakdown_area = request_body['car_breakdown_area']
        safe_parking_area = request_body['safe_parking_area']
        water_level_area = request_body['water_level_area']
        my_document = search.Document(
            # Setting the doc_id is optional. If omitted, the search service will create an identifier.
            doc_id = str(counter),
            fields=[
                search.TextField(name='car_break_down', value=str(car_breakdown_area)),
                search.TextField(name='safe_parking_area', value=str(safe_parking_area)),
                search.NumberField(name='water_level_area', value=int(water_level_area)),
                search.GeoField(name='wlocation', value=search.GeoPoint(latitude,longitude))                 
                ])
        documents_list.extend([my_document])
        self.response.write(len(documents_list))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')
class UnsureHandler(webapp2.RequestHandler):  
    def post(self):
        global documents_counter
        global total_docs_counter
        documents_counter+=1   	
        total_docs_counter+=1
        request_body = self.request.body

    	doc(self, total_docs_counter, request_body)
        if documents_counter == 200:
            try:
                index = search.Index(name="index_monsoon")
                index.put(documents_list)
                self.response.write("posted location objects")
  except search.Error:
        self.response.write('Put failed')
    	
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
    ('/crowddata', UnsureHandler)
    #('/storelocationdata', LocationDataHandler)
    #('/crowdsourcedworker', CrowdSourcedTaskHandler)
], debug=True)
