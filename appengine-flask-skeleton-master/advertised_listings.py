from flask import Flask,request,json,jsonify,Response,abort
import global_vars
from google.appengine.ext import ndb
from google.appengine.api import search
from gcloud import storage
from models import User,Listing
from error_handlers import InvalidUsage
from math import radians, sin, cos, sqrt, asin

app = Flask(__name__)


# TODO: write functions for getting listings when a user is not logged in


# Calculate some similarity score ranking
# Maybe try to calculate the probability that the user will rent/enjoy/be-interested-in this item 
# TODO: What are we trying to optimize with this score? The probability of rental or enjoyment or depends?
# Maybe for new users, we try to find the probability that the user will rent. So the first items they see are the ones they're most likely to rent
# For exisiting users who have built some trust with the system, maybe more value is found through discovery of new items?
# Tons of experimentation and exploring to do here... This will make/break the entire app

# This partial snapshots function will be displayed when the user first opens the app
# In the future, we want to display recommended categories of listings that the user might like
# This function will be replaced, but need something for the MVP..
@app.route('/advertised_listings/snapshots/user_id=<int:user_id>/radius=<int:radius_miles>')
def get_advertised_listings_partial_snapshots(user_id, radius_miles):
	# Get the user
	u = User.get_by_id(user_id)
	if u is None:
		raise InvalidUsage('UserID does not match any existing user', status_code=400)

	# Calculate radius in meters
	radius_meters = radius_miles*METERS_PER_MILE

	# Get all of the Listings local to the current user
	index = search.Index(name='Listing')
	query_string = 'distance(location, geopoint('+str(u.last_known_location.lat)+','+str(u.last_known_location.lon)+')) < '+str(radius_meters)+' AND NOT owner_id='+str(user_id)

	# FIXME: Currently returns only 20 items at a time (search limit). Also, return ids_only!
	try:
		# FIXME: add limit to the number of items returned
		results = index.search(query_string)
	except search.Error:
		abort(500)


	matched_listings = get_matched_listings(u, radius_miles, results)

	resp 			 = jsonify({'listings':matched_listings})
	resp.status_code = 200
	return resp





ListingsFetchedPerQueryCycle = 100		# Database will return 100 listings per fetch cycle
MaxNumListingsToReturnToUser = 10		# return 10 listings matching the user's search

# This function returns listings whose names match part of the search string sent by the user
@app.route('/advertised_listings/user_id=<int:user_id>/radius=<int:radius_miles>/search=<search_string>')
def search_listings(user_id, radius_miles, search_string):
	# Get the user
	u = User.get_by_id(user_id)
	if u is None:
		raise InvalidUsage('UserID does not match any existing user', status_code=400)

	# Calculate radius in meters
	radius_meters = radius_miles*METERS_PER_MILE

	index = search.Index(name='Listing')
	query_string = 'distance(location, geopoint('+str(u.last_known_location.lat)+','+str(u.last_known_location.lon)+')) < '+str(radius_meters)+' AND NOT owner_id='+str(user_id)+' AND name: '+search_string

	# FIXME: Currently returns only 20 items at a time (search limit). Also, return ids_only!
	try:
		# FIXME: add limit to the number of items returned
		results = index.search(query_string)
	except search.Error:
		abort(500)

	matched_listings = get_matched_listings(u, radius_miles, results)

	resp 			 = jsonify({'results matching '+search_string:matched_listings})
	resp.status_code = 200
	return resp




# Helper function that returns a detailed list of listings info given a Search API results object
def get_matched_listings(user, radius_miles, results):
	matched_listings = []
	for matched_listing in results:
		try:
			l = Listing.get_by_id(int(matched_listing.doc_id))
		except:
			abort(500)
		if l is None:
			# If there is an inconsistency and item is not found in Datastore, raise some error here...
			# raise InvalidUsage('Inconsistency in databases. Item not found in Datastore.', status_code=400)
			continue
		# FIXME: send only what's needed..
		distance 		= haversine(l.location.lat,l.location.lon,user.last_known_location.lat,user.last_known_location.lon)
		listing_data	= {'listing_id':l.key.id(), 'name':l.name, 'rating':l.rating, 
							'daily_rate':l.daily_rate, 'distance':distance,
							'score':item_score(distance, radius_miles, l.total_value, global_vars.MAX_PRICE, l.category, user.category_weights), 
							'image_media_links':get_listing_images(l.key.id())}
		matched_listings += [listing_data]

	return matched_listings







distance_weight 		= 0.5
price_weight 			= 0.5
category_weight 		= 0

# Function that returns a score for a listing, depending on
# 1. how far away it is
# 2. how much it costs
# 3. how often the user tends to rent items from the same category
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

