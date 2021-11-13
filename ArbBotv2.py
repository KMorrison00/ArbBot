from web3 import Web3
import json
from peregrinearb import bellman_ford_multi, print_profit_opportunity_for_path_multi
import networkx as nx
import math
from dotenv import load_dotenv, find_dotenv
import os


def main():
    load_dotenv(find_dotenv())

    mainnet_node = os.getenv('INFURA_MAINNET')
    orfeed_abi = os.getenv('ORFEED_ABI')
    orfeed_data_address = os.getenv("ORFEED_DATA_ADDRESS")

    w3 = Web3(Web3.HTTPProvider(mainnet_node))

    # orfeed data dapp ABI
    orfeed_abi = json.loads(orfeed_abi)

    # orfeed data dapp address
    orfeed_data_address = w3.toChecksumAddress(orfeed_data_address)

    # initialize the contract
    contract = w3.eth.contract(address=orfeed_data_address, abi=orfeed_abi)

    coins = ["ETH", "MKR", "DAI", "USX", "OMG", "ZRX", "BAT", "LINK"]
    exchanges = ["BANCOR", "KYBER", "UNISWAP", "UNIWSWAPV2"]
    len_ex = len(exchanges)
    len_cur = len(coins)

    graph = nx.MultiDiGraph()

    # this replaces call to create_weighted_multi_exchange_digraph
    for e in range(len_ex):
        for i in range(len_cur):
            for j in range(len_cur):
                # getExchangeRate method errors if you try to use the same currency as both args
                if i != j:
                    quote = contract.functions.getExchangeRate(coins[i], coins[j], exchanges[e], 1000000000).call()
                    # if a quote is zero it can't be logged or used in the algo, so skip any 0's
                    if quote != 0:
                        # divide the quote by 10^9 to compensate for lack of decimals in normal erc20 token prices
                        graph.add_edge(coins[i], coins[j],
                                       market_name=(coins[i]+"/"+coins[j]),
                                       exchange_name=str.lower(exchanges[e]),
                                       weight=-math.log(quote / (10 ** 9)))

    graph, paths = bellman_ford_multi(graph, 'ETH')
    for path in paths:
        # orfeed arb method only support up to 3 curriencies to trade, could try to tweek i suppose
        if path and len(path) < 4:
            print_profit_opportunity_for_path_multi(graph, path)


def test():
    load_dotenv(find_dotenv())

    mainnet_node = os.getenv('INFURA_MAINNET')
    orfeed_abi = os.getenv('ORFEED_ABI')
    orfeed_data_address = os.getenv("ORFEED_DATA_ADDRESS")

    w3 = Web3(Web3.HTTPProvider(mainnet_node))

    # orfeed data dapp ABI
    orfeed_abi = json.loads(orfeed_abi)

    # orfeed data dapp address
    orfeed_data_address = w3.toChecksumAddress(orfeed_data_address)

    # initialize the contract
    contract = w3.eth.contract(address=orfeed_data_address, abi=orfeed_abi)

    coins = ["ETH", "MKR", "DAI", "USX", "OMG", "ZRX", "BAT", "LINK"]
    exchanges = ["BANCOR", "KYBER", "UNISWAP", "UNIWSWAPV2"]
    len_ex = len(exchanges)
    len_cur = len(coins)

    quote = contract.functions.getExchangeRate(coins[0], coins[3], exchanges[1], 1000000000).call()
    print(quote)
    print(quote / (10**9))


if __name__ == "__main__":
    # test()
    main()
