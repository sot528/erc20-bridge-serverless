import os
import json
import boto3
from src.operator import bridge
from src.operator import execute_apply_relay

# DynamoDB
db = boto3.resource('dynamodb')
table = db.Table(os.environ['STAGE'] + '-erc20BridgeInfo')


def bridge_public_to_private(event, context):
    bridge(1, table)


def bridge_private_to_public(event, content):
    bridge(2, table)


def apply_relay_private(event, content):
    execute_apply_relay(1, event['relay_transactions'])


def apply_relay_public(event, content):
    execute_apply_relay(2, event['relay_transactions'])
