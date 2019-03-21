import os
import json
import boto3
from src.operator import bridge
from src.operator import execute_apply_relay

# DynamoDB
db = boto3.resource('dynamodb')
table = db.Table(os.environ['STAGE'] + 'ERC20BridgeInfo')


def bridge_public_to_private(event, context):
    bridge(_load_chain_config(False), table, _get_private_key(False))


def bridge_private_to_public(event, content):
    bridge(_load_chain_config(True), table, _get_private_key(True))


def apply_relay_private(event, content):
    execute_apply_relay(_load_chain_config(False), _get_private_key(
        False), event['relay_transactions'])


def apply_relay_public(event, content):
    execute_apply_relay(_load_chain_config(
        True), _get_private_key(True), event['relay_transactions'])


def _load_chain_config(to_public_chain):
    if to_public_chain:
        return {
            'toPublicChain': False,
            'chainRpcUrlFrom': os.environ['PRIVATE_CHAIN_RPC_URL'],
            'bridgeContractAddressFrom': os.environ['PRIVATE_CHAIN_BRIDGE_CONTRACT_ADDRESS'],
            'chainRpcUrlTo': os.environ['PUBLIC_CHAIN_RPC_URL'],
            'bridgeContractAddressTo': os.environ['PUBLIC_CHAIN_BRIDGE_CONTRACT_ADDRESS'],
            'gas': os.environ['PUBLIC_CHAIN_GAS'],
            'gasPrice': os.environ['PUBLIC_CHAIN_GAS_PRICE']
        }
    else:
        return {
            'toPublicChain': True,
            'chainRpcUrlFrom': os.environ['PUBLIC_CHAIN_RPC_URL'],
            'bridgeContractAddressFrom': os.environ['PUBLIC_CHAIN_BRIDGE_CONTRACT_ADDRESS'],
            'chainRpcUrlTo': os.environ['PRIVATE_CHAIN_RPC_URL'],
            'bridgeContractAddressTo': os.environ['PRIVATE_CHAIN_BRIDGE_CONTRACT_ADDRESS'],
            'gas': os.environ['PRIVATE_CHAIN_GAS'],
            'gasPrice': os.environ['PRIVATE_CHAIN_GAS_PRICE']
        }


def _get_private_key(to_public_chain):
    if to_public_chain:
        name = os.environ['STAGE'] + 'ssmBridgeOperatorPublicChainPrivateKey'
    else:
        name = os.environ['STAGE'] + 'ssmBridgeOperatorPrivateChainPrivateKey'

    return boto3.client('ssm').get_parameter(
        Name=name,
        WithDecryption=True)['Parameter']['Value']
