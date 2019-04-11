#!/usr/bin/env bash

echo "Starting DynamoDB Local ..."
node_modules/serverless/bin/serverless dynamodb start

# Execute test
python -m unittest discover

echo "Stopping DynamoDB Local"
dynamodb_pid=`ps -ax | grep DynamoDBLocal | grep -v grep | awk '{ print $1 }'`
kill -9 $dynamodb_pid

echo "Finished"
