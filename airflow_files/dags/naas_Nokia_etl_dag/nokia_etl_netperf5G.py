import paramiko
import pandas as pd
import io
import time
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv

import sys
import os
sys.path.insert(0,os.path.abspath(os.path.dirname(__file__)))

env_path_envFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '_env', '.env'))
load_dotenv(env_path_envFolder)

def insert_or_update_dataframe_to_mongo(df):
    # Conectar a la base de datos MongoDB
    #uri= f"mongodb://{os.getenv("MONGO_HOST_USER")}:{os.getenv("MONGO_HOST_PASS")}@{os.getenv("MONGO_HOST_URL")}:{os.getenv("MONGO_HOST_PORT")}/"
    
    uri = "mongodb://"+os.getenv('MONGO_HOST_USER')+":"+os.getenv('MONGO_HOST_PASS')+"@"+os.getenv('MONGO_HOST')+":"+os.getenv('MONGO_PORT')+"/"
    print(uri)

    client = MongoClient(uri)
    db = client[os.getenv("MONGO_DB_COREMETRIC")]
    collection = db[os.getenv("MONGO_COL_5G_NETPERF")]

    # Reorganizar el DataFrame en la estructura deseada
    grouped = df.groupby('eventdate')
    for eventdate, group in grouped:
        data = []
        for index, row in group.iterrows():
            data.append(row.to_dict())

        document = {"eventdate": eventdate, "data": data}
        filter_query = {"eventdate": eventdate}
        update_query = {"$set": document}
        collection.update_one(filter_query, update_query, upsert=True)
        
    print("DataFrame inserted or updated in MongoDB successfully.")

def download_clean_concatenate_files(hostname, port, username, password, private_key, remote_folder, start_date):
    # Crear una instancia de cliente SSH
    client = paramiko.SSHClient()

    # Configurar la política para aceptar las claves SSH automáticamente
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    data_frames = []

    try:
        # Conectar al servidor SFTP
        client.connect(hostname, port, username, password, key_filename=private_key)

        # Crear una instancia de cliente SFTP dentro de la conexión SSH
        sftp_client = client.open_sftp()

        # Obtener lista de archivos en la carpeta remota
        files = sftp_client.listdir(remote_folder)
        formato = '%Y-%m-%d_%H-%M'

        # Convertir la cadena a datetime
        ultimo_eventdate = datetime.strptime(start_date, formato)
        
        fecha_actual = datetime.now().date() + timedelta(hours=2)
        
        while ultimo_eventdate.date() != fecha_actual:
            fecha_formateada = ultimo_eventdate.strftime('%Y-%m-%d')
            existe_fichero = False

            for fichero in files:
                if fichero.startswith(fecha_formateada):
                    existe_fichero = True
                    fichero_encontrado = fichero
                    break
            
            if existe_fichero:
                stime = time.time()
                remote_path = f"{remote_folder}/{fichero_encontrado}"
            
                # Descargar el archivo y leerlo como un DataFrame de pandas
                with sftp_client.file(remote_path) as file:
                    # Leer el contenido del archivo
                    content = file.read()

                if content:
                    # Convertir contenido a un DataFrame de pandas
                    df = pd.read_csv(io.BytesIO(content)) 

                    # Eliminar filas con NaN y duplicados
                    df['eventdate'] = pd.to_datetime(df['eventdate'])
                    df_cleaned = df.dropna().sort_values(by='eventdate', ascending=True)
                    data_frames.append(df_cleaned)

                    etime = time.time()  # Capturar el tiempo de finalización
                    execution_time = etime - stime
                    # print(f"Archivo '{file}' descargado, limpiado y almacenado en la lista. {execution_time} segundos")

                    ultimo_eventdate = ultimo_eventdate + timedelta(hours=24)
                
                else:
                    print(f"No se pudo descargar el archivo '{file}' desde SFTP.")
            else:
                print(f"No existe ningún fichero que contenga la fecha {fecha_formateada}.")
                ultimo_eventdate = ultimo_eventdate + timedelta(hours=24)

        stime = time.time()
        remote_path = f"{remote_folder}/{sorted(files)[-1]}"
    
        # Descargar el archivo y leerlo como un DataFrame de pandas
        with sftp_client.file(remote_path) as file:
            # Leer el contenido del archivo
            content = file.read()

        if content:
            # Convertir contenido a un DataFrame de pandas
            df = pd.read_csv(io.BytesIO(content)) 

            # Eliminar filas con NaN y duplicados
            df['eventdate'] = pd.to_datetime(df['eventdate'])
            df_cleaned = df.sort_values(by='eventdate', ascending=True)
            data_frames.append(df_cleaned)

            etime = time.time()  # Capturar el tiempo de finalización
            execution_time = etime - stime
            
        sftp_client.close()
        client.close()

    except Exception as e:
        print(f"Error al descargar archivos desde SFTP: {e}")

    # Concatenar todos los DataFrames en uno solo y eliminar duplicados
    if data_frames:
        combined_df = pd.concat(data_frames, ignore_index=True).drop_duplicates()
        return combined_df, len(files)
    else:
        return None

def network_performance_5G_etl():

    REMOTE_FOLDER = "data/naas6g/5G/network_performance_event"
    START_DATE = "2024-05-19_13-00"

    # Llamar a la función para descargar, limpiar, concatenar y almacenar archivos desde la carpeta remota
    start_time = time.time()  # Capturar el tiempo de inicio
    combined_df, n_files = download_clean_concatenate_files(os.getenv("SFTP_HOSTNAME"), os.getenv("SFTP_PORT"), os.getenv("SFTP_USER"), os.getenv("SFTP_PASS"), os.getenv("ID_RSA_ROUTE"), REMOTE_FOLDER, START_DATE)

    if combined_df is not None:
        print("Combined and cleaned DataFrame without duplicates:")
        print(f"Files : {n_files}")
        insert_or_update_dataframe_to_mongo(combined_df)
        end_time = time.time()  # Capturar el tiempo de finalización
        execution_time = end_time - start_time  # Calcular el tiempo total de ejecución

        print(f"The total execution time was {execution_time:.2f} seconds.")

    else:
        print("No se pudieron descargar archivos o no se encontraron archivos válidos para combinar.")

    print("Entering the listening loop")
    while True:
        client = paramiko.SSHClient()

        # Configurar la política para aceptar las claves SSH automáticamente
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(os.getenv("SFTP_HOSTNAME"), os.getenv("SFTP_PORT"), os.getenv("SFTP_USER"), os.getenv("SFTP_PASS"), key_filename=os.getenv("ID_RSA_ROUTE"))

        # Crear una instancia de cliente SFTP dentro de la conexión SSH
        sftp_client = client.open_sftp()
        files = sftp_client.listdir(REMOTE_FOLDER)
        if n_files != len(files):
            remote_path = f"{REMOTE_FOLDER}/{sorted(files)[-1]}"
        
            # Descargar el archivo y leerlo como un DataFrame de pandas
            with sftp_client.file(remote_path) as file:
                # Leer el contenido del archivo
                content = file.read()

            if content:
                # Convertir contenido a un DataFrame de pandas
                df = pd.read_csv(io.BytesIO(content)) 

                # Eliminar filas con NaN y duplicados
                df['eventdate'] = pd.to_datetime(df['eventdate'])
                df_cleaned = df.sort_values(by='eventdate', ascending=True)
                n_files += 1
                print(f"\nNew file. Files : {n_files}")
                insert_or_update_dataframe_to_mongo(df_cleaned)

            sftp_client.close()
            client.close()
        time.sleep(120)
