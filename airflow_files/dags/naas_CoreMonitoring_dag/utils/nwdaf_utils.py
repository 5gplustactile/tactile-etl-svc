import logging 
import requests
import urllib.parse
import os
import json
import datetime

os.system("clear")

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

def nwdaf_url_request_gen(NWDAF_HOST, NWDAF_PORT, NWDAF_STARTTS, NWDAF_ENDTS, EVENT, NF_TYPE):
    # "startTs": "2023-06-01T00:00:00.000Z", "endTs": "2024-02-04T00:00:00.000Z"
    data= {
            "event-id": EVENT,
            "ana-req":{"startTs": NWDAF_STARTTS, "endTs": NWDAF_ENDTS},
            "tgt-ue":{"anyUe": True},
            "event-filter":{
                "nfTypes":[NF_TYPE]
            }
        }

    url_encoded_data = urllib.parse.urlencode(data, quote_via=urllib.parse.quote)

    url_encoded_data = url_encoded_data.replace("True", "true")
    url_encoded_data = url_encoded_data.replace("False", "false")

    url="http://"+ NWDAF_HOST + ':' + NWDAF_PORT + "/nnwdaf-analyticsinfo/v1/analytics?"+url_encoded_data.replace("%27", '%22')
    print("\ncurl -X GET '"+url+"'")

    logger.info('Get nwdaf upf data...')
    try:
        logger.info('request nwdaf data')
        response = requests.get(url)
        if response.status_code == 204:
            print(f"No content for request.")
            nwdaf_nfload_data ={}

        else:
            nwdaf_nfload_data = json.loads(response.text)
            return nwdaf_nfload_data
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        nwdaf_nfload_data = None

        return 'NWDAF Error Request'

        
def get_openNwdaf_data(NWDAF_HOST, NWDAF_PORT, NWDAF_STARTTS, NWDAF_ENDTS):
    print('Get OpenNwdaf Data')
    # Nwdaf data request
    nwdaf_nfload_data = nwdaf_url_request_gen(NWDAF_HOST,NWDAF_PORT,  NWDAF_STARTTS, NWDAF_ENDTS, 'NF_LOAD', 'UPF')
    print('NWDAF UPF1 from %s until %s : %s ' % (NWDAF_STARTTS, NWDAF_ENDTS,nwdaf_nfload_data))

    if 'nfLoadLevelInfos' in nwdaf_nfload_data: 
        nfCpuUsageUpf1= nwdaf_nfload_data['nfLoadLevelInfos'][0]['nfCpuUsage']
    else: 
        nfCpuUsageUpf1=0
    print (' Recent Cpu Load Upf1 %.2f' % (float(nfCpuUsageUpf1)) )
    nfCpuUsageUpf2 = nwdaf_url_request_gen(NWDAF_HOST,NWDAF_PORT,  NWDAF_STARTTS, NWDAF_ENDTS, 'NF_LOAD', 'UPF2')
    print('NWDAF UPF2 from %s until %s : %s ' % (NWDAF_STARTTS, NWDAF_ENDTS, nfCpuUsageUpf2))

    # Current core status considering NWDAF Info
    if nfCpuUsageUpf2:
        print('Step: Current extended U2')
        current_core = 'core-extended-u2'
    else:
        print('Step: Current default U2')
        current_core = 'core-default'

    return current_core, nfCpuUsageUpf1, nfCpuUsageUpf2
