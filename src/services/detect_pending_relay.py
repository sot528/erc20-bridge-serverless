from datetime import datetime
from web3 import Web3
from src.services.helpers import contract
from src.services.helpers import notification
from src.services.helpers.logger import logger


def execute(chain_config, notification_enabled, relay_from_block_num, apply_relay_from_block_num, relay_ignore_sec_threshold):
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
        provider_to, chain_config['bridgeContractAddressTo'], apply_relay_from_block_num)

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
            notification.notify_pending_relays(
                chain_config['isDeposit'], pending_relays, relay_from_block_num, apply_relay_from_block_num)
    else:
        logger.info("No pending relay was detected.")
