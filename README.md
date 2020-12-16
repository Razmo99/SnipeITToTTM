# SnipeITToTTM
 Snipe-IT To Telstra Track and Monitor(TTM), Syncs data from TTM to Snipe-IT.

 # How it works

 1. Connects to Telstra Track Monitor and retrieves all trackers with a friendly name.
 1. Looks up each tracker by serial number in Snipe-IT. If a match is found, it then appends a dictionary with both devices to a match list.
 1. The match list is then iterated over.
    1. Custom fields for each tracker are iterated over and matched with the inputted `fieldsets` to build a payload.
 1. The tracker is then patched in Snipe-IT.
    1. If the patch is successful, a check will be made to see if the tracker is checked out to another asset.\
    _If this returns true the checked-out to asset will be patched with the map url assuming it has the correct field set._

# Requirements

 - Telstra Track Monitor
    - Trackers
    - API Key
 - Snipe-IT
    - API Key
    - Assets to track

# Installing
Download the Repo and place it on your docker host.
## .env file
Create a new file next to the "docker-compose.yml" called ".env" enter in all the required environment variables



# Docker environment variables
~~~
SNIPEIT_SERVER # URL to the Snipe-IT Server
SNIPEIT_TOKEN # API Token for the Snipe-IT Server
MATCH_DATA = "{
    'fieldsets':[
                    {
                    'snipeit':'',#FieldSet "DB Field" in Snipe-IT
                    'ttm':''#ttm field
                    },
                    {...}#Repeat to match more fields
                ],
    'ttm_serial':'', #ttm serialNumber field
    'ttm_latitude':'',#ttm lastLatitude field
    'ttm_longitude':'',#ttm lastLongitude field
    'snipeit_last_known_location':'_snipeit_last_known_location_23' # Last Known Location fieldset DB Field in Snipe-IT
    }"
TTM_SERVER # URL for the TTM API
TTM_CLIENT_ID # Client ID
TTM_CLIENT_SECRET # Client Secret for O2Auth
TTM_SAVE_LOCATION # Location to save the O2Auth Temp token
SCHEDULE_RUN_EVERY_MINUTES #Number of minutes in between syncs
DEBUG # Debug logging
LOG_SAVE_LOCATION # location to save log file
~~~
## MATCH_DATA
A dictionary that is passed to the app.\
It must be encased in **double quotes** so its parsed correctly.\
It contains the following keys;
 - fieldsets -- {list}
    - Contains dictionaries that match up Snipe-IT Custom Fields to ttm fields
      
      The dictionary should look like below:
      ~~~python
      {'snipeit':'_snipeit_XXXXXXX_X','ttm':'XXXXXXXX'}
       ~~~
      "snipeit" being the "Custom Field" in Snipe-IT and "ttm" being the matching value in "Telstra Track Monitor"\
      _Add as many dictionaries and you want to match fields._

 - ttm_serial -- {string}
    - A field that will be used as the TTM devices serial number, as of now it should be "**serialNumber**"
 - ttm_latitude -- {string}
    - A field that will be used to construct the map url, as of now it should be "**lastLatitude**"
 - ttm_longitude -- {string}
    - A field that will be used to construct the map url, as of now it should be "**lastLongitude**"
 - snipeit_last_known_location -- {string}
    - A "Custom Field" in Snipe-IT to patch the map url into. This can be found under:\
    `Settings > Custom Fields > DB Field` it should look similar to > `_snipeit_customfieldname_number`\
    _This field is used when a tracker is checked out to another asset._