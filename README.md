# SnipeITToTTM
 Snipe-IT To Telstra Track and Monitor(TTM), Syncs dats from TTM to Snipe-IT

# Enviroment Variables Docker
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
    'ttm_serial':'', #ttm serial number field
    'ttm_latitude':'',#ttm lastLatitude field
    'ttm_longitude':'',#ttm lastLongitude field
    'snipeit_last_known_location':'_snipeit_last_known_location_23' # Last Known Location fiedset DB Field in Snipe-IT
    }"
TTM_SERVER # URL for the TTM API
TTM_CLIENT_ID # Client ID
TTM_CLIENT_SECRET # Client Secret for O2Auth
TTM_SAVE_LOCATION # Location to save the O2Auth Temp token
SCHEDULE_RUN_EVERY_MINUTES #Number of minutes in between syncs
DEBUG # Debug logging
~~~
