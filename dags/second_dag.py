from airflow.models import DAG
from airflow.operators.python import PythonOperator
import databases

args = {
    'owner': 'airflow',
    'start_date': dt.datetime(2022, 11, 11),
    'retries': 100,
    'retry_delay': dt.timedelta(minutes=1),
    'depends_on_past': False,
}

with DAG(dag_id='posts_transform', default_args=args, schedule_interval=dt.timedelta(minutes=1)) as dag:
    create_posts_dataset = PythonOperator(
        task_id='download_posts_dataset',
        python_callable=download_posts_dataset,
        dag=dag
    )
    transform_posts_dataset = PythonOperator(
        task_id='transform_dataset',
        python_callable=transform_dataset,
        dag=dag
    )
    save_posts_dataset = PythonOperator(
        task_id='save_dataset',
        python_callable=save_dataset,
        dag=dag
    )
    create_posts_dataset >> transform_posts_dataset >> save_posts_dataset