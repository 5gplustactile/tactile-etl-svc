"""

"""
import logging 
import requests  
import pymongo
import os
from pymongo import MongoClient
import json
import pandas as pd
import datetime
import time
from pymongo.uri_parser import parse_uri
from dotenv import load_dotenv
import pandas as pd
from github import Github
from github import Auth
import numpy as np


import sys
import os
sys.path.insert(0,os.path.abspath(os.path.dirname(__file__)))

#Define current path
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

#Load env file
env_path_envFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '_env', '.env'))
load_dotenv(env_path_envFolder)

from utils.nwdaf_utils import nwdaf_url_request_gen, get_openNwdaf_data
from utils.git_utils import repo_sync_file
from utils.scenario_utils import get_metric_value, handle_def_def, handle_def_ext, handle_ext_ext, handle_ext_def, handle_to_empty, handle_svc_validation


# TASK
def run_get_prometheus_metrics():
    import requests
    """
        This method is responsible for running feature engineering
    """
    ct = datetime.datetime.now()

    str_container_filter_tag = os.getenv('K8_FILTER_STR')

    # get prometheus data
    post_query_url = os.getenv('PROM_URL') + ':' + os.getenv('PROM_PORT') + '/api/v1/query?query=' + os.getenv('PROM_QUERY')
    logger.info('Get prometheus data updated...', post_query_url)
    response = requests.post(post_query_url)
    prometheus_data = json.loads(response.text)
    #logger.info(prometheus_data)
    res = pd.json_normalize(prometheus_data['data']['result'])

  
    # # parse prometheus data
    # # get metric value and load dataframe 
    df = pd.DataFrame(res)
    print('Check df columns: ', df.columns)

    df['metric.value'] = df['value'].apply(get_metric_value) 
    #print('Metricas df: ', df[['metric.pod','metric.value']].head(300))
    df['metric.container']=df['metric.container'].fillna('No info')
    filtered_df = df[df["metric.container"].str.contains("upf")]
    print('Metricas df filtered: ', filtered_df[['metric.pod','metric.value']].head(300))
    df = df[df['metric.container'].notnull()] # contains no missing values 
    df5g = df[df['metric.container'].str.contains(str(str_container_filter_tag))] # filter open5gs containers]
    df5g['timestamp'] = ct
    df5g = df5g.filter(items=['timestamp','metric.container','metric.value']).set_index('metric.container')

    logger.info('Save metric data.')
    logger.info('Metrics 5g to send: ', df5g.head(50))

    try:
        # # save locally prometheus data
        df5g.to_csv('k8-metrics' + str_container_filter_tag + '.csv')
        logging.info('Saved metric data to local.')

    except:
        logging.info('Error in local saving of metrics.')

# TASK
def run_send_metrics():
    """
        This method is responsible for sending metrics to a endpoint
    """

    import requests
    import pandas as pd

    str_container_filter_tag ='open5gs'
    df = pd.read_csv('k8-metrics' + str_container_filter_tag + '.csv').set_index('metric.container')

    #Add sample value
    cpu_load_delta_min = float(os.getenv('CPU_LOAD_DELTA_MIN'))
    cpu_load_delta_max = float(os.getenv('CPU_LOAD_DELTA_MAX'))
    df['metric.value'] += np.random.uniform(cpu_load_delta_min, cpu_load_delta_max, size=len(df)).round(1)
    print('Added sample random value...')
    
    try:
    
        def send_metrics(df):
            # defining the api-endpoint
            url = os.getenv('EVENT_INPUT_COREMETRIC_ANALYTICS_URL') 
            df = df.drop_duplicates()         
            data = json.loads(df.to_json(orient='index'))
            print(data)

            headers = {'Content-Type': 'application/json'}

            for i in df.index:
                data = df.to_json()
                r = requests.post(url, 
                    data=json.dumps(data), headers=headers
                )
                #print(r.text)
                #logger.info(r.text)   
            logger.info('Data sending finish..')       

            return "Data sent!"
        
        logger.info('Sending_data')
        print(df.head(30))
        
        send_metrics(df)        

    except Exception as err:
        logger.exception(err)
        raise err

# TASK
def run_sendToGit():
    """
        This method is responsible for sending metrics to a endpoint
    """

    from datetime import datetime, timedelta
    import os

    # Get the current timestamp
    current_timestamp = datetime.utcnow()
    # Format the timestamp into ISO 8601 format
    current_iso_timestamp = current_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    print(current_iso_timestamp)

    mongo_uri = "mongodb://" + os.getenv('MONGO_HOST_USER') + ":" + os.getenv('MONGO_HOST_PASS') + "@" + os.getenv('MONGO_HOST_PASS') + "MONGO_HOST" + ":" + os.getenv('MONGO_HOST_PORT') + "/"
    client = pymongo.MongoClient(mongo_uri)
    gh_token = os.getenv('GH_TOKEN')
    gh_reponame = os.getenv('GH_REPO')
    NWDAF_HOST = os.getenv('NWDAF_HOST')
    NWDAF_PORT = os.getenv('NWDAF_PORT')
    NWDAF_STARTTS = os.getenv('NWDAF_STARTTS')
    NWDAF_ENDTS = current_iso_timestamp # "2024-02-12T00:00:00.000Z"
    DAG_PATH= os.getenv('DAG_PATH')
    nfCpuNoUsage= os.getenv('NF_LOAD_NO_USAGE')

    print('------STEP %s)-- Repo sync name: %s ' % (0, gh_reponame))

    print('------STEP %s)-- %s ' % (1, 'REQUEST NWDAF DATA'))
    
    current_core, nfCpuUsageUpf1, nfCpuUsageUpf2 = get_openNwdaf_data(NWDAF_HOST, NWDAF_PORT, NWDAF_STARTTS, NWDAF_ENDTS)
    
    print('------STEP %s)-- %s ' % (2, current_core))

    # Validate service is registered in NAAS BO
    #handle_svc_validation()

    print('------STEP %s)-- %s ' % (3, 'CORE NETWORK ANALYTIC METRICS'))
    # ALGORITH PARAMETERS
    cpuPercRange = float(os.getenv('CPU_THRESHOLD_RATE'))
    cpuUniqueValueFitted= (nfCpuUsageUpf1 ) * (1-float(cpuPercRange))  
    upf_extension_theslhold = float(os.getenv('UPF_EXTENSION_THRESHOLD'))

    # THRESHOLD CONDITIONS
    print('----------------------------DYNAMIC DEPLOYMENT THRESHOLD CONDITIONS----------------------------')
    print('Traffic load analysis. Threshold defined to extend UPF: %.2f  with a adjust range: %.2f ' % (upf_extension_theslhold, cpuPercRange) )

    
    if current_core == 'core-extended-u2':
        print('////////////////////Detected Core extended u2')
        if 'nfLoadLevelInfos' in nfCpuUsageUpf2: 
            nfCpuUsageUpf2= nfCpuUsageUpf2['nfLoadLevelInfos'][0]['nfCpuUsage'] 
        else: 
            nfCpuUsageUpf2=0

        print ('CPU Load Extended: UPF1 %.2f' % nfCpuUsageUpf1 ) 
        print ('CPU Load Extended: UPF2 %.2f' % nfCpuUsageUpf2 ) 
        cpuCombThresholdLimit= (nfCpuUsageUpf1 + nfCpuUsageUpf2) * (1-cpuPercRange)
        print('Extended: Combinated Trigger point %.2f  and current value:  %.2f' % (cpuCombThresholdLimit, upf_extension_theslhold) )

        print('Extended core analysis')
        if ((cpuCombThresholdLimit <= upf_extension_theslhold) and current_core=='core-extended-u2'):

            handle_ext_def(gh_token,gh_reponame, DAG_PATH,nfCpuUsageUpf1, nfCpuUsageUpf2, nfCpuNoUsage) 
      
        if ((cpuCombThresholdLimit > upf_extension_theslhold) and current_core=='core-extended-u2'): 

            handle_ext_ext()
               
    else: #core-default
        print('////////////////////Detected Core Default. Check actions.')
        cpuCombThresholdLimit=99
        print ('Default: UPF1 %.2f' % nfCpuUsageUpf1 ) 
        print ('Default: Unique Trigger point: %.2f ' % cpuUniqueValueFitted )
        print ('Detected Default core analysis')
        print ('Default: cpuUniqueValueFitted', cpuUniqueValueFitted)
        print ('Default: upf_extension_theslhold', upf_extension_theslhold)

        if ((cpuUniqueValueFitted <= upf_extension_theslhold) and current_core=='core-default'):

            handle_def_def(cpuUniqueValueFitted,upf_extension_theslhold)         

        if ((cpuUniqueValueFitted > upf_extension_theslhold) and current_core=='core-default'):   

            handle_def_ext(gh_token, gh_reponame, DAG_PATH)        
                      
        else:            
            print('No actions needed.')

# TASK   
def run_CoreMetric_computation():
    """
        This method is responsible for sending metrics to a endpoint
    """
    print("Core analytics computation")

    import pandas as pd
    from pymongo import MongoClient
    from datetime import datetime

    mongo_uri = "mongodb://"+os.getenv('MONGO_HOST_USER')+":"+os.getenv('MONGO_HOST_PASS')+"@"+os.getenv('MONGO_HOST')+":"+os.getenv('MONGO_PORT')+"/"
    print(mongo_uri)
    client = pymongo.MongoClient(mongo_uri)
    db = client[os.getenv('MONGO_DB_COREMETRIC')]    
    col = db[os.getenv('MONGO_COL_COREMETRIC')]   

    df0 = pd.DataFrame(list(col.find())) 
    print('df: ', df0.head())
 
    df = pd.DataFrame(list(col.find())).sort_values(by='createdAt', ascending=False).head(49)
    df_sorted = df[['createdAt','data']]
    print ('Core Metrics for training: ', df_sorted.head())
    print('Columns of dataframe: ', df.columns)
    print('Request Core Metric Data to Nwdaf, input data: ', df.shape)
    
    columns = ['datetime', 'core_category', 'value']


    # Create an empty DataFrame with defined column names
    dfTh = pd.DataFrame(columns=columns)

    for index, row in df.iterrows():
        print(row['data']['timestamp'])
        print(row['data']['metric.value'])

        catList=['open5gs-amf','open5gs-ausf','open5gs-bsf','open5gs-nrf','open5gs-nssf','open5gs-pcf','open5gs-smf','open5gs-upf']
        for cat in catList:
            print('Category: ', cat)
            timestamp_th = datetime.strptime(row['data']['timestamp'][cat], '%Y-%m-%d %H:%M:%S.%f')
            core_value = row['data']['metric.value'][cat]
                
            dfTh = dfTh._append({'datetime': timestamp_th, 'core_category': cat, 'value': core_value}, ignore_index=True)
    print('dfTh:', dfTh)

    print('Unique cells: ', dfTh['core_category'].unique())
    DAG_PATH_DATA = os.getenv('DAG_PATH_CORE') + '/data/core_nfload_data.csv'
    dfTh.to_csv(DAG_PATH_DATA)

# TASK
def run_trainAndPredict():
    """
        This method is responsible for running feature engineering
    """

    print('Train and predict..')

    import pandas as pd
    from statsmodels.tsa.arima.model import ARIMA

    DAG_PATH_DATA = os.getenv('DAG_PATH_CORE') + '/data/core_nfload_data.csv'
    df = pd.read_csv(DAG_PATH_DATA, index_col=0)

    print(df.head(4))

    # Crear un diccionario para almacenar los modelos ARIMA y las predicciones
    modelos_y_predicciones = {}

    # Iterar sobre las categorías únicas
    for categoria in df['core_category'].unique():
        # Filtrar el DataFrame para obtener solo los datos de la categoría actual
        df_categoria = df[df['core_category'] == categoria]
        # Convertir el timestamp en un índice temporal
        df_categoria['timestamp'] = pd.to_datetime(df_categoria['datetime'])
        df_categoria.set_index('timestamp', inplace=True)
        
        # Entrenar el modelo ARIMA
        modelo_arima = ARIMA(df_categoria['value'], order=(5,1,0))  # Ajustar los parámetros según tu conjunto de datos
        modelo_arima_entrenado = modelo_arima.fit()
        
        # Realizar predicciones para los próximos 4 valores
        predicciones = modelo_arima_entrenado.forecast(steps=1)

        # Almacenar el modelo y las predicciones en el diccionario
        modelos_y_predicciones[categoria] = {'modelo': modelo_arima_entrenado, 'predicciones': predicciones}
        #print('modelos y predicciones: ', modelos_y_predicciones)

    # Crear un DataFrame agregado para almacenar todas las predicciones
    df_predicciones_agregadas = pd.DataFrame(columns=['timestamp', 'core_category', 'predicted_value'])

    # Iterar sobre los modelos y predicciones almacenados en el diccionario
    for categoria, info in modelos_y_predicciones.items():
        # Generar un índice de fechas para las predicciones
        fechas_prediccion = pd.date_range(start=df['datetime'].max(), periods=1, freq='15T') #steps
        print('fechas_prediccion: ', fechas_prediccion)
        
        # Crear un DataFrame temporal para almacenar las predicciones de esta categoría
        df_predicciones_categoria = pd.DataFrame({
            'timestamp': fechas_prediccion,
            'core_category': [categoria] * 1, #steps
            'predicted_value': info['predicciones']
        })

        # Agregar las predicciones de esta categoría al DataFrame agregado
        df_predicciones_agregadas = pd.concat([df_predicciones_agregadas, df_predicciones_categoria], ignore_index=True)

    print('predicciones agregadas: ', df_predicciones_agregadas.head(30))
    
    new_column_names = {'datetime': 'timestamp', 'value': 'predicted_value'}
    df_renamed = df.rename(columns=new_column_names)

    df_predicciones_agregadas['predicted_value'] = df_predicciones_agregadas['predicted_value'].apply(lambda x: round(x, 2))    
    print('df_pred_agg: ', df_predicciones_agregadas.shape)
    print('df_pred_agg: ', df_predicciones_agregadas.head(100))

    # Concatenating vertically
    df_all = pd.concat([df_renamed, df_predicciones_agregadas])
       
    DAG_PATH_DATA = os.getenv('DAG_PATH_CORE') + '/data/core_nfload_predict.csv'
    df_predicciones_agregadas.to_csv(DAG_PATH_DATA)

# TASK
def run_send_core_predictions():
    """
        This method is responsible for sending metrics to a endpoint
    """
    print("Core predictions")

    import requests
    import pandas as pd
    str_container_filter_tag ='open5gs'
  
    DAG_PATH_DATA = os.getenv('DAG_PATH_CORE') + '/data/core_nfload_predict.csv'
    df = pd.read_csv(DAG_PATH_DATA, index_col=0)
    #df['index_pred']= (df['timestamp'] + '_' + df['core_category'])
    #df.set_index("index_pred", inplace=True)
    print('ff', df)

    try:
        def send_core_predictions(df):
            # defining the api-endpoint
            url = os.getenv('EVENT_INPUT_COREMETRIC_PREDICT_URL') 
            df = df.drop_duplicates()         
            df.set_index("core_category", inplace=True)
            data = json.loads(df.to_json(orient='index'))
            print(data)

            headers = {'Content-Type': 'application/json'}

            for i in df.index:
                data = df.to_json()
                r = requests.post(url, 
                    data=json.dumps(data), headers=headers
                ) 
                logger.info(r.text)
            logger.info('Data sending finish..')       
            

            return "Data sent!"
        
        logger.info('Sending_data')                
        send_core_predictions(df)        

    except Exception as err:
        logger.exception(err)
        raise err
