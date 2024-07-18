"""

"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import logging
from datetime import timedelta
#import mlflow

from naas_QosMonitoring_dag import QosMonitoring_dag


logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)




#mlflow.set_tracking_uri('http://mlflow:600')

#experiment = mlflow.set_experiment("Airflow_Example")


def _task1():
    """
        This method is responsible for running _task1 logic
    """
    try:

        logger.info('task1-')

        QosMonitoring_dag.run_get_devo_qos()

    except Exception as err:
        logger.exception(err)
        raise err

def _task2():
    """
        This method is responsible for running _task2 logic
    """
    try:

        logger.info('task2-')

        QosMonitoring_dag.run_QoSsus_computation()

    except Exception as err:
        logger.exception(err)
        raise err


def _task3():
    """
        This method is responsible for running _task3 logic
    """
    try:

        logger.info('task3-')

        QosMonitoring_dag.run_trainAndPredict()

    except Exception as err:
        logger.exception(err)
        raise err


def _task4():
    """
        This method is responsible for running _task3 logic
    """
    try:

        logger.info('taks4')
        QosMonitoring_dag.run_send_metrics()

    except Exception as err:
        logger.exception(err)
        raise err

def _task5():
    """
        This method is responsible for running _task3 logic
    """
    try:

        logger.info('taks5')
        QosMonitoring_dag.run_send_predictions()

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


with DAG(dag_id='dag_QosMonitoring', start_date=datetime(2024, 7, 3), 
    catchup=False, default_args=_args, schedule_interval='*/5 * * * *',) as dag:


    t1 = PythonOperator(
        task_id='getDevoQoS',
        op_kwargs=dag.default_args,
        provide_context=True,
        python_callable=_task1
    )


    t2 = PythonOperator(
        task_id='QoSsustainabiltyComp',
        op_kwargs=dag.default_args,
        provide_context=True,
        python_callable=_task2
    )

    t3 = PythonOperator(
        task_id='trainAndPredict',
        op_kwargs=dag.default_args,
        provide_context=True,
        python_callable=_task3
    )

    t4 = PythonOperator(
        task_id='sendMetricsToEventAPI',
        op_kwargs=dag.default_args,
        provide_context=True,
        python_callable=_task4
    )

    t5 = PythonOperator(
        task_id='sendMetricsToPredictionAPI',
        op_kwargs=dag.default_args,
        provide_context=True,
        python_callable=_task5
    )


    

    t1 >> t2 >> t3 >> [t4, t5]



    

