import json
import requests

import dfk_tavern_tracker.api_querier.variables as var

def api_call(query,url=var.API_URL):
    return requests.post(url,json={'query':query})

def total_heroes(originRealm):

    query = f"""query{{
    heroes(skip:0,first:1,orderBy:summonedTime,orderDirection:desc,where:{{originRealm:"{originRealm}"}}) {{
        id
        }}
    }}"""

    while True:
        r = api_call(query)
        if r.status_code == 200:
            json_data = json.loads(r.text)
            return int(json_data['data']['heroes'][0]['id']) - var.REALM_ID_OFFSET[originRealm]

def hero_query(hero_id,query_base=var.QUERY_HERO_BASE):
    
    query = f"""query{{
    heroes(skip:0,first:1,where:{{id:{hero_id}}}) {{
        {var.QUERY_HERO_BASE}
    }}
    }}"""
    
    return query

def get_hero_query(hero_id):
    
    query = hero_query(hero_id)
    
    return query

def batch_hero_query(skip,first,originRealm):
    
    query = f"""query{{
    heroes(skip:{skip},first:{first},orderBy:numberId,orderDirection:asc,where:{{originRealm:"{originRealm}"}}) {{
        {var.QUERY_HERO_BASE}
    }}
    }}"""
    
    return query

def get_batch_hero_queries(originRealm):
    
    queries = []
    
    n_heroes = total_heroes(originRealm)
    n_loops = int(n_heroes/var.QUERY_HERO_LENGTH)
    for i in range(n_loops+1):
        skip = i*var.QUERY_HERO_LENGTH
        if i<(n_loops):
            first = var.QUERY_HERO_LENGTH
        else:
            first = n_heroes % var.QUERY_HERO_LENGTH
        query = batch_hero_query(skip,first,originRealm)
        
        queries.append(query)
    
    return queries

def get_all_realms_hero_queries():

    for ix, realm in enumerate(var.REALMS):
        if ix == 0:
            queries = get_batch_hero_queries(realm)
        else:
            queries += get_batch_hero_queries(realm)

    return queries
