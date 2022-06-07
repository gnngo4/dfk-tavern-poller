import faust

import bq_utils as bq

app = faust.App('transaction_processor',broker="kafka:9092")

class transaction(faust.Record,validation=True):
    contract: str
    action: str
    transaction_time: str
    transaction_hash: str
    user_address: str
    ID: str
    price: float

transaction_topic = app.topic("blockchain_transactions",value_type=transaction)
heroes_table = app.Table("in_tavern",key_type=str,value_type=int,partitions=1)

def process(transaction,table):

    if transaction.contract == 'Serendale_AuctionHouse':
        _type = 'Hero'
    else:
        _type = 'Pet'

    print('----')
    print(f"{_type}")
    print(transaction.action)

    process_check = 0
    if transaction.action == 'createAuction':
        print(f"Add {transaction.ID} to {_type} table")
        ### Score hero value function here
        """
        bq.write_hero(
                transaction.user_address,
                transaction.ID,
                transaction.price,
                transaction.transaction_hash,
                transaction.transaction_time,
                bq.HERO_TAVERN_TABLE
                )
        """
        table[transaction.ID] = 1
        process_check = 1

    if transaction.action == 'bid' and \
            (table.get(transaction.ID) is None):
                print(f"DO NOTHING || {transaction.ID} is not registered")
                print(f"ADD to `{bq.SOLD_TABLE}`")
                bq.write_hero(
                        transaction.user_address,
                        transaction.ID,
                        transaction.price,
                        transaction.transaction_hash,
                        transaction.transaction_time,
                        bq.SOLD_TABLE
                        )
                process_check = 1
    elif transaction.action == 'bid' and \
            (table.get(transaction.ID) is not None):
                print(f"Remove {transaction.ID} from {_type} table")
                print(f"ADD to `{bq.SOLD_TABLE}`")
                bq.write_hero(
                        transaction.user_address,
                        transaction.ID,
                        transaction.price,
                        transaction.transaction_hash,
                        transaction.transaction_time,
                        bq.SOLD_TABLE
                        )
                _ = table.pop(transaction.ID)
                process_check = 1
    else:
        pass

    if transaction.action == 'cancelAuction' and \
            (table.get(transaction.ID) is None):
                #print(f"DO NOTHING || {transaction.ID} is not registered")
                process_check = 1
    elif transaction.action == 'cancelAuction' and \
            (table.get(transaction.ID) is not None):
                #print(f"Remove {transaction.ID} from {_type} table")
                _ = table.pop(transaction.ID)
                process_check = 1
    else:
        pass

    if not process_check:
        print(f"No process")
    
    #print(table.keys())

@app.agent(transaction_topic)
async def process_transaction(transactions):
    async for transaction in transactions:
        
        if transaction.contract == 'Serendale_AuctionHouse':
            process(transaction,heroes_table)
        else:
            continue
