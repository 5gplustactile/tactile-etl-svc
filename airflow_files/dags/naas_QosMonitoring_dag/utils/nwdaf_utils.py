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
        response = requests.get(url)
        nwdaf_nfload_data = json.loads(response.text)

        return nwdaf_nfload_data
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        nwdaf_nfload_data = None

        return nwdaf_nfload_data

