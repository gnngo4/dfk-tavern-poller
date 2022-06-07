import os

WEBSOCKET = "https://rpc.s0.t.hmny.io"

ABIDIR = "./dfk_tavern_tracker/blockchain_streamer/abi"

SEARCH_CONTRACTS = {
    "0x13a65b9f8039e2c032bc022171dc05b30c3f2892": 'Serendale_AuctionHouse',
    "0x72f860bf73ffa3fc42b97bbcf43ae80280cfcdc3": 'Serendale_Hatchery',
}

SEARCH_JSONS = {
    "0x13a65b9f8039e2c032bc022171dc05b30c3f2892": os.path.join(ABIDIR,'SaleAuction.json'),
    "0x72f860bf73ffa3fc42b97bbcf43ae80280cfcdc3": os.path.join(ABIDIR,'SaleAuction.json'),
}

PRICE_DENOMINATOR = 10e17

# DECODE VARIABLES
DECODE_KEYS = {
        'createAuction':'AuctionCreated',
        'cancelAuction':'AuctionCancelled',
        'bid':'AuctionSuccessful',
        }

PRICE_KEYS = {
        'createAuction':'_startingPrice',
        'cancelAuction':'_bidAmount',
        'bid':'_bidAmount',
        }
