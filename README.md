# Spartan_Server

### Project Organization
Each separate set of APIs are grouped into separate .py files based on objects. For example, all of the HTTP calls relating to users (creating new, updating info, etc)
are grouped into `users.py`. Similarly, all of the HTTP calls for listings (creating new, updating info, uploading pics) in the database are grouped into `listings.py`. 

To signal these functional distinctions in the methods, each file is given a special HTTP extension. For example, all API calls relating to users should be sent to `http://bygo-client-server.appspot.com/users/*` where `*` is the name of desired function. See the documentation in the Workflows section for more exmaples.



#################################################
#################################################
#################################################
############## TODO: FIX WORKFLOWS ##############
#################################################
#################################################
#################################################


appcfg.py -A molten-unison-112921 update app.yaml 
###################################################

########### USER FUNCTIONS ##############
### Create User
curl -H "Content-Type: application/json" -X POST -d "{\"first_name\":\"Lester\", \"last_name\":\"Nygaard\", \"email\":\"lg_killa@gasdfasfdmail.com\", \"phone_number\":\"6451823434\", \"password\":\"password123\", \"signup_method\":\"Phone Number\", \"location_lat\":\"40.106361\", \"location_lon\":\"-88.2327326\"}" http://molten-unison-112921.appspot.com/user/create

### Add/Update User profile picture
curl -X POST -F "filename=profile_picture.jpg" -F "userfile=@C:/Users/Sayan/Desktop/lion-male-roar.jpg" http://molten-unison-112921.appspot.com/user/new_user_image/user_id=5745865499082752

### Delete User Profile Picture
curl -X DELETE http://molten-unison-112921.appspot.com/user/delete_user_image/user_id=5745865499082752

### Delete User
curl -X DELETE http://molten-unison-112921.appspot.com/user/delete/user_id=5638830484881408

### Update User
curl -H "Content-Type: application/json" -X POST -d "{\"first_name\":\"Lester\", \"last_name\":\"Nygaard\", \"email\":\"lg_killa@gmail.com\", \"phone_number\":\"1111111111\"}" http://molten-unison-112921.appspot.com/user/update/user_id=5717271485874176

### Get User Data (also returns a media link to their profile picture)
curl http://molten-unison-112921.appspot.com/user/get/user_id=5638830484881408


########### LISTING FUNCTIONS ##############
### Create Listing
curl -H "Content-Type: application/json" -X POST -d "{\"owner_id\":\"5749328048029696\", \"category_id\":\"5699257587728384\", \"name\":\"The Wire Season 1\", \"item_description\":\"Boxed DVD set.\", \"total_value\":\"40\", \"hourly_rate\":\"2\", \"daily_rate\":\"7\", \"weekly_rate\":\"15\"}" http://bygo-client-server.appspot.com/listing/create

### Add listing image
curl -X POST -F "filename=pp.jpg" -F "userfile=@C:/Users/Sayan/Desktop/lion-male-roar.jpg" http://bygo-client-server.appspot.com/listing/new_listing_image/listing_id=6243983994912768