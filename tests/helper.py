import boto3

dynamodb_client = boto3.resource(
    'dynamodb', endpoint_url='http://localhost:8000/')


def create_erc20_bridge_info_db_table():
    return dynamodb_client.create_table(
        TableName='localERC20BridgeInfo',
        KeySchema=[
            {
                'AttributeName': 'key',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'key',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        })
