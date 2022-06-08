import os

from airflow import DAG
from airflow.decorators import task

from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator
from airflow.contrib.operators.bigquery_operator import BigQueryOperator

from datetime import datetime
import pendulum

localpath = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'dfk_data')

schema = [
        {"name":"owner","type":"STRING","description":""},
        {"name":"name","type":"STRING","description":""},
        {"name":"id","type":"STRING","description":""},
        {"name":"numberId","type":"STRING","description":""},
        {"name":"statGenes","type":"STRING","description":""},
        {"name":"visualGenes","type":"STRING","description":""},
        {"name":"rarity","type":"INTEGER","description":""},
        {"name":"shiny","type":"BOOLEAN","description":""},
        {"name":"generation","type":"INTEGER","description":""},
        {"name":"firstName","type":"INTEGER","description":""},
        {"name":"lastName","type":"INTEGER","description":""},
        {"name":"shinyStyle","type":"INTEGER","description":""},
        {"name":"mainClass","type":"STRING","description":""},
        {"name":"subClass","type":"STRING","description":""},
        {"name":"summonedTime","type":"INTEGER","description":""},
        {"name":"summons","type":"INTEGER","description":""},
        {"name":"maxSummons","type":"INTEGER","description":""},
        {"name":"level","type":"INTEGER","description":""},
        {"name":"xp","type":"INTEGER","description":""},
        {"name":"sp","type":"INTEGER","description":""},
        {"name":"status","type":"STRING","description":""},
        {"name":"strength","type":"INTEGER","description":""},
        {"name":"intelligence","type":"INTEGER","description":""},
        {"name":"wisdom","type":"INTEGER","description":""},
        {"name":"luck","type":"INTEGER","description":""},
        {"name":"agility","type":"INTEGER","description":""},
        {"name":"vitality","type":"INTEGER","description":""},
        {"name":"endurance","type":"INTEGER","description":""},
        {"name":"dexterity","type":"INTEGER","description":""},
        {"name":"hp","type":"INTEGER","description":""},
        {"name":"mp","type":"INTEGER","description":""},
        {"name":"stamina","type":"INTEGER","description":""},
        {"name":"strengthGrowthP","type":"INTEGER","description":""},
        {"name":"intelligenceGrowthP","type":"INTEGER","description":""},
        {"name":"wisdomGrowthP","type":"INTEGER","description":""},
        {"name":"luckGrowthP","type":"INTEGER","description":""},
        {"name":"agilityGrowthP","type":"INTEGER","description":""},
        {"name":"vitalityGrowthP","type":"INTEGER","description":""},
        {"name":"enduranceGrowthP","type":"INTEGER","description":""},
        {"name":"dexterityGrowthP","type":"INTEGER","description":""},
        {"name":"strengthGrowthS","type":"INTEGER","description":""},
        {"name":"intelligenceGrowthS","type":"INTEGER","description":""},
        {"name":"wisdomGrowthS","type":"INTEGER","description":""},
        {"name":"luckGrowthS","type":"INTEGER","description":""},
        {"name":"agilityGrowthS","type":"INTEGER","description":""},
        {"name":"vitalityGrowthS","type":"INTEGER","description":""},
        {"name":"enduranceGrowthS","type":"INTEGER","description":""},
        {"name":"dexterityGrowthS","type":"INTEGER","description":""},
        {"name":"hpSmGrowth","type":"INTEGER","description":""},
        {"name":"hpRgGrowth","type":"INTEGER","description":""},
        {"name":"hpLgGrowth","type":"INTEGER","description":""},
        {"name":"mpSmGrowth","type":"INTEGER","description":""},
        {"name":"mpRgGrowth","type":"INTEGER","description":""},
        {"name":"mpLgGrowth","type":"INTEGER","description":""},
        {"name":"mining","type":"INTEGER","description":""},
        {"name":"gardening","type":"INTEGER","description":""},
        {"name":"foraging","type":"INTEGER","description":""},
        {"name":"fishing","type":"INTEGER","description":""},
        {"name":"profession","type":"STRING","description":""},
        {"name":"passive1","type":"STRING","description":""},
        {"name":"passive2","type":"STRING","description":""},
        {"name":"active1","type":"STRING","description":""},
        {"name":"active2","type":"STRING","description":""},
        {"name":"statBoost1","type":"STRING","description":""},
        {"name":"statBoost2","type":"STRING","description":""},
        {"name":"statsUnknown1","type":"STRING","description":""},
        {"name":"element","type":"STRING","description":""},
        {"name":"statsUnknown2","type":"STRING","description":""},
        {"name":"gender","type":"STRING","description":""},
        {"name":"headAppendage","type":"STRING","description":""},
        {"name":"backAppendage","type":"STRING","description":""},
        {"name":"background","type":"STRING","description":""},
        {"name":"hairStyle","type":"STRING","description":""},
        {"name":"hairColor","type":"STRING","description":""},
        {"name":"visualUnknown2","type":"STRING","description":""},
        {"name":"summonsRemaining","type":"INTEGER","description":""},
        {"name":"pjStatus","type":"STRING","description":""},
        {"name":"network","type":"STRING","description":""},
        {"name":"originRealm","type":"STRING","description":""},
        {"name":"timestamp","type":"TIMESTAMP","description":""},
        {"name":"score_mining_lvl100","type":"FLOAT","description":""},
        {"name":"score_gardening_lvl100","type":"FLOAT","description":""},
        {"name":"score_fishing_lvl100","type":"FLOAT","description":""},
        {"name":"score_foraging_lvl100","type":"FLOAT","description":""},
        ]

def get_date_string():
    
    now = datetime.now()
    
    return f"{str(now.year).zfill(4)}{str(now.month).zfill(2)}{str(now.day).zfill(2)}_H{str(now.hour).zfill(2)}M{str(now.minute).zfill(2)}"

@task
def move_latest_to_old_gcs():

    from google.cloud import storage
    
    # Get BUCKET
    client = storage.Client()
    bucket = client.bucket(BUCKET)
    # Move objects in `LATEST` to `OLD` folder
    for blob in bucket.list_blobs(prefix='LATEST/'):
        bucket.rename_blob(
                blob,
                new_name=blob.name.replace('LATEST/','OLD/')
                )

    return 0

@task
def get_queries(fill: int):

    from dfk_tavern_tracker.api_querier.utils import get_all_realms_hero_queries
    
    queries = get_all_realms_hero_queries()

    return queries

@task
def hero_api_call(query: str):

    import json
    from dfk_tavern_tracker.api_querier.utils import api_call

    while True:

        r = api_call(query)
        print(r.text)
        if r.status_code == 200:
            return json.loads(r.text)

@task
def format_to_parquet(json_data: dict):

    from dfk_tavern_tracker.preprocess import preprocess

    from glom import glom
    from datetime import datetime
    import pandas as pd

    columns = list( json_data['data']['heroes'][0].keys() )
    start_hero_id = glom( json_data,('data.heroes',['id']) )[0].zfill(13)
    filename = f"{localpath}/{date_string}_HERO{start_hero_id}.parquet"

    data_dict = {}
    for column in columns:
        data_dict[column] = glom( json_data,('data.heroes',[column]) )

    df = pd.DataFrame.from_dict(data_dict)
    df = pd.concat(
            (
                pd.json_normalize(df['owner']),
                df.drop(columns='owner')
                ),axis=1
            )
    df['timestamp'] = pd.Series([datetime.now()] * df.shape[0])
    # Score hero professions with heuristics
    df = preprocess.score_professions(df)
    df.to_parquet(filename)

    return filename

@task
def upload_to_gcs(filename: str):
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    :param bucket: GCS bucket name
    :param object_name: target path & file-name
    :param local_file: source path & file-name
    :return:
    """

    from google.cloud import storage

    # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # (Ref: https://github.com/googleapis/python-storage/issues/74)
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
    # End of Workaround

    # Get BUCKET
    client = storage.Client()
    bucket = client.bucket(BUCKET)
    # Upload
    object_name = f"LATEST/{filename.split('/')[-1]}"
    blob = bucket.blob(object_name)
    blob.upload_from_filename(filename)
    # Clean airflow parquet data
    os.system(f'rm {filename}')

date_string = get_date_string()

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="hero_info",
    schedule_interval="@daily",
    start_date=pendulum.datetime(2022, 5, 25, tz="America/Toronto"),
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    tags=['dtc-de-project'],
) as dag:
    
    i = move_latest_to_old_gcs()
    queries = get_queries(i)
    all_hero_json_data = hero_api_call.expand(query=queries)
    filenames = format_to_parquet.expand(json_data=all_hero_json_data)
    get_data = upload_to_gcs.expand(filename=filenames)
    create_bq_ext_table = BigQueryCreateExternalTableOperator(
                task_id = f"hero_external_table_task",
                table_resource = {
                    "tableReference": {
                        "projectId": PROJECT_ID,
                        "datasetId": BIGQUERY_DATASET,
                        "tableId": f"hero_external_table",
                        },
                    "schema": {
                        "fields": schema
                        },
                    "externalDataConfiguration": {
                        "autodetect": "True",
                        "sourceFormat": "PARQUET",
                        "sourceUris": [f"gs://{BUCKET}/LATEST/*"],
                        },
                    },
                )

    get_data >> create_bq_ext_table
