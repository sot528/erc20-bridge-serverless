import os
import logging
from web3 import Web3
from src.contract import apply_relay
from src.contract import get_relay_event_logs
from src.contract import parse_relay_event_log

# Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def relay(mode, dynamo_table):
    """
    Execute relay process.

    Args:
        mode (Integer):
            1: Relay token from public chain to private chain
            2: Relay token from private chain to public chain
    """
    if mode is (1, 2):
        raise ValueError("Mode must be 1 or 2")

    # Load chain config
    chain_config = _load_chain_config(mode)

    # Providers
    provider_from = Web3.HTTPProvider(chain_config['CHAIN_RPC_URL_FROM'])
    provider_to = Web3.HTTPProvider(chain_config['CHAIN_RPC_URL_TO'])

    # Get block offset
    relay_block_offset = _get_block_offset(mode, dynamo_table)

    # Get latest block num
    latest_block_num = _get_latest_block_number(provider_from)

    if latest_block_num < relay_block_offset:
        logger.info('There is no more block. latestBlockNum={latest_block_num}, blockOffset={relay_block_offset}'.format(
            latest_block_num=latest_block_num, relay_block_offset=relay_block_offset))
        return

    # Get Relay events
    relay_event_logs = get_relay_event_logs(
        provider_from, chain_config['BRIDGE_CONTRACT_ADDRESS_FROM'], relay_block_offset, latest_block_num)

    logger.info('---------- {num} Relay events from block {fromBlock} to {toBlock} ----------'.format(
        num=len(relay_event_logs), fromBlock=relay_block_offset, toBlock=latest_block_num))

    # Execute applyRelay transaction for each relay event
    for relay_event_log in relay_event_logs:
        parsed_event = parse_relay_event_log(relay_event_log)
        logger.info(
            '[RelayEvent] blockNum={blockNumber}, txHash={txHash}, sender={sender}, recipient={recipient}, amount={amount}, fee={fee}'
            .format(**parsed_event))

        try:
            response = apply_relay(provider_to, chain_config['BRIDGE_CONTRACT_ADDRESS_TO'],
                                   chain_config['CHAIN_OPERATOR_SIGNER_TO'],
                                   chain_config['OPERATOR_PRIVATE_KEY_TO'],
                                   parsed_event['sender'], parsed_event['recipient'], parsed_event['amount'], parsed_event['txHash'],
                                   chain_config['GAS_TO'], chain_config['GAS_PRICE_TO'])

            logger.info(
                '[ApplyRelay] txHash={txHash}, relayEventTxHash={relayEventTxHash}'.format(txHash=response, relayEventTxHash=parsed_event['txHash']))
        except Exception as e:
            logger.error('[ApplyRelay] failed. error={error}'.format(error=e))
            continue

    logger.info('-----------------------------------------------------')

    # Update block offset
    _update_block_offset(mode, dynamo_table, latest_block_num + 1)


def _get_latest_block_number(provider):
    web3Client = Web3(provider)
    return web3Client.eth.blockNumber


def _load_chain_config(mode):
    config = {}
    if mode is 1:
        config['CHAIN_RPC_URL_FROM'] = os.environ['PUBLIC_CHAIN_RPC_URL']
        config['BRIDGE_CONTRACT_ADDRESS_FROM'] = os.environ['PUBLIC_CHAIN_BRIDGE_CONTRACT_ADDRESS']
        config['CHAIN_RPC_URL_TO'] = os.environ['PRIVATE_CHAIN_RPC_URL']
        config['BRIDGE_CONTRACT_ADDRESS_TO'] = os.environ['PRIVATE_CHAIN_BRIDGE_CONTRACT_ADDRESS']
        config['OPERATOR_PRIVATE_KEY_TO'] = os.environ['PRIVATE_CHAIN_OPERATOR_PRIVATE_KEY']
        config['CHAIN_OPERATOR_SIGNER_TO'] = os.environ['PRIVATE_CHAIN_OPERATOR_SIGNER']
        config['GAS_TO'] = os.environ['PRIVATE_CHAIN_GAS']
        config['GAS_PRICE_TO'] = os.environ['PRIVATE_CHAIN_GAS_PRICE']
    elif mode is 2:
        config['CHAIN_RPC_URL_FROM'] = os.environ['PRIVATE_CHAIN_RPC_URL']
        config['BRIDGE_CONTRACT_ADDRESS_FROM'] = os.environ['PRIVATE_CHAIN_BRIDGE_CONTRACT_ADDRESS']
        config['CHAIN_RPC_URL_TO'] = os.environ['PUBLIC_CHAIN_RPC_URL']
        config['BRIDGE_CONTRACT_ADDRESS_TO'] = os.environ['PUBLIC_CHAIN_BRIDGE_CONTRACT_ADDRESS']
        config['OPERATOR_PRIVATE_KEY_TO'] = os.environ['PUBLIC_CHAIN_OPERATOR_PRIVATE_KEY']
        config['CHAIN_OPERATOR_SIGNER_TO'] = os.environ['PUBLIC_CHAIN_OPERATOR_SIGNER']
        config['GAS_TO'] = os.environ['PUBLIC_CHAIN_GAS']
        config['GAS_PRICE_TO'] = os.environ['PUBLIC_CHAIN_GAS_PRICE']
    else:
        raise ValueError("mode must be 1 or 2.")

    return config


def _get_block_offset(mode, table):
    if mode is 1:
        key = "block_offset_public"
    elif mode is 2:
        key = "block_offset_private"
    else:
        raise ValueError("mode must be 1 or 2.")

    result = table.get_item(Key={
        'key': key
    })

    if result is None or 'Item' not in result:
        return 0

    return int(result['Item']['value'])


def _update_block_offset(mode, table, offset):
    if mode is 1:
        key = "block_offset_public"
    elif mode is 2:
        key = "block_offset_private"
    else:
        raise ValueError("mode must be 1 or 2.")

    table.put_item(Item={
        "key": key,
        "value": int(offset)
    })
