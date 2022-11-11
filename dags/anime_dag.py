import asyncio
import datetime as dt
import json
import requests

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

ANIME_ONE = "https://www.pinterest.com/resource/BoardFeedResource/get/?source_url=/TomoeHanami/%D0%B0%D0%BD%D0%B8%D0%BC%D0%B5-%D0%BA%D0%B0%D1%80%D1%82%D0%B8%D0%BD%D0%BA%D0%B8/&data=%7B%22options%22%3A%7B%22add_vase%22%3Atrue%2C%22board_id%22%3A%22592504963415172930%22%2C%22field_set_key%22%3A%22react_grid_pin%22%2C%22filter_section_pins%22%3Afalse%2C%22is_react%22%3Atrue%2C%22prepend%22%3Afalse%2C%22page_size%22%3A250%7D%2C%22context%22%3A%7B%7D%7D"
DATABASE_URL = f"postgresql://airflow:123@10.1.1.2:5432/data"


def download_posts_dataset():
    """
        Привет МОАИС
        Остальным соболезную))
    """
    response = requests.get(ANIME_ONE, stream=True)
    response.raise_for_status()
    with open("/files/raw.json", 'w', encoding='utf-8') as f:
        for chunk in response.iter_lines():
            f.write(chunk.decode('utf-8'))


def transform_dataset():
    result = []
    with open("/files/raw.json", "r") as f:
        data = json.loads(''.join(f.readlines()))
    for  pic in data['resource_response']['data']:
        pic_data = {
            "title": pic['title'],
            "grid_title": pic['grid_title'],
            "dominant_color": pic['dominant_color'],
            "image_url": pic['images']['orig']['url'],
            "visual_annotation": pic['pin_join']['visual_annotation']
        }
        result.append(pic_data)
    with open("/files/prep.json", 'w', encoding='utf-8') as f:
        json.dump(result, f)
        


def save_dataset():
    async def do():
        database = databases.Database(DATABASE_URL)
        await database.connect()
        with open("/files/prep.json", "r") as f:
            data = json.loads(''.join(f.readlines()))
            for idx, item in enumerate(data):
                try:
                    await database.execute(f"insert into pictures (title, grid_title, dominant_color, image_url, visual_annotation) values (\
                        '{item['title']}',  \
                        '{item['grid_title']}', \
                        '{item['dominant_color']}', \
                        '{item['image_url']}', \
                        '{json.dumps(item['visual_annotation'])}' \
                    );")
                    r = requests.get(item['image_url'])
                    with open(f"/files/{idx}", "wb") as f:
                        f.write(r.content)
                except:
                    pass

    asyncio.get_event_loop().run_until_complete(do())


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