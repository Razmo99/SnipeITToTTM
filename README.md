# SnipeITToTTM
 Snipe-IT To Telstra Track and Monitor(TTM), Syncs data from TTM to Snipe-IT.

 ## How it works
 1. Connects to Telstra Track Monitor and retrieves all trackers with a friendly name.
 1. Looks up each tracker by serial number in Snipe-IT. If a match is found, it then appends a dictionary with both devices to a match list.
 1. The match list is then iterated over.
    1. Custom fields for each tracker are iterated over and matched with the inputted [fieldsets](#match_data) to build a payload.
 1. The tracker is then patched in Snipe-IT.
    1. If the patch is successful, a check will be made to see if the tracker is checked out to another asset.\
    _If this returns true the checked-out to asset will be patched with the map url assuming it has the correct fieldsets._

## Requirements
 - Telstra Track Monitor
    - Trackers
    - API Key
 - Snipe-IT
    - API Key
    - Assets to track

## Installing
1. Download the Repo and place it on your docker host.
1. Create a new file next to the "docker-compose.yml" called ".env" enter in all the required [docker environment variables](#docker-environment-variables)
1. `docker-compose up --build`
   1. Don't add the `-d` flag so you can see if any errors occur on startup.\
   If it starts successfully then stop and start the container again in detached mode.

## Docker environment variables
- SNIPEIT_SERVER {string} # URL to the Snipe-IT Server ***Required**
- SNIPEIT_TOKEN {string} # API Token for the Snipe-IT Server ***Required**
- MATCH_DATA {string} # Refer to [link](#match_data) ***Required**
- TTM_SERVER {string} # URL for the TTM API ***Required**
- TTM_CLIENT_ID {string} # Client ID ***Required**
- TTM_CLIENT_SECRET {string} # Client Secret for O2Auth ***Required**
- TTM_SAVE_LOCATION {string} # Location to save the O2Auth Temp token
   - This can be just a file name i.e "ttm_token.json" or the full directory path "/app/storage/ttm_token.json"
- SCHEDULE_RUN_EVERY_MINUTES {int} #Number of minutes in between syncs
   - If unspecified defaults to 30
- DEBUG {bool} # Debug logging
- LOG_SAVE_LOCATION {string} # location to save log file
   - This can be just a file name i.e "snipeit_to_ttm.log" or the full directory path "/app/storage/snipeit_to_ttm.log"

_If no "save locations" are specified default names will be used and files will be placed in the working dir of the app_   

### MATCH_DATA
A dictionary that is passed to the app.\
It must be encased in **double quotes** so its parsed correctly.\
It contains the following keys;
 - fieldsets -- {list}
    - Contains dictionaries that match up Snipe-IT Custom Fields to ttm fields
      
      The dictionary should look like below:
      ~~~python
      {'snipeit':'_snipeit_ttm_lasttemperature_9','ttm':'lasttemperature'} #This just an example
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

## Dockerfile
Slightly modified version of the dockerfile layed out [here](https://www.kevin-messer.net/how-to-create-a-small-and-secure-container-for-your-python-applications/)\
