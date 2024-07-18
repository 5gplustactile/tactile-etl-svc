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

from naas_CoreMonitoring_dag import CoreMonitoring_dag


logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)




#mlflow.set_tracking_uri('http://mlflow:600')

#experiment = mlflow.set_experiment("Airflow_Example")


def _task1():
    """
        This method is responsible for running _task1 logic
    """
    try:

        logger.info('tak1-Get data from Core 5G Network Functions')

        CoreMonitoring_dag.run_get_prometheus_metrics()

    except Exception as err:
        logger.exception(err)
        raise err

def _task2():
    """
        This method is responsible for running _task2 logic
    """
    try:

        logger.info('taks2')

        CoreMonitoring_dag.run_send_metrics()

    except Exception as err:
        logger.exception(err)
        raise err

def _task3():
    """
        This method is responsible for running _task3 logic
    """
    try:

        logger.info('taks3')
        CoreMonitoring_dag.run_sendToGit()

    except Exception as err:
        logger.exception(err)
        raise err

def _task4():
    """
        This method is responsible for running _task3 logic
    """
    try:

        logger.info('taks4')
        CoreMonitoring_dag.run_trainAndPredict()

    except Exception as err:
        logger.exception(err)
        raise err

def _task5():
    """
        This method is responsible for running _task3 logic
    """
    try:

        logger.info('taks5')
        CoreMonitoring_dag.run_CoreMetric_computation()

    except Exception as err:
        logger.exception(err)
        raise err

def _task6():
    """
        This method is responsible for running _task3 logic
    """
    try:

        logger.info('taks6')
        CoreMonitoring_dag.run_send_core_predictions()

    except Exception as err:
        logger.exception(err)
        raise err

_args = {
    'owner': 'Naas6G',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 21),
    'email': ['rodrigosanzsanz@telefonica.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
    
}


with DAG(dag_id='dag_CoreMonitoring', start_date=datetime(2024, 7, 3), 
    catchup=False, default_args=_args, schedule_interval='*/10 * * * *',) as dag:


    getCoreMetrics = PythonOperator(
        task_id='getCoreMetricsByNF-open5gs',
        op_kwargs=dag.default_args,
        provide_context=True,
        python_callable=_task1
    )


    t2 = PythonOperator(
        task_id='sendMetricsToEventAPI-open5gs',
        op_kwargs=dag.default_args,
        provide_context=True,
        python_callable=_task2
    )

    t3 = PythonOperator(
        task_id='sendToGit-HighTrafficScenario-Event',
        op_kwargs=dag.default_args,
        provide_context=True,
        python_callable=_task3
    )

    t4 = PythonOperator(
        task_id='trainAndPredict',
        op_kwargs=dag.default_args,
        provide_context=True,
        python_callable=_task4
    )

    t5 = PythonOperator(
        task_id='coreMetricComputation',
        op_kwargs=dag.default_args,
        provide_context=True,
        python_callable=_task5
    )

    t6 = PythonOperator(
        task_id='sendCorePredictions',
        op_kwargs=dag.default_args,
        provide_context=True,
        python_callable=_task6
    )
    

    getCoreMetrics >> t2 >> t5 >> t4 >> t6 >> t3



    

