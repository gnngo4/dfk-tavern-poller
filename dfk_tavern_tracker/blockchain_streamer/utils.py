from datetime import datetime
from web3 import Web3

from dfk_tavern_tracker.blockchain_streamer import variables as var
from dfk_tavern_tracker.blockchain_streamer.abi_parser import ABIParser
from dfk_tavern_tracker.blockchain_streamer.decoder import decode_transaction_function, decode_transaction_receipts


web3 = Web3(Web3.HTTPProvider(var.WEBSOCKET))

# Parse transactions
def filter_transactions(transactions,filter_dict):
    # Set up variables
    filter_list = list( filter_dict.keys() )
    filter_transactions = {}
    for addr in filter_list:
        filter_transactions[addr] = []
    # 
    for transaction in transactions:
        try:
            _transaction = web3.eth.get_transaction(transaction)
            _from = _transaction['from'] if _transaction['from'] is not None else 'None'
            _to = _transaction['to'] if _transaction['to'] is not None else 'None'
            if _to.lower() in filter_list:
                filter_transactions[_to.lower()].append(
                    transaction
                )
        except:
            print(f'ERROR: {transaction.hex()}')
            
    return {k:v for k,v in filter_transactions.items() if v}

# Get transaction info
def log_transaction(transaction_id, abi_json,search_contracts=var.SEARCH_CONTRACTS,verbose=False):
    import warnings
    warnings.filterwarnings('ignore')
    # Get transaction info from blockchain
    txn = web3.eth.get_transaction(transaction_id)
    txn_receipt = web3.eth.get_transaction_receipt(transaction_id)
    # Transaction info
    _timestamp = datetime.fromtimestamp(int(txn['timestamp'],0)).strftime("%Y/%m/%d, %H:%M:%S")
    _from = txn['from']
    _to = search_contracts[txn['to'].lower()]
    _input = txn['input']
    # abi info
    abi_parser = ABIParser(abi_json)
    json_data = abi_parser.load_json()

    # Contract
    contract = web3.eth.contract(txn['to'],abi=json_data)
    decoded_function = decode_transaction_function(
            transaction_id,
            _timestamp,
            _from,
            contract,
            _input,
            abi_parser
            )
    decoded_receipts = decode_transaction_receipts(
            decoded_function['action'],
            contract,
            txn_receipt,
            abi_parser
            )

    # Log
    if verbose:
        print(f"\n{_to}")
        print('Transaction info:')
        for _key,_value in decoded_function.items():
            print(f"  {_key}: {_value}")
        print(f"Receipt: {decoded_receipts}")

    return _to ,decoded_function, decoded_receipts
