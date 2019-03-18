import os
import json
import boto3
from src.operator import relay

# DynamoDB
db = boto3.resource('dynamodb')
table = db.Table(os.environ['STAGE'] + '-erc20BridgeInfo')


def relay_public_to_private(event, context):
    relay(1, table)


def relay_private_to_public(event, content):
    relay(2, table)
