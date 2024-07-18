"""

"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import logging
from datetime import timedelta
#import mlflow

import sys
import os
sys.path.insert(0,os.path.abspath(os.path.dirname(__file__)))

from naas_Nokia_etl_dag import nokia_etl_netperf5G
from naas_Nokia_etl_dag import nokia_etl_netperf4G
from naas_Nokia_etl_dag import nokia_etl_congestion5G
from naas_Nokia_etl_dag import nokia_etl_congestion4G

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)


def _task1():
    """
        This method is responsible for running _task1 logic
    """
    try:

        logger.info('task1-')

        nokia_etl_netperf5G.network_performance_5G_etl()

    except Exception as err:
        logger.exception(err)
        raise err
    
def _task2():
    """
        This method is responsible for running _task1 logic
    """
    try:

        logger.info('task2-')

        nokia_etl_congestion4G.congestion_4g_etl()

    except Exception as err:
        logger.exception(err)
        raise err

def _task3():
    """
        This method is responsible for running _task1 logic
    """
    try:

        logger.info('task3-')

        nokia_etl_congestion5G.congestion_5G_etl()

    except Exception as err:
        logger.exception(err)
        raise err

def _task4():
    """
        This method is responsible for running _task1 logic
    """
    try:

        logger.info('task4-')

        nokia_etl_netperf4G.network_performance_4G_etl()

    except Exception as err:
        logger.exception(err)
        raise err


_args = {
    'owner': 'Naas6G',
    'depends_on_past': False,
    'start_date': datetime(2023, 11, 21),
    'email': ['rodrigosanzsanz@telefonica.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
    
}


with DAG(dag_id='dag_Nokia_etl', start_date=datetime(2024, 7, 3), 
    catchup=False, default_args=_args, schedule_interval='0 0 1 2 *',) as dag:


    t1 = PythonOperator(
        task_id='netperf5G_ETL',
        op_kwargs=dag.default_args,
        provide_context=True,
        python_callable=_task1
    )
    t2 = PythonOperator(
        task_id='congestion4G_ETL',
        op_kwargs=dag.default_args,
        provide_context=True,
        python_callable=_task2
    )
    t3 = PythonOperator(
        task_id='congestion5G_ETL',
        op_kwargs=dag.default_args,
        provide_context=True,
        python_callable=_task3
    )
    t4 = PythonOperator(
        task_id='netperf4G_ETL',
        op_kwargs=dag.default_args,
        provide_context=True,
        python_callable=_task4
    )


    


    

    [t1, t2, t3, t4]



    

