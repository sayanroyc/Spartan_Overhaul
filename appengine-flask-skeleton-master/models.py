from google.appengine.ext import ndb

class Category(ndb.Model):
	name 				= ndb.StringProperty(required=True)

class CategoryWeight(ndb.Model):
	category 			= ndb.KeyProperty(required=True, kind=Category)
	weight				= ndb.FloatProperty(required=True)

class User(ndb.Model):
	first_name 												= ndb.StringProperty(required=True)
	last_name 												= ndb.StringProperty(required=True)
	notification_tokens										= ndb.StringProperty(repeated=True)
	phone_number 											= ndb.StringProperty()
	is_phone_number_verified 								= ndb.BooleanProperty(required=True)
	phone_number_verification_code 							= ndb.IntegerProperty()
	phone_number_verification_code_distribution_datetime 	= ndb.DateTimeProperty()
	email 													= ndb.StringProperty(required=True)
	is_email_verified 										= ndb.BooleanProperty(required=True)
	email_verification_code 								= ndb.IntegerProperty()
	password 												= ndb.StringProperty()
	facebook_id												= ndb.StringProperty()
	signup_method 											= ndb.StringProperty(required=True, choices=['Facebook', 'Email', 'Phone Number'])
	credit 													= ndb.FloatProperty(required=True) # How much money the user owes at the end of the week
	debit 													= ndb.FloatProperty(required=True) # How much money the user has credited to their account (i.e. $15 from signing up or promotions)
	date_created 											= ndb.DateTimeProperty(auto_now_add=True)
	date_last_modified 										= ndb.DateTimeProperty(auto_now=True)
	status													= ndb.StringProperty(required=True, choices=['Active', 'Inactive', 'Deactivated'])
	last_known_location										= ndb.GeoPtProperty()
	category_weights										= ndb.StructuredProperty(CategoryWeight, repeated=True)
	# profile_image	 										= ndb.BlobProperty(required=False, indexed=False)
	# TODO: More required fields like BrainTree client token, images, address, etc.

class Meeting_Location(ndb.Model):
	user 				= ndb.KeyProperty(required=True, kind=User)
	google_places_id 	= ndb.StringProperty(required=True)
	name 				= ndb.StringProperty(required=True)
	address 			= ndb.StringProperty(required=True)
	date_created		= ndb.DateTimeProperty(auto_now_add=True)
	date_last_modified 	= ndb.DateTimeProperty(auto_now=True)
	is_private 			= ndb.BooleanProperty(required=True) # Whether or not any user can see this address

class Listing(ndb.Model):
	owner 				= ndb.KeyProperty(required=True, kind=User)
	renter 				= ndb.KeyProperty(kind=User)
	status 				= ndb.StringProperty(required=True, choices=['Available', 'Reserved', 'Rented', 'Unavailable', 'Damaged', 'Unlisted', 'Deactivated', 'Deleted'])
	name 				= ndb.StringProperty(required=True)
	item_description 	= ndb.StringProperty(required=True)
	rating		 		= ndb.FloatProperty()	# Value of -1 is used to signal no rating
	total_value 		= ndb.FloatProperty(required=True)
	hourly_rate 		= ndb.FloatProperty(required=True)
	daily_rate 			= ndb.FloatProperty(required=True)
	weekly_rate			= ndb.FloatProperty(required=True)
	category 			= ndb.KeyProperty(required=True, kind=Category)
	date_created		= ndb.DateTimeProperty(auto_now_add=True)
	date_last_modified 	= ndb.DateTimeProperty(auto_now=True)
	location			= ndb.GeoPtProperty(required=True, indexed=True)
	# location_lat		= ndb.FloatProperty(required=True)
	# location_lon		= ndb.FloatProperty(required=True)
	# TODO: More required fields like images, listed date, item location, user-selected related items, totalReturns, etc.

class Proposed_Meeting_Time(ndb.Model):
	time 			= ndb.DateTimeProperty(required=True) # The time of the meeting proposal
	duration		= ndb.FloatProperty(required=True, default=30.0) # Duration of the timeframe in minutes
	is_available 	= ndb.BooleanProperty(required=True)


class Meeting_Event(ndb.Model):
	owner 						= ndb.KeyProperty(required=True, kind=User)
	renter 						= ndb.KeyProperty(required=True, kind=User)
	listing 					= ndb.KeyProperty(required=True, kind=Listing)
	deliverer 					= ndb.StringProperty(required=True, choices=['Owner', 'Renter']) # person who has the item
	status 						= ndb.StringProperty(required=True, choices=['Proposed', 'Scheduled', 'Delayed', 'Canceled', 'Rejected', 'Concluded'])
	proposed_meeting_times 		= ndb.StructuredProperty(Proposed_Meeting_Time, repeated=True)
	proposed_meeting_locations 	= ndb.KeyProperty(kind=Meeting_Location, repeated=True)
	time 						= ndb.DateTimeProperty()
	location 					= ndb.KeyProperty(kind=Meeting_Location)
	date_created 				= ndb.DateTimeProperty()

	# FIXME: Are these necessary? 
	owner_confirmation_time 	= ndb.DateTimeProperty()	# Moment that the Owner confirms the Handoff
	renter_confirmation_time 	= ndb.DateTimeProperty()	# Moment that the Renter confirms the Handoff
	



	
# class Message(ndb.Model):
# 	sender 			= ndb.KeyProperty(required=True, kind=User)
# 	receiver 		= ndb.KeyProperty(required=True, kind=User)
# 	text 			= ndb.StringProperty()
# 	date_created 	= ndb.DateTimeProperty()


# class Meeting_Message(Message):
# 	event = ndb.KeyProperty(required=True, kind=Meeting_Event)


# TODO: Add duration property (how many time_frames the rental event is expected to last for)
class Rent_Event(ndb.Model):
	owner 				= ndb.KeyProperty(required=True, kind=User)
	renter 				= ndb.KeyProperty(required=True, kind=User)
	listing 			= ndb.KeyProperty(required=True, kind=Listing)
	rental_rate 		= ndb.FloatProperty()
	time_frame 			= ndb.StringProperty(choices=['Hour', 'Day', 'Week'])
	status 				= ndb.StringProperty(required=True, choices=['Inquired', 'Proposed', 'Scheduled Start', 'Ongoing', 'Scheduled End', 'Canceled', 'Rejected', 'Concluded'])
	proposed_by 		= ndb.StringProperty(choices=['Renter', 'Owner']) 	# If the Renter proposes, think of this as a Rent Request. If the Owner proposes, the Renter is 'pre-approved' to Rent
	start_meeting_event = ndb.KeyProperty(kind=Meeting_Event)
	end_meeting_event 	= ndb.KeyProperty(kind=Meeting_Event)
	date_created 		= ndb.DateTimeProperty(required=True)
	date_responded		= ndb.DateTimeProperty() # How long it takes for the Owner to respond to the request
	date_ended			= ndb.DateTimeProperty() # How long it takes to go from creation to Canceled/Rejected/Concluded



'''
class ItemImage(ndb.Model):
	# image = db.BlobProperty(required=True, indexed=False)
	image 				= ndb.BlobKeyProperty()
	item 				= ndb.KeyProperty(required=True, indexed=True, kind=Item) #, collection_name="images")
	description 		= ndb.StringProperty(required=False, indexed=False)

class ItemReview(ndb.Model):
	user 				= ndb.KeyProperty(required=True, indexed=True, kind=User) #, collection_name="itemReviews")
	item 				= ndb.KeyProperty(required=True, indexed=True, kind=Item) #, collection_name="reviews")
	rating 				= ndb.FloatProperty(required=True, indexed=True, default=0.0)
	comment 			= ndb.TextProperty(required=False, indexed=False)
	date 				= ndb.DateTimeProperty(required=True, indexed=True)
	# TODO: More required fields?

class RenterReview(ndb.Model):
	user 				= ndb.KeyProperty(required=True, indexed=True, kind=User) #, collection_name="renterReviews")
	renter 				= ndb.KeyProperty(required=True, indexed=True, kind=User) #, collection_name="reviews")
	rating 				= ndb.FloatProperty(required=True, indexed=True, default=0.0)
	comment 			= ndb.TextProperty(required=False, indexed=False)
	date 				= ndb.DateTimeProperty(required=True, indexed=True)
	# TODO: More required fields?

class TimeDispute(ndb.Model):
	owner 					= ndb.KeyProperty(required=True, indexed=True, kind=User) #, collection_name="time_disputes_as_owner")
	renter 					= ndb.KeyProperty(required=True, indexed=True, kind=User) #, collection_name="time_disputes_as_renter")
	rentEvent 				= ndb.KeyProperty(required=True, indexed=True, kind=RentEvent) #, collection_name="time_disputes")
	timeDifference 			= ndb.FloatProperty(required=True, indexed=True) # Time dispute in hours
	meeting 				= ndb.KeyProperty(required=True, indexed=False, kind=MeetingEvent) #, collection_name="time_dispute")

'''