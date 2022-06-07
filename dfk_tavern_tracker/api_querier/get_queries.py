import argparse

import sys,os
sys.path.append(os.path.dirname('..'))

from dfk_tavern_tracker.api_querier.utils import get_batch_hero_queries

import dfk_tavern_tracker.api_querier.variables as var

for ix,realm in enumerate(var.REALMS):
    if ix == 0:
        queries = get_batch_hero_queries(realm)
    else:
        queries += get_batch_hero_queries(realm)

    print(len(queries))

import pdb; pdb.set_trace()
