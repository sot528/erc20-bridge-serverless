import os
import logging
from web3 import Web3
from src.contract import apply_relay
from src.contract import get_relay_event_logs
from src.contract import get_relay_event_log_by_tx_hash
from src.contract import parse_relay_event_log

# Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def bridge(chain_config, dynamo_table, private_key):
    """ Execute bridge process.
    """
    # Providers
    provider_from = Web3.HTTPProvider(chain_config['chainRpcUrlFrom'])
    provider_to = Web3.HTTPProvider(chain_config['chainRpcUrlTo'])

    # Get block offset
    relay_block_offset = _get_block_offset(
        chain_config['toPublicChain'], dynamo_table)

    # Get latest block num
    latest_block_num = _get_latest_block_number(provider_from)

    if latest_block_num < relay_block_offset:
        logger.info('There is no more block. latestBlockNum={latest_block_num}, blockOffset={relay_block_offset}'.format(
            latest_block_num=latest_block_num, relay_block_offset=relay_block_offset))
        return

    # Get Relay events
    relay_event_logs = get_relay_event_logs(
        provider_from, chain_config['bridgeContractAddressFrom'], relay_block_offset, latest_block_num)

    logger.info('---------- {num} Relay events from block {fromBlock} to {toBlock} ----------'.format(
        num=len(relay_event_logs), fromBlock=relay_block_offset, toBlock=latest_block_num))

    # Execute applyRelay transaction for each relay event
    for relay_event_log in relay_event_logs:
        parsed_event = parse_relay_event_log(relay_event_log)
        logger.info(
            '[RelayEvent] blockNum={blockNumber}, txHash={txHash}, sender={sender}, recipient={recipient}, amount={amount}, fee={fee}, timestamp={timestamp}'
            .format(**parsed_event))

        try:
            response = _apply_relay(
                provider_to, chain_config, private_key, parsed_event)
            logger.info(
                '[ApplyRelay] txHash={txHash}, relayEventTxHash={relayEventTxHash}'.format(txHash=response, relayEventTxHash=parsed_event['txHash']))
        except Exception as e:
            logger.error('[ApplyRelay] failed. error={error}'.format(error=e))
            continue

    logger.info('Finished.')

    # Update block offset
    _update_block_offset(
        chain_config['toPublicChain'], dynamo_table, latest_block_num + 1)


def execute_apply_relay(chain_config, private_key, relay_transactions):
    """ Execute applyRelay.
    """
    # Providers
    provider_from = Web3.HTTPProvider(chain_config['chainRpcUrlFrom'])
    provider_to = Web3.HTTPProvider(chain_config['chainRpcUrlTo'])

    for relay_transaction in relay_transactions:
        relay_event_log = get_relay_event_log_by_tx_hash(
            provider_from, relay_transaction)
        parsed_event = parse_relay_event_log(relay_event_log)

        logger.info(
            '[RelayEvent] blockNum={blockNumber}, txHash={txHash}, sender={sender}, recipient={recipient}, amount={amount}, fee={fee}'
            .format(**parsed_event))

        try:
            response = _apply_relay(
                provider_to, chain_config, private_key, parsed_event)
            logger.info(
                '[ApplyRelay] txHash={txHash}, relayEventTxHash={relayEventTxHash}'.format(txHash=response, relayEventTxHash=parsed_event['txHash']))
        except Exception as e:
            logger.error('[ApplyRelay] failed. error={error}'.format(error=e))
            continue

    logger.info('Finished')


def _apply_relay(provider, chain_config, private_key, relay_event):
    return apply_relay(provider, chain_config['bridgeContractAddressTo'],
                       private_key,
                       relay_event['sender'], relay_event['recipient'], relay_event['amount'], relay_event['txHash'],
                       chain_config['gas'], chain_config['gasPrice'])


def _get_latest_block_number(provider):
    web3 = Web3(provider)
    return web3.eth.blockNumber


def _get_block_offset(to_public_chain, table):
    result = table.get_item(Key={
        'key': _get_block_offset_key(to_public_chain)
    })

    if result is None or 'Item' not in result:
        return 0

    return int(result['Item']['value'])


def _update_block_offset(to_public_chain, table, offset):
    table.put_item(Item={
        "key": _get_block_offset_key(to_public_chain),
        "value": int(offset)
    })


def _get_block_offset_key(to_public_chain):
    if to_public_chain:
        return "private_to_public_offset"
    else:
        return "public_to_private_offset"
