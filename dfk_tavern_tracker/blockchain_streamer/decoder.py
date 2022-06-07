from dfk_tavern_tracker.blockchain_streamer import variables as var

def _filter_function(_transaction,_timestamp,_from,_func):
    
    _action = list(_func.keys())[0]

    price_flag = var.PRICE_KEYS[_action] 
    if _action == 'createAuction':
        _price = [ x[price_flag] for x in _func[_action] if list(x.keys())[0] == price_flag][0][0] / var.PRICE_DENOMINATOR
    elif _action == 'cancelAuction':
        _price = -1
    elif _action == 'bid':
        _price = [ x[price_flag] for x in _func[_action] if list(x.keys())[0] == price_flag][0][0] / var.PRICE_DENOMINATOR
    else:
        print(f"{_action} NOT IMPLEMENTED.")
        NotImplemented

    if _action in list( var.DECODE_KEYS.keys() ):
        
        result = {
                'action':_action,
                'transaction_time':_timestamp,
                'transaction_hash':_transaction,
                'user_address':_from,
                'ID':[ x['_tokenId'] for x in _func[_action] if list(x.keys())[0] == '_tokenId'][0][0],
                'price': _price
                }

        return result

    else:

        return _func

def decode_transaction_function(_transaction,_timestamp,_from,contract, txn_input, abi_parser):
    """
    Decode txn function & function input
    """
    result = {}

    decoded_txn_input = contract.decode_function_input(txn_input)
    func = str(decoded_txn_input[0]).split('Function ')[1].split('(')[0]
    result[func] = []

    inputs = decoded_txn_input[1]
    input_types = abi_parser.get_function_input_types(func)
    output_types = abi_parser.get_function_output_types(func)
    # Save function info
    for key,values in inputs.items():
        result[func].append(
            {
                key: (values, input_types[key])
            }
        )

    result = _filter_function(_transaction.hex(),_timestamp,_from,result)

    return result

def _filter_receipt(_action,_receipt):
    
    receipt_var = var.DECODE_KEYS[_action]
    
    try:
        if receipt_var == list(_receipt.keys())[0]:
            return "SUCCESS"
        else:
            return str(_receipt)

    except:
        return str(_receipt)

def decode_transaction_receipts(_action,contract, txn_receipt, abi_parser):
    """
    Extract txn receipt
    """
    results = {}
    abi_events = abi_parser.get_event_names()
    for event in abi_events:
        results[event] = []
        try:
            processed_receipts = getattr(contract.events,event)().processReceipt(txn_receipt)
            if isinstance(processed_receipts, tuple) and len(processed_receipts) > 0:
                for receipt in processed_receipts:
                    receipt_inputs = dict(dict(receipt)['args'])
                    input_types = abi_parser.get_event_input_types(event)
                    # Save event info
                    for key,values in receipt_inputs.items():
                        results[event].append(
                            {
                                key: (values, input_types[key])
                            }
                        )
        except:
            continue

    return _filter_receipt(
            _action,
            {k:v for k,v in results.items() if v}
            )
