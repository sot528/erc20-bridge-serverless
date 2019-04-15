import os
import json
import boto3
from src.operator import execute_bridge
from src.operator import execute_apply_relay_by_tx_hashes
from src.operator import execute_detect_pending_relay

# DynamoDB
db = boto3.resource('dynamodb')
table = db.Table(os.environ['STAGE'] + 'ERC20BridgeInfo')


def deposit(event, context):
    """ 入金処理の実行
    """
    execute_bridge(_load_chain_config(True), table, _get_private_key(True))


def withdraw(event, content):
    """ 出金処理の実行
    """
    execute_bridge(_load_chain_config(False), table, _get_private_key(False))


def applyRelayForDeposit(event, content):
    """ Relayイベントのトランザクションハッシュを指定して入金処理を実行(未完了の入金処理をリトライする際に利用)
    """
    execute_apply_relay_by_tx_hashes(_load_chain_config(
        True), _get_private_key(True), event['relayTransactions'])


def applyRelayForWithdraw(event, content):
    """ Relayイベントのトランザクションハッシュを指定して出金処理を実行(未完了の出金処理をリトライする際に利用)
    """
    execute_apply_relay_by_tx_hashes(_load_chain_config(False), _get_private_key(
        False), event['relayTransactions'])


def detectPendingDeposit(event, content):
    """ 未完了の入金処理の検出
    """
    execute_detect_pending_relay(_load_chain_config(True),
                                 event['notificationEnabled'],
                                 int(os.environ['RELAY_FROM_BLOCK_NUM']),
                                 int(os.environ['APPLY_RELAY_FROM_BLOCK_NUM']),
                                 int(os.environ['RELAY_IGNORE_SEC_THRESHOLD']))


def detectPendingWithdraw(event, content):
    """ 未完了の出金処理の検出
    """
    execute_detect_pending_relay(_load_chain_config(False),
                                 event['notificationEnabled'],
                                 int(os.environ['RELAY_FROM_BLOCK_NUM']),
                                 int(os.environ['APPLY_RELAY_FROM_BLOCK_NUM']),
                                 int(os.environ['RELAY_IGNORE_SEC_THRESHOLD']))


def _load_chain_config(is_deposit):
    """ チェーン情報の取得
    """
    if is_deposit:
        # 入金時
        return {
            'isDeposit': True,
            'chainRpcUrlFrom': os.environ['PUBLIC_CHAIN_RPC_URL'],
            'bridgeContractAddressFrom': os.environ['PUBLIC_CHAIN_BRIDGE_CONTRACT_ADDRESS'],
            'chainRpcUrlTo': os.environ['PRIVATE_CHAIN_RPC_URL'],
            'bridgeContractAddressTo': os.environ['PRIVATE_CHAIN_BRIDGE_CONTRACT_ADDRESS'],
            'gas': os.environ['PRIVATE_CHAIN_GAS'] if 'PRIVATE_CHAIN_GAS' in os.environ else '',
            'gasPrice': os.environ['PRIVATE_CHAIN_GAS_PRICE'] if 'PRIVATE_CHAIN_GAS_PRICE' in os.environ else ''
        }
    else:
        # 出金時
        return {
            'isDeposit': False,
            'chainRpcUrlFrom': os.environ['PRIVATE_CHAIN_RPC_URL'],
            'bridgeContractAddressFrom': os.environ['PRIVATE_CHAIN_BRIDGE_CONTRACT_ADDRESS'],
            'chainRpcUrlTo': os.environ['PUBLIC_CHAIN_RPC_URL'],
            'bridgeContractAddressTo': os.environ['PUBLIC_CHAIN_BRIDGE_CONTRACT_ADDRESS'],
            'gas': os.environ['PUBLIC_CHAIN_GAS'] if 'PUBLIC_CHAIN_GAS' in os.environ else '',
            'gasPrice': os.environ['PUBLIC_CHAIN_GAS_PRICE'] if 'PUBLIC_CHAIN_GAS_PRICE' in os.environ else ''
        }


def _get_private_key(is_deposit):
    """ プライベートキーの取得
    """
    if is_deposit:
        # 入金時
        name = os.environ['STAGE'] + 'ssmBridgeOperatorPrivateChainPrivateKey'
    else:
        # 出金時
        name = os.environ['STAGE'] + 'ssmBridgeOperatorPublicChainPrivateKey'

    return boto3.client('ssm').get_parameter(
        Name=name,
        WithDecryption=True)['Parameter']['Value']
