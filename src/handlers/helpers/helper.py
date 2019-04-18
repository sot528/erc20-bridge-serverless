import os
import boto3
import logging


# DynamoDB
_db = boto3.resource('dynamodb')
db_table = _db.Table(os.environ['ALIS_APP_ID'] + 'ERC20BridgeInfo')


def load_chain_config(is_deposit):
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


def get_private_key(is_deposit):
    """ プライベートキーの取得
    """
    if is_deposit:
        # 入金時
        name = os.environ['ALIS_APP_ID'] + 'ssmBridgeOperatorPrivateChainPrivateKey'
    else:
        # 出金時
        name = os.environ['ALIS_APP_ID'] + 'ssmBridgeOperatorPublicChainPrivateKey'

    return boto3.client('ssm').get_parameter(
        Name=name,
        WithDecryption=True)['Parameter']['Value']
