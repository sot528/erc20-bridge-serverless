import os
import json
import boto3
from src.operator import execute_bridge
from src.operator import execute_apply_relay_by_tx_hashes
from src.operator import execute_detect_pending_relay

# DynamoDB
db = boto3.resource('dynamodb')
table = db.Table(os.environ['STAGE'] + 'ERC20BridgeInfo')


def bridgePubToPri(event, context):
    execute_bridge(_load_chain_config(True), table, _get_private_key(True))


def bridgePriToPub(event, content):
    execute_bridge(_load_chain_config(False), table, _get_private_key(False))


def applyRelayByTxHashesPriToPub(event, content):
    execute_apply_relay_by_tx_hashes(_load_chain_config(True), _get_private_key(
        True), event['relayTransactions'])


def applyRelayByTxHashesPubToPri(event, content):
    execute_apply_relay_by_tx_hashes(_load_chain_config(
        False), _get_private_key(False), event['relayTransactions'])


def detectPendingRelayPubToPri(event, content):
    execute_detect_pending_relay(_load_chain_config(True),
                                 event['notificationEnabled'],
                                 int(os.environ['RELAY_FROM_BLOCK_NUM']),
                                 int(os.environ['APPLY_RELAY_FROM_BLOCK_NUM']),
                                 int(os.environ['RELAY_IGNORE_SEC_THRESHOLD']))


def detectPendingRelayPriToPub(event, content):
    execute_detect_pending_relay(_load_chain_config(False),
                                 event['notificationEnabled'],
                                 int(os.environ['RELAY_FROM_BLOCK_NUM']),
                                 int(os.environ['APPLY_RELAY_FROM_BLOCK_NUM']),
                                 int(os.environ['RELAY_IGNORE_SEC_THRESHOLD']))


def _load_chain_config(public_to_private):
    if public_to_private:
        return {
            'publicToPrivate': True,
            'chainRpcUrlFrom': os.environ['PUBLIC_CHAIN_RPC_URL'],
            'bridgeContractAddressFrom': os.environ['PUBLIC_CHAIN_BRIDGE_CONTRACT_ADDRESS'],
            'chainRpcUrlTo': os.environ['PRIVATE_CHAIN_RPC_URL'],
            'bridgeContractAddressTo': os.environ['PRIVATE_CHAIN_BRIDGE_CONTRACT_ADDRESS'],
            'gas': os.environ['PRIVATE_CHAIN_GAS'] if 'PRIVATE_CHAIN_GAS' in os.environ else '',
            'gasPrice': os.environ['PRIVATE_CHAIN_GAS_PRICE'] if 'PRIVATE_CHAIN_GAS_PRICE' in os.environ else ''
        }
    else:
        return {
            'publicToPrivate': False,
            'chainRpcUrlFrom': os.environ['PRIVATE_CHAIN_RPC_URL'],
            'bridgeContractAddressFrom': os.environ['PRIVATE_CHAIN_BRIDGE_CONTRACT_ADDRESS'],
            'chainRpcUrlTo': os.environ['PUBLIC_CHAIN_RPC_URL'],
            'bridgeContractAddressTo': os.environ['PUBLIC_CHAIN_BRIDGE_CONTRACT_ADDRESS'],
            'gas': os.environ['PUBLIC_CHAIN_GAS'] if 'PUBLIC_CHAIN_GAS' in os.environ else '',
            'gasPrice': os.environ['PUBLIC_CHAIN_GAS_PRICE'] if 'PUBLIC_CHAIN_GAS_PRICE' in os.environ else ''
        }


def _get_private_key(public_to_private):
    if public_to_private:
        name = os.environ['STAGE'] + 'ssmBridgeOperatorPrivateChainPrivateKey'
    else:
        name = os.environ['STAGE'] + 'ssmBridgeOperatorPublicChainPrivateKey'

    return boto3.client('ssm').get_parameter(
        Name=name,
        WithDecryption=True)['Parameter']['Value']
