from web3 import Web3

import variables as var
from utils import filter_transactions, log_transaction

def main(verbose=False):

    web3 = Web3(Web3.HTTPProvider(var.WEBSOCKET))

    prev_block = web3.eth.block_number
    while True:
            
        try:
            # get block number
            current_block = web3.eth.block_number
            if prev_block == current_block:
                    continue
            # update `prev_block` when block number changes
            prev_block = current_block
            # get transactions
            txns = dict(
                    web3.eth.get_block(current_block)
            )['transactions']
            # filter transactions based on `search_contracts`
            filtered_txns = filter_transactions(txns,var.SEARCH_CONTRACTS)
            # log
            if filtered_txns:
                    for k, filtered_transactions in filtered_txns.items():
                            for filtered_transaction in filtered_transactions:
                                    contract,func,receipt = log_transaction(
                                            filtered_transaction,
                                            var.SEARCH_JSONS[k],
                                            verbose=verbose
                                            )
        except:
            import sys
            sys.exit()

if __name__ == '__main__':

    main(verbose=True)
