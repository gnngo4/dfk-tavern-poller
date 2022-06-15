from web3 import Web3

from confluent_kafka import Producer
import uuid
import json

import os,sys,time,logging

from dfk_tavern_tracker.blockchain_streamer import variables as var
from dfk_tavern_tracker.blockchain_streamer.utils import filter_transactions, log_transaction

import bq_utils as bq

def blockchain_streamer():

    bootstrap_servers = "kafka:9092"
    topic = "blockchain_transactions"
    p = Producer({'bootstrap.servers': bootstrap_servers})
    
    try:
        web3 = Web3(Web3.HTTPProvider(var.WEBSOCKET))
    except Exception as ex:
        print(ex)


    REPEATED_TRANSACTIONS = []
    prev_block = web3.eth.block_number
    while True:

        try:

            # get block number
            try:
                current_block = web3.eth.block_number
            except Exception as ex:
                print(ex)
                continue

            if prev_block == current_block:
                continue

            # update `prev_block` when block number changes
            prev_block = current_block

            # get transactions
            try:
                txns = dict(
                        web3.eth.get_block(current_block)
                )['transactions']
            except Exception as ex:
                print(ex)
                continue

            # filter transactions based on `search_contracts`
            filtered_txns = filter_transactions(txns,var.SEARCH_CONTRACTS)

            # log
            if filtered_txns:
                for k, filtered_transactions in filtered_txns.items():
                    for filtered_transaction in filtered_transactions:

                        # Do not process transactions that have been processed already
                        if filtered_transaction.hex() in REPEATED_TRANSACTIONS:
                            print(f"REPEATED: {filtered_transaction.hex()}")
                            continue
                        else:
                            REPEATED_TRANSACTIONS.append(filtered_transaction.hex())
                            if len(REPEATED_TRANSACTIONS) > 40:
                                REPEATED_TRANSACTIONS = REPEATED_TRANSACTIONS[1:]

                        # Submit transaction to kafka topic
                        try:
                            contract,func,receipt = log_transaction(
                                    filtered_transaction,
                                    var.SEARCH_JSONS[k],
                                    verbose=False
                                    )
                        except Exception as ex:
                            print(ex)
                            continue

                        if receipt == 'SUCCESS':
                            func['contract'] = contract
                            record_key = str(uuid.uuid4())
                            record_value = json.dumps(func)
                            p.produce(topic,key=record_key,value=record_value)
                            p.poll(0)
                        else:
                            print(f"DID NOT PROCESS:\n{func}\n{receipt}")

        
        except KeyboardInterrupt:
            p.flush()
            sys.exit(0)

        else:
            continue

if __name__ == "__main__":
    # Start in 60 seconds
    time.sleep(120)
    # Set-up Bigquery tables
    bq.create_bq_table(bq.SOLD_TABLE,bq.TABLE_SCHEMA)
    # Live parsing of blockchain data
    blockchain_streamer()
