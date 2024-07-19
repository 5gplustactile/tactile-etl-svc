

import logging 
import requests  
import pymongo
from pymongo import MongoClient
import json
import pandas as pd
import datetime
import time
import os
from dotenv import load_dotenv
import pandas as pd
from github import Github
from github import Auth

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

import sys
import os
sys.path.insert(0,os.path.abspath(os.path.dirname(__file__)))

from git_utils import repo_sync_file

def get_metric_value(list_):

    list_ = list_[1]

    return list_

def handle_def_def(cpuUniqueValueFitted,upf_extension_theslhold):
    print('************From:default , To: default')
    print('Action: DEFAULT TRAFFIC SCENARIO. NO ACTIONS.')
    print('D1 Core >   Traffic: normal  -  Status: default - Action: no actions')
    print('Current trigger : %.2f Extention Trigger: %.2f' % (cpuUniqueValueFitted,upf_extension_theslhold) )

def handle_def_ext(gh_token,gh_reponame,DAG_PATH):
    print('************From:default , To: extended')
    print('Action: HIGH TRAFFIC SCENARIO Detected!')        
    new_sce= 'sce-2u1dn'
    # Update SMF config
    print('SMF-Updating core config gitops with: nº upf=2, dnn=1, smf=1, slice=1, cell=1, tac=1 ')
    local_path = DAG_PATH + '/config-open5gs/scenario-custom-upf1dnn1-upf2dnn1/chart-smf/smf.yaml'
    git_path = '/open5gs/charts/open5gs-smf/resources/config/smf.yaml'
    entity = 'smf'
    git_branch = 'openverso'
    repo_sync_file(gh_token,gh_reponame, entity, local_path, git_path, git_branch, new_sce)

    # Update SMF Values 
    print('SMF Values core config gitops ')
    local_path = DAG_PATH + '/config-open5gs/scenario-custom-upf1dnn1-upf2dnn1/chart-smf/values.yaml'
    git_path = '/open5gs/charts/open5gs-smf/values.yaml'
    entity = 'values'
    git_branch = 'openverso'
    repo_sync_file(gh_token,gh_reponame, entity, local_path, git_path, git_branch, new_sce)

    # Update 1UPF 
    print('Values-Updating core config gitops with: nº upf=1, dnn=1, smf=1, slice=1, cell=1, tac=1 ')
    local_path = DAG_PATH + '/config-open5gs/scenario-custom-upf1dnn1-upf2dnn1/default-values.yaml'
    git_path = '/values/main-values/default-values.yaml'
    entity = 'default-values'
    git_branch = 'openverso'
    repo_sync_file(gh_token,gh_reponame, entity, local_path, git_path, git_branch, new_sce)

    data = {"svcid":"1", "status":"active-airflow"}

    # #Update NAAS API SVC Status
    # url = "http://"+ os.getenv('HOST_SVC_API')+ ":" + os.getenv('IP_SVC_API') + "/api/naasapiservices"
    # logger.info('Get naas api web svc data...')
    # response = requests.post(url,json = data)
    # if response.status_code == 200:
    #     print("POST request successful!")
    # else:
    #     print(f"POST request failed with status code: {response.status_code}")
    # naas_apisvc_data = json.loads(response.text)
    # logger.info('Update status Service data...')
    # logger.info(naas_apisvc_data)
            
def handle_ext_ext():
    print('************From:extended , To: extended')
    print('E2 Core >   Traffic: high  -  Status: extended - Action: no action')

def handle_ext_def(gh_token,gh_reponame, DAG_PATH,nfCpuUsageUpf1, nfCpuUsageUpf2,nfCpuNoUsage):
    print('************From:extended , To: default')
    print('Action: DEFAULT TRAFFIC SCENARIO.')
    print('E1 Core >   Traffic: normal  -  Status: extended - Action: block traffic to upf 2')
    new_sce= 'default'
    print("CPU UPF usage below threshold.")
    print('Checking if additional UPF can be deleted.')

    #FIRST STEP BLOCK
    # Update SMF config
    print('SMF-Updating core config gitops with: nº upf=2, dnn=1, smf=1, slice=1, cell=1, tac=1 ')
    local_path = DAG_PATH + '/config-open5gs/scenario-default/chart-smf/smf.yaml'
    git_path = '/open5gs/charts/open5gs-smf/resources/config/smf.yaml'
    entity = 'smf'
    git_branch = 'openverso'
    repo_sync_file(gh_token,gh_reponame, entity, local_path, git_path, git_branch, new_sce)           

    # Reconfigure SMF to Block admitting traffic to UPF2
    print('Values-Updating core config gitops with: nº upf=2, dnn=1, smf=1, slice=1, cell=1, tac=1 ')
    local_path = DAG_PATH + '/config-open5gs/scenario-default/chart-smf/values.yaml'
    git_path = '/open5gs/charts/open5gs-smf/values.yaml'
    entity = 'values'
    git_branch = 'openverso'
    repo_sync_file(gh_token,gh_reponame, entity, local_path, git_path, git_branch, new_sce)

    
    #   wait until traffic is 0 or empty        
    if nfCpuUsageUpf2 < float(nfCpuNoUsage):
        print('Core >   Traffic: normal  -  Status: extended - Action: confirmed eliminate upf2')
        # Update UPF Config
        print('Current UPF1 Cpu load: %.2f and Cpu UPF2 %.2f' % (100*nfCpuUsageUpf1,100*nfCpuUsageUpf2))
        print('Minimum traffic in UPF2...Delete UPF2')
        local_path = DAG_PATH + '/config-open5gs/scenario-default/default-values.yaml'
        git_path = '/values/main-values/default-values.yaml'
        entity = 'default-values'
        git_branch = 'openverso'
        repo_sync_file(gh_token,gh_reponame, entity, local_path, git_path, git_branch, new_sce)
    else:
        print('Additional UPF can not be undeploy because still has traffic routing...')

def handle_to_empty(gh_token,gh_reponame, DAG_PATH):
    print('************From: , To: empty')

    # Update Empty Core Config 
    print('Updating core config gitops with: upf=1, dnn=1, smf=1, slice=1, cell=1, tac=1 ')
    local_path = DAG_PATH + '/config-open5gs/scenario-empty/default-values.yaml'
    git_path = '/values/main-values/default-values.yaml'
    entity = 'default-values'
    repo_sync_file(gh_token,gh_reponame, entity, local_path, git_path, new_sce)

def handle_svc_validation(DAG_PATH):
    print('Handle validation')
    print('Check if dynamic-deployment is an available service.')
    url = ("http://%s:%s/api/svc/v1/dynamic-deployment" % (os.getenv('HOST_SVC_API'), os.getenv('IP_SVC_API')) )
    logger.info('Get naas svc data...')
    response = requests.get(url)
    naas_svc_data = json.loads(response.text)
    logger.info(naas_svc_data)

    url = ("http://%s:%s/api/naasapiservices" % (os.getenv('HOST_WEB_API'), os.getenv('IP_WEB_API')) )  
    logger.info('Post naas api web svc data...')
    response = requests.get(url)  
    naas_apisvc_data = json.loads(response.text)
    naasapiservices = naas_apisvc_data['naasapiservices']

    # Filter python objects with list comprehensions
    dynamic_svc = [x for x in naasapiservices if x['name'] == 'dynamic-deployment'][0] 
    core_status = dynamic_svc['currentnetworktype']
