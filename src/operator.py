import os
import logging
from datetime import datetime
from web3 import Web3
from src import contract
from src import notification_util

# Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def execute_bridge(chain_config, dynamo_table, private_key):
    """ 入出金処理の実行
    """
    # Web3プロバイダーの生成
    provider_from = Web3.HTTPProvider(chain_config['chainRpcUrlFrom'])
    provider_to = Web3.HTTPProvider(chain_config['chainRpcUrlTo'])

    # 処理を開始するブロックのオフセットを取得
    relay_block_offset = _get_block_offset(
        chain_config['publicToPrivate'], dynamo_table)

    # 最新のブロック数を取得
    latest_block_num = _get_latest_block_number(provider_from)

    if latest_block_num < relay_block_offset:
        # 最新のブロックを処理済み
        logger.info('There is no more block. latestBlockNum={latest_block_num}, blockOffset={relay_block_offset}'.format(
            latest_block_num=latest_block_num, relay_block_offset=relay_block_offset))
        return

    # Relayイベントを取得
    relay_event_logs = contract.get_relay_event_logs(
        provider_from, chain_config['bridgeContractAddressFrom'], relay_block_offset, latest_block_num)

    logger.info('---------- {num} Relay events from block {fromBlock} to {toBlock} ----------'.format(
        num=len(relay_event_logs), fromBlock=relay_block_offset, toBlock=latest_block_num))

    # 各Relayイベントに対して、applyRelay処理を実行
    for relay_event_log in relay_event_logs:
        parsed_event = contract.parse_relay_event_log(relay_event_log)
        logger.info(
            '[RelayEvent] timestamp={timestamp}, blockNum={blockNumber}, txHash={txHash}, sender={sender}, recipient={recipient}, amount={amount}, fee={fee}'
            .format(**parsed_event))

        try:
            # applyRelay処理を実行
            response = _apply_relay(
                provider_to, chain_config, private_key, parsed_event)
            logger.info(
                '[ApplyRelay] txHash={txHash}, relayEventTxHash={relayEventTxHash}'.format(txHash=response, relayEventTxHash=parsed_event['txHash']))
        except Exception as e:
            logger.error('[ApplyRelay] failed. error={error}'.format(error=e))
            continue

    logger.info('Finished.')

    # 次の入出金処理を開始する際のブロックのオフセットを更新
    _update_block_offset(
        chain_config['publicToPrivate'], dynamo_table, latest_block_num + 1)


def execute_apply_relay_by_tx_hashes(chain_config, private_key, relay_transactions):
    """ Relayイベントのトランザクションハッシュを指定して入出金処理を実行(未完了の入出金処理をリトライする際に利用)
    """
    # Web3プロバイダーの生成
    provider_from = Web3.HTTPProvider(chain_config['chainRpcUrlFrom'])
    provider_to = Web3.HTTPProvider(chain_config['chainRpcUrlTo'])

    # 各Relayイベントに対して、applyRelay処理を実行
    for relay_transaction in relay_transactions:
        # トランザクションハッシュからRelayイベントを取得
        relay_event_log = contract.get_relay_event_log_by_tx_hash(
            provider_from, relay_transaction)

        parsed_event = contract.parse_relay_event_log(relay_event_log)

        logger.info(
            '[RelayEvent] timestamp={timestamp}, blockNum={blockNumber}, txHash={txHash}, sender={sender}, recipient={recipient}, amount={amount}, fee={fee}'
            .format(**parsed_event))

        try:
            # applyRelay処理を実行
            response = _apply_relay(
                provider_to, chain_config, private_key, parsed_event)
            logger.info(
                '[ApplyRelay] txHash={txHash}, relayEventTxHash={relayEventTxHash}'.format(txHash=response, relayEventTxHash=parsed_event['txHash']))
        except Exception as e:
            logger.error('[ApplyRelay] failed. error={error}'.format(error=e))
            continue

    logger.info('Finished')


def execute_detect_pending_relay(chain_config, notification_enabled, relay_from_block_num, apply_relay_from_block_num, relay_ignore_sec_threshold):
    """ 未完了の入出金処理の検出
    """
    logger.info(
        'Relay from block: {relay_from_block_num}, Apply Relay from block: {apply_relay_from_block_num}'.format(
            relay_from_block_num=relay_from_block_num, apply_relay_from_block_num=apply_relay_from_block_num))

    # Web3プロバイダーの生成
    provider_from = Web3.HTTPProvider(chain_config['chainRpcUrlFrom'])
    provider_to = Web3.HTTPProvider(chain_config['chainRpcUrlTo'])

    # Relayイベントの取得
    relay_events = contract.get_relay_event_logs(
        provider_from, chain_config['bridgeContractAddressFrom'], relay_from_block_num)

    # ApplyRelayイベントの取得
    apply_relay_events = contract.get_apply_relay_event_logs(
        provider_to, chain_config['bridgeContractAddressFrom'], apply_relay_from_block_num)

    # applyRelayが実行済みのRelayイベントの抽出
    completed_relay_tx_hashes = set()
    for apply_relay_event in apply_relay_events:
        parsed_apply_relay_event = contract.parse_apply_relay_event_log(
            apply_relay_event)
        completed_relay_tx_hashes.add(parsed_apply_relay_event['relayTxHash'])

    # applyRelayが未実行のRelayイベントの抽出
    pending_relays = []
    for relay_event in relay_events:
        parsed_relay_event = contract.parse_relay_event_log(relay_event)

        # NOTICE 直近のRelayイベントはバッチで処理されるまでにタイムラグがあるため無視する
        if (datetime.utcnow().timestamp() - parsed_relay_event['timestamp']) < relay_ignore_sec_threshold:
            continue

        if parsed_relay_event['txHash'] not in completed_relay_tx_hashes:
            pending_relays.append(parsed_relay_event)

    # 未完了の入出金処理が存在するか
    if len(pending_relays) > 0:
        logger.info(
            '{pending_relay_count} pending relays were detected.'.format(pending_relay_count=len(pending_relays)))

        for pending_relay in pending_relays:
            logger.info(
                '[RelayEvent] timestamp={timestamp}, blockNum={blockNumber}, txHash={txHash}, sender={sender}, recipient={recipient}, amount={amount}, fee={fee}'
                .format(**pending_relay))

        # Slackに通知
        if notification_enabled:
            notification_util.notify_pending_relays(
                chain_config['publicToPrivate'], pending_relays, relay_from_block_num, apply_relay_from_block_num)
    else:
        logger.info("No pending relay was detected.")


def _apply_relay(provider, chain_config, private_key, relay_event):
    """ applyRelayの実行
    """
    return contract.apply_relay(provider, chain_config['bridgeContractAddressTo'],
                                private_key,
                                relay_event['sender'], relay_event['recipient'], relay_event['amount'], relay_event['txHash'],
                                chain_config['gas'], chain_config['gasPrice'])


def _get_latest_block_number(provider):
    """ 最新のブロック数の取得
    """
    web3 = Web3(provider)
    return web3.eth.blockNumber


def _get_block_offset(public_to_private, table):
    """ 入出金を開始するブロックのオフセットの取得
    """
    result = table.get_item(Key={
        'key': _get_block_offset_key(public_to_private)
    })

    if result is None or 'Item' not in result:
        return 0

    return int(result['Item']['value'])


def _update_block_offset(public_to_private, table, offset):
    """ 入出金を開始するブロックのオフセットの更新
    """
    table.put_item(Item={
        "key": _get_block_offset_key(public_to_private),
        "value": int(offset)
    })


def _get_block_offset_key(public_to_private):
    """ ブロックオフセットのテーブルのキーの取得
    """
    if public_to_private:
        # 入金時
        return "public_to_private_offset"
    else:
        # 出金時
        return "private_to_public_offset"
