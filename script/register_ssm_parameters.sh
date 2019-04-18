#!/usr/bin/env bash

# SSM Secure String param
aws ssm put-parameter \
    --name ${ALIS_APP_ID}ssmBridgeOperatorPublicChainPrivateKey \
    --value ${OPERATOR_PUBLIC_CHAIN_PRIVATE_KEY} \
    --type SecureString \
    --overwrite \
    --key-id alias/aws/ssm

aws ssm put-parameter \
    --name ${ALIS_APP_ID}ssmBridgeOperatorPrivateChainPrivateKey \
    --value ${OPERATOR_PRIVATE_CHAIN_PRIVATE_KEY} \
    --type SecureString \
    --overwrite \
    --key-id alias/aws/ssm
