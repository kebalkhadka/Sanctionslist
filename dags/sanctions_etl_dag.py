
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import ETL functions
from etl.etl import test_db_connection, extract, transform, load

default_args = {
    'owner': 'airflow',
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
    'start_date': datetime(2025, 5, 28),
    'email_on_failure': False,
    'email_on_retry': False,
}

dag = DAG(
    'etl_sanctions_pipeline',
    default_args=default_args,
    description='ETL pipeline for sanctions data',
    schedule='@daily',
    catchup=False,
)

def test_db_task():
    if not test_db_connection():
        raise Exception("DB connection failed")

def extract_task(**context):
    extracted_files = extract()
    context['ti'].xcom_push(key='extracted_files', value=extracted_files)

def transform_task(**context):
    extracted_files = context['ti'].xcom_pull(key='extracted_files', task_ids='extract_data')
    transformed_files = transform(extracted_files)
    context['ti'].xcom_push(key='transformed_files', value=transformed_files)

def load_task(**context):
    transformed_files = context['ti'].xcom_pull(key='transformed_files', task_ids='transform_data')
    load(transformed_files)

test_db = PythonOperator(
    task_id='test_db_connection',
    python_callable=test_db_task,
    dag=dag,
)

extract_data = PythonOperator(
    task_id='extract_data',
    python_callable=extract_task,
    dag=dag,
)

transform_data = PythonOperator(
    task_id='transform_data',
    python_callable=transform_task,
    dag=dag,
)

load_data = PythonOperator(
    task_id='load_data',
    python_callable=load_task,
    dag=dag,
)
 
# extract_data >> transform_data
# test_db >> load_data
# transform_data >> load_data

extract_data >> transform_data >> test_db >> load_data
