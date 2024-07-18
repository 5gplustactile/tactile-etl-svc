"""

"""
import logging 
import requests  
from random_object_id import generate
from bson.objectid import ObjectId
import pymongo
import os
from pymongo import MongoClient
import json
import pandas as pd
import datetime
import time
from pymongo.uri_parser import parse_uri
import os
from dotenv import load_dotenv
import pandas as pd
from github import Github
from github import Auth

from pandas import json_normalize

import sys
import os
sys.path.insert(0,os.path.abspath(os.path.dirname(__file__)))

#Define current path
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

#Load env file
env_path_envFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '_env', '.env'))
load_dotenv(env_path_envFolder)


def run_get_prometheus_metrics():
    import requests
    """
        This method is responsible for running feature engineering
    """

    ct = datetime.datetime.now()

    str_container_filter_tag = os.getenv('K8_FILTER_STR')

    # get prometheus data
    post_query_url = os.getenv('PROM_URL') + '/api/v1/query?query=' + os.getenv('PROM_QUERY')
    logger.info('Get prometheus data...')
    response = requests.post(post_query_url)
    prometheus_data = json.loads(response.text)
    #logger.info(prometheus_data)
    res = pd.json_normalize(prometheus_data['data']['result'])

  

def run_get_devo_qos():
    """
        This method is responsible for sending metrics to a endpoint
    """

    import requests
    import pandas as pd
    import json
    from datetime import datetime, timedelta
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context

    url = "https://apiv2-sasr.devo.com/search/query"
    #DAG_PATH = '/opt/airflow/dags/naas_QosMonitoring_dag/queries/query_nr1477a.txt'
    #print('DAG_PATH: ', DAG_PATH)
    print(os.getenv('DAG_PATH_QOS') )
    DAG_PATH = os.getenv('DAG_PATH_QOS') + '/queries/query_nr1477a.txt' 

    # Open the file and load its contents
    with open(DAG_PATH, 'r') as file:
        payload = file.read()

    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + os.getenv('NAAS_DEVO_TOKEN'),
    'Content-Encoding': 'json'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    #print(response.text)
    # Parse the JSON response into a Python dictionary
    api_data = response.json()

    # Flatten the nested JSON structure
    df = json_normalize(api_data['object'])

    df['nr1477'] = (df['pdcpc-dl_pdcp_vol_ue_tput_qos_01__sum']+df['pdcpc-dl_pdcp_vol_ue_tput_qos_02__sum'] + \
               df['pdcpc-dl_pdcp_vol_ue_tput_qos_03__sum']+df['pdcpc-dl_pdcp_vol_ue_tput_qos_04__sum'] + \
               df['pdcpc-dl_pdcp_vol_ue_tput_qos_05__sum']+df['pdcpc-dl_pdcp_vol_ue_tput_qos_06__sum'] + \
               df['pdcpc-dl_pdcp_vol_ue_tput_qos_07__sum']+df['pdcpc-dl_pdcp_vol_ue_tput_qos_08__sum'] + \
               df['pdcpc-dl_pdcp_vol_ue_tput_qos_09__sum']+df['pdcpc-dl_pdcp_vol_ue_tput_qos_10__sum'] + \
               df['pdcpc-dl_pdcp_vol_ue_tput_qos_11__sum']+df['pdcpc-dl_pdcp_vol_ue_tput_qos_12__sum'] + \
               df['pdcpc-dl_pdcp_vol_ue_tput_qos_13__sum']+df['pdcpc-dl_pdcp_vol_ue_tput_qos_14__sum'] + \
               df['pdcpc-dl_pdcp_vol_ue_tput_qos_15__sum']+df['pdcpc-dl_pdcp_vol_ue_tput_qos_16__sum'] + \
               df['pdcpc-dl_pdcp_vol_ue_tput_qos_17__sum']+df['pdcpc-dl_pdcp_vol_ue_tput_qos_18__sum'] + \
               df['pdcpc-dl_pdcp_vol_ue_tput_qos_19__sum']+df['pdcpc-dl_pdcp_vol_ue_tput_qos_20__sum'] )/ \
               (df['pdcpc-dl_pdcp_time_ue_tput_qos_01__sum']+df['pdcpc-dl_pdcp_time_ue_tput_qos_02__sum'] + \
               df['pdcpc-dl_pdcp_time_ue_tput_qos_03__sum']+df['pdcpc-dl_pdcp_time_ue_tput_qos_04__sum'] + \
               df['pdcpc-dl_pdcp_time_ue_tput_qos_05__sum']+df['pdcpc-dl_pdcp_time_ue_tput_qos_06__sum'] + \
               df['pdcpc-dl_pdcp_time_ue_tput_qos_07__sum']+df['pdcpc-dl_pdcp_time_ue_tput_qos_08__sum'] + \
               df['pdcpc-dl_pdcp_time_ue_tput_qos_09__sum']+df['pdcpc-dl_pdcp_time_ue_tput_qos_10__sum'] + \
               df['pdcpc-dl_pdcp_time_ue_tput_qos_11__sum']+df['pdcpc-dl_pdcp_time_ue_tput_qos_12__sum'] + \
               df['pdcpc-dl_pdcp_time_ue_tput_qos_13__sum']+df['pdcpc-dl_pdcp_time_ue_tput_qos_14__sum'] + \
               df['pdcpc-dl_pdcp_time_ue_tput_qos_15__sum']+df['pdcpc-dl_pdcp_time_ue_tput_qos_16__sum'] + \
               df['pdcpc-dl_pdcp_time_ue_tput_qos_17__sum']+df['pdcpc-dl_pdcp_time_ue_tput_qos_18__sum'] + \
               df['pdcpc-dl_pdcp_time_ue_tput_qos_19__sum']+df['pdcpc-dl_pdcp_time_ue_tput_qos_20__sum'] )


    df['nr1477'] = df['nr1477'].round(2)    
    df['timestamp'] = pd.to_datetime(df['eventdate'], unit='ms')
    df['kpiName']='RanUEThroughput'
    #df['timestamp'] = df['timestamp'] + pd.Timedelta(hours=1)
    # Get current time
    current_time = datetime.now()
    print('current date', current_time)

    # Calculate the time 30 minutes ago
    time_threshold = current_time - timedelta(minutes=80)

    # Filter DataFrame to get only the rows within the last 30 minutes
    filtered_df = df[df['timestamp'] >= time_threshold].sort_values(by='timestamp')

    # Convert the datetime format to string format
    filtered_df['timestamp_str'] = filtered_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    filtered_df['nr1477'] = filtered_df['nr1477'].fillna(0)

    # Display the DataFrame with the new string format column
    print(filtered_df.columns.to_list())

    df_out= filtered_df[['timestamp_str', 'kpiName', 'GNODEB_NAME', 'NRCELL_NAME', 'GNODEBID','CELLID','nr1477']]

    DAG_PATH_DATA = os.getenv('DAG_PATH_QOS') + '/data/qos_current_data.csv'
    #df_out.to_csv('/opt/airflow/dags/naas_QosMonitoring_dag/data_nr1477.csv')
    df_out.to_csv(DAG_PATH_DATA)
    print('Result: ',df_out.head(20) )

def run_QoSsus_computation():
    """
        This method is responsible for sending metrics to a endpoint
    """
    print("QoSsus analytics computaion")

    import pandas as pd
    from pymongo import MongoClient
    from datetime import datetime

    mongo_uri = "mongodb://"+os.getenv('MONGO_HOST_USER')+":"+os.getenv('MONGO_HOST_PASS')+"@"+os.getenv('MONGO_HOST')+":"+os.getenv('MONGO_PORT')+"/"
    print(mongo_uri)
    client = pymongo.MongoClient(mongo_uri)
    db = client[os.getenv('MONGO_DB_QOS_TH')]    
    col = db[os.getenv('MONGO_COL_QOS_TH')]    
 
    df = pd.DataFrame(list(col.find())).head(50)
    print('Columns of dataframe: ', df.columns)
    print('Request QOS Throuthput Data to Nwdaf, input data: ', df.shape)
    columns = ['datetime', 'cellid', 'value']


    # Create an empty DataFrame with defined column names
    dfTh = pd.DataFrame(columns=columns)

    for index, row in df.iterrows():
        print(row['data'])
        for c in row['data']:
            timestamp_th = datetime.strptime(c['timestamp_str'], '%Y-%m-%d %H:%M:%S')
            dfTh = dfTh.append({'datetime': timestamp_th, 'cellid': c['CELLID'], 'value': c['nr1477']}, ignore_index=True)

    print('Unique cells: ', dfTh['cellid'].unique())
    DAG_PATH_DATA = os.getenv('DAG_PATH_QOS') + '/data/qos_uethroughput_data.csv'
    dfTh.to_csv(DAG_PATH_DATA)


def run_trainAndPredict():
    """
        This method is responsible for sending metrics to a endpoint
    """
    print("Train and Predict")
    import pandas as pd
    from statsmodels.tsa.arima.model import ARIMA

    DAG_PATH_DATA = os.getenv('DAG_PATH_QOS') + '/data/qos_uethroughput_data.csv'
    df = pd.read_csv(DAG_PATH_DATA, index_col=0)

    print(df.head(4))

    # Crear un diccionario para almacenar los modelos ARIMA y las predicciones
    modelos_y_predicciones = {}

    # Iterar sobre las categorías únicas
    for categoria in df['cellid'].unique():
        # Filtrar el DataFrame para obtener solo los datos de la categoría actual
        df_categoria = df[df['cellid'] == categoria]
        # Convertir el timestamp en un índice temporal
        df_categoria['timestamp'] = pd.to_datetime(df_categoria['datetime'])
        df_categoria.set_index('timestamp', inplace=True)
        
        # Entrenar el modelo ARIMA
        modelo_arima = ARIMA(df_categoria['value'], order=(5,1,0))  # Ajustar los parámetros según tu conjunto de datos
        modelo_arima_entrenado = modelo_arima.fit()
        
        # Realizar predicciones para los próximos 4 valores
        predicciones = modelo_arima_entrenado.forecast(steps=4)

        # Almacenar el modelo y las predicciones en el diccionario
        modelos_y_predicciones[categoria] = {'modelo': modelo_arima_entrenado, 'predicciones': predicciones}
        print('modelos y predicciones: ', modelos_y_predicciones)

    # Crear un DataFrame agregado para almacenar todas las predicciones
    df_predicciones_agregadas = pd.DataFrame(columns=['timestamp', 'cellid', 'predicted_value'])

    # Iterar sobre los modelos y predicciones almacenados en el diccionario
    for categoria, info in modelos_y_predicciones.items():
        # Generar un índice de fechas para las predicciones
        fechas_prediccion = pd.date_range(start=df['datetime'].max(), periods=4, freq='15T')
        print('fechas_prediccion: ', fechas_prediccion)
        
        # Crear un DataFrame temporal para almacenar las predicciones de esta categoría
        df_predicciones_categoria = pd.DataFrame({
            'timestamp': fechas_prediccion,
            'cellid': [categoria] * 4,
            'predicted_value': info['predicciones']
        })

        # Agregar las predicciones de esta categoría al DataFrame agregado
        df_predicciones_agregadas = pd.concat([df_predicciones_agregadas, df_predicciones_categoria], ignore_index=True)
    
    new_column_names = {'datetime': 'timestamp', 'value': 'predicted_value'}
    df_renamed = df.rename(columns=new_column_names)

    df_predicciones_agregadas['predicted_value'] = df_predicciones_agregadas['predicted_value'].apply(lambda x: round(x, 2))    
    print('df_pred_agg: ', df_predicciones_agregadas.shape)
    print('df_pred_agg: ', df_predicciones_agregadas.head(100))

    # Concatenating vertically
    df_all = pd.concat([df_renamed, df_predicciones_agregadas])
       
    DAG_PATH_DATA = os.getenv('DAG_PATH_QOS') + '/data/qos_uethroughput_predict.csv'
    df_predicciones_agregadas.to_csv(DAG_PATH_DATA)

def run_send_predictions():
    """
        This method is responsible for sending metrics to a endpoint
    """

    import requests
    import pandas as pd

    DAG_PATH = os.getenv('DAG_PATH_QOS') + '/data/qos_uethroughput_predict.csv' 
    df = pd.read_csv(DAG_PATH, index_col=0)

    try:
    
        def send_predictions(df):
            # defining the api-endpoint
            url = os.getenv('EVENT_INPUT_QOS_PREDICT_URL') 
            df = df.drop_duplicates()         
            data = json.loads(df.to_json(orient='records'))
            print(data)

            headers = {'Content-Type': 'application/json'}

            for i in df.index:
                data = df.to_json(orient='records')
                r = requests.post(url, 
                    data=json.dumps(data), headers=headers
                )
                print('data: ', data)
        
            logger.info('Data sending finish..')       

            return "Data sent!"
        
        logger.info('Sending_data')
        print(df.head(30))
        
        send_predictions(df)        

    except Exception as err:
        logger.exception(err)
        raise err

     
def run_send_metrics():
    """
        This method is responsible for sending metrics to a endpoint
    """

    import requests
    import pandas as pd

    DAG_PATH = os.getenv('DAG_PATH_QOS') + '/data/qos_current_data.csv' 
    df = pd.read_csv(DAG_PATH, index_col=0)

    try:
    
        def send_metrics(df):
            # defining the api-endpoint
            url = os.getenv('EVENT_INPUT_QOS_URL') 
            df = df.drop_duplicates()         
            data = json.loads(df.to_json(orient='records'))
            print(data)

            headers = {'Content-Type': 'application/json'}

            for i in df.index:
                data = df.to_json(orient='records')
                r = requests.post(url, 
                    data=json.dumps(data), headers=headers
                )
                print('data: ', data)
        
            logger.info('Data sending finish..')       

            return "Data sent!"
        
        logger.info('Sending_data')
        print(df.head(30))
        
        send_metrics(df)        

    except Exception as err:
        logger.exception(err)
        raise err

