import os,pathlib
import logging
import logging.handlers
import schedule
import time
import datetime
import json
from conf_mgr import conf_mgr
import TelstraTrackMonitorAPI
import SnipeITAPI
from ast import literal_eval

def main():
    #Initialise Config
    conf = conf_mgr()
    #if the config has sections and it passes the check config fun continue
    if conf.check_conf():
        #Initialise the TelstraTrackMonitorAPI.TokenManager with the fields pulled from the config
        ttm_token = TelstraTrackMonitorAPI.TokenManager(
            server=conf.config['ttm_auth']['server'],
            client_id=conf.config['ttm_auth']['client_id'],
            client_secret=conf.config['ttm_auth']['client_secret'],
            save_location=conf.config['ttm_auth']['save_location']
        )
        #Try to load any stored tokens
        ttm_token.load_token()
    else:
        logger.exception('Did not find expected headers in config.')

    default_match_data="{'fieldsets':[],'ttm_serial':'','ttm_latitude':'','ttm_longitude':'','snipeit_last_known_location':''}"
    match_data=literal_eval(os.getenv('MATCH_DATA',default_match_data))

    if not match_data.get('ttm_serial') or not match_data.get('ttm_latitude') or not match_data.get('ttm_longitude') or not match_data.get('snipeit_last_known_location'):
        logger.exception('One or more of the following are missing: ttm_serial, ttm_latitude, ttm_longitude, snipeit_last_known_location these are required to continue!')
    else:
        if ttm_token.update_token():
            # retreive ttm devices
            with TelstraTrackMonitorAPI.Sessions(ttm_token.server,ttm_token.access_token) as TTM:
                ttm_devices=TTM.devices_get({'$filter':'not(deviceFriendlyName eq null)'}).json()
            #Create aSnipe-IT Sessions
            with SnipeITAPI.Sessions(server=conf.config['snipeit_auth']['server'],token=conf.config['snipeit_auth']['token']) as snipeit_session:
                #List to stick match results
                snipeit_device_matches=[]
                #Iterate over ttm devices
                for ttm_device in ttm_devices:
                    #Search for the TTM Device in Snipe-IT based on serial #
                    snipe_device_search=snipeit_session.assets_get_byserial(serial=ttm_device['serialNumber']).json()
                    #Iterate over returned rows, only really expect one, but meh.
                    for snipeit_device in snipe_device_search['rows']:
                        #Check the serials match again because multiple rows; this is mostly redundant.
                        if snipeit_device['serial'] == ttm_device['serialNumber']:
                            snipeit_device_matches.append({
                                'snipeit':snipeit_device,
                                'ttm':ttm_device
                            })
                        else:
                            logger.debug('Failed to find device in Snipe-IT { SN: '+ttm_device['serialNumber']+' }')
            
                #Iterate over Snipe-IT Matches
                for snipeit_device_match in snipeit_device_matches:
                    patch_data={}
                    #Find all custom fields of the snipe-it device and stick em in a list
                    snipe_device_custom_fields=[]
                    [snipe_device_custom_fields.append(value['field']) for (key,value) in snipeit_device_match['snipeit']['custom_fields'].items()]                    
                    #Iterate over the fieldsets and match em up
                    for custom_fieldset in match_data['fieldsets']:
                        #Only add patch data for fields we know the asset has
                        if custom_fieldset in snipe_device_custom_fields:
                            patch_data[custom_fieldset['snipeit']]=snipeit_device_match['ttm'][custom_fieldset['ttm']]
                    #Patch data to tracker in Snipe-IT
                    if patch_data:
                        patch_operation = snipeit_session.asset_patch(snipeit_device_match['snipeit']['id'],json.dumps(patch_data))
                        #If the patch succeeded and the tracker is checked out to another asset
                        if patch_operation.ok:
                            #Try get the id of the assigned_ to asset and patch the google maps url to it                        
                            try:
                                assigned_to_id = None
                                assigned_to_id = snipeit_device_match['snipeit']['assigned_to']['id'] if snipeit_device_match['snipeit']['assigned_to']['type']=='asset' else None
                            except KeyError:
                                logger.info(snipeit_device_match['snipeit']['name']+' is not checked out to another asset')
                            except TypeError:
                                logger.info(snipeit_device_match['snipeit']['name']+' is not checked out to another asset')
                            else:
                                if not assigned_to_id is None:
                                    url_patch_data={
                                            match_data['snipeit_last_known_location']:"http://maps.google.com/maps?q={0},{1}".format(snipeit_device_match['ttm']["lastLatitude"],snipeit_device_match['ttm']["lastLongitude"])
                                        }
                                    patch_assigned_to=snipeit_session.asset_patch(
                                        assigned_to_id,
                                        json.dumps(url_patch_data)
                                        )
        else:
            logger.exception('Failed to Sync, unable to update tokens')

if __name__ == "__main__":
    #Change the current working directory to be the parent of the main.py
    working_dir=pathlib.Path(__file__).resolve().parent
    os.chdir(working_dir)
    print("changed working dir to: "+str(working_dir))
    #Initialise logging
    logging_format='%(asctime)s - %(levelname)s - [%(module)s]::%(funcName)s() - %(message)s'
    log_name = os.getenv("LOG_SAVE_LOCATION",'snipeit_to_ttm.log')
    rfh = logging.handlers.RotatingFileHandler(
    filename=log_name, 
    mode='a',
    maxBytes=5*1024*1024,
    backupCount=2,
    encoding='utf-8',
    delay=0
    )
    console=logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.basicConfig(
        level=logging.DEBUG,
        format=logging_format,
        handlers=[rfh,console]
    )
    
    logger = logging.getLogger(__name__)
    def job():
        logger.info('------------- Starting Session -------------')
        start=time.time()
        main()
        end=time.time()
        logger.info('Synced in:'+str(end-start)+' Second(s)')
        logger.info('------------- Finished Session -------------')
    job()
    #run_every = os.getenv('SCHEDULE_RUN_EVERY_MINUTES',30)
    #logger.info('Syncing every: '+run_every+' minutes')
    #schedule.every(int(run_every)).minutes.do(job)
    #while 1:
    #    schedule.run_pending()
    #    time.sleep(1)