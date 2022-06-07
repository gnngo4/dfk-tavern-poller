import argparse

import sys,os
sys.path.append(os.path.dirname('..'))

from dfk_tavern_tracker.api_querier.utils import get_hero_query 
from dfk_tavern_tracker.api_querier.utils import get_batch_hero_queries

import dfk_tavern_tracker.api_querier.variables as var

def main(params):
    
    option = params.option
    hero_id = params.hero_id

    if option == 'heroes':
        for realm in var.REALMS:
            queries = get_batch_hero_queries(realm)
            for query in queries:
                print(query)

    elif option == 'hero':
        assert hero_id > 0
        query = get_hero_query(hero_id)
        print(query)

    else:
        NotImplemented

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Get query for hero(es)")

    parser.add_argument('option',help='query hero or heroes',choices=['hero','heroes'])
    parser.add_argument('--hero_id',default=0,type=int)

    args = parser.parse_args()

    main(args)
