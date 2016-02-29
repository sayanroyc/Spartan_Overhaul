from flask import Flask,request,json,jsonify,Response,abort
import global_vars
from google.appengine.ext import ndb
from google.appengine.api import search
from gcloud import storage
from models import User,Listing
from error_handlers import InvalidUsage
from math import radians, sin, cos, sqrt, asin

app = Flask(__name__)


# Calculate some similarity score ranking
# Maybe try to calculate the probability that the user will rent/enjoy/be-interested-in this item 
# TODO: What are we trying to optimize with this score? The probability of rental or enjoyment or depends?
# Maybe for new users, we try to find the probability that the user will rent. So the first items they see are the ones they're most likely to rent
# For exisiting users who have built some trust with the system, maybe more value is found through discovery of new items?
# Tons of experimentation and exploring to do here... This will make/break the entire app

@app.route('/advertised_listings/snapshots/user_id=<int:user_id>/radius=<int:radius_miles>')
def get_advertised_listings_partial_snapshots(user_id, radius_miles):
	# Get the user
	u = User.get_by_id(user_id)
	if u is None:
		raise InvalidUsage('UserID does not match any existing user', status_code=401)

	# Get the user's location data
	user_location_lat 	= u.last_known_location.lat
	user_location_lon 	= u.last_known_location.lon

	# Calculate radius in meters
	radius_meters 		= radius_miles*METERS_PER_MILE

	# Get all of the Listings local to the current user
	index = search.Index(name='Listing')
	query_string = 'distance(location, geopoint('+str(user_location_lat)+','+str(user_location_lon)+')) < '+str(radius_meters)

	# FIXME: Currently returns only 20 items at a time (search limit). Also, return ids_only!
	try:
		# FIXME: add limit to the number of items returned
		results = index.search(query_string)
		matched_listings = []
		for matched_listing in results:
			l = Listing.get_by_id(int(matched_listing.doc_id))
			if l is None:
				# If there is an inconsistency and item is not found in Datastore, delete it from search API
				# Raise some error here...
				# raise InvalidUsage('Inconsistency in databases. Item not found in Datastore.', status_code=402)
				continue
			owner_id = l.owner.integer_id()
			if user_id == owner_id:
				# We don't want to display the owner's own items.. 
				continue
			# FIXME: send only what's needed..
			listing_id 			= str(l.key.id())
			name 				= l.name
			listing_value		= float(l.total_value)
			daily_rate			= float(l.daily_rate)
			category_id 		= str(l.category.id())
			location 			= str(l.location)
			distance 			= haversine(l.location.lat,l.location.lon,user_location_lat,user_location_lon)
			score 				= item_score(distance, radius_miles, listing_value, global_vars.MAX_PRICE, l.category, u.category_weights)
			rating				= l.rating
			image_media_links	= get_listing_images(listing_id)
			listing_data		= {'listing_id':listing_id, 'name':name, 'rating':rating, 'category_id':category_id, 'daily_rate':daily_rate, 'location':location, 'distance':distance, 'score':score, 'image_media_links':image_media_links}
			matched_listings += [listing_data]
	except search.Error:
		logging.exception('Search failed')

	# Return a list of items
	# resp 			 = jsonify({'results near ('+str(user_location_lat)+', '+str(user_location_lon)+')':matched_listings})
	resp 			 = jsonify({'listings':matched_listings})
	resp.status_code = 200
	return resp

'''
@app.route('/listings/snapshots_no_user', methods=['POST'])
def get_default_no_user_listings():
	json_data = request.get_json()
	
	# TODO: Get location data

	# Get all of the items local to the current user
	# FIXME: Currently returning all items listed in the database
	qry   = Listing.query()
	items = qry.fetch(limit=100)

	# Calculate a score for each item
	data = []
	for i in items:
		snapshot_id = str(i.key.id())
		score 		= float(no_user_score(i))
		item_data 	= {'snapshot_id':snapshot_id, 'score':score}
		data += [item_data]

	# Return a list of the scores and 
	resp 			 = jsonify({'listings':data})
	resp.status_code = 200
	return resp
'''




distance_weight 		= 0.5
price_weight 			= 0.5
category_weight 		= 0

def item_score(dist, rad, price, max_price, item_category, user_category_weights):
	dist_score = distance_score(dist, rad)
	pri_score = price_score(price, max_price)
	cat_score = category_score(item_category, user_category_weights)

	distance_weighted_score = distance_weight*dist_score
	price_weighted_score	= price_weight*pri_score
	category_weighted_score	= category_weight*cat_score

	return (distance_weighted_score + price_weighted_score + category_weighted_score)
	# return (dist_score, pri_score, cat_score)


# maps distance from [0, MAXRADIUS] to [0, 1] and returns a score based on distance
def distance_score(dist, rad):
	return -1.0*dist/rad


# maps price from [0, MAXPRICE] to [0, 1] and returns a score based on price
def price_score(price, max_price):
	return -1.0*price/max_price


# returns weight increases depending on user's category tendencies and the current item
def category_score(item_category, user_category_weights):
	for user_category_weight in user_category_weights:
		if user_category_weight.category.id() == item_category.id():
			return user_category_weight.weight
	return 0



# Helper function to calculate distance from one location to another
# Move this some place else..
# Should connect listings.py and search.py into one, add this function to it
METERS_PER_MILE = 1609.344
EARTH_RADIUS = 6378135 			# meters
def haversine(lat1, lon1, lat2, lon2):
	dLat = radians(lat2 - lat1)
	dLon = radians(lon2 - lon1)
	lat1 = radians(lat1)
	lat2 = radians(lat2)

	a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
	c = 2*asin(sqrt(a))
	return EARTH_RADIUS * c / METERS_PER_MILE


# Helper function to return a listing's image links
def get_listing_images(listing_id):	
	client = storage.Client()
	bucket = client.get_bucket(global_vars.LISTING_IMG_BUCKET)

	listing_img_objects = bucket.list_blobs(prefix=str(listing_id))
	listing_img_media_links = []
	for img_object in listing_img_objects:
		listing_img_media_links += [img_object.media_link]

	return listing_img_media_links




### Server Error Handlers ###
@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
	response = jsonify(error.to_dict())
	response.status_code = error.status_code
	return response

@app.errorhandler(404)
def page_not_found(e):
	"""Return a custom 404 error."""
	return 'Sorry, Nothing at this URL.', 404

@app.errorhandler(500)
def application_error(e):
	"""Return a custom 500 error."""
	return 'Sorry, unexpected error: {}'.format(e), 500

