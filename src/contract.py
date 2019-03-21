import json
from web3 import Web3
from eth_account import Account

ABI_JSON = '[{"name":"Relay","inputs":[{"type":"address","name":"_from","indexed":true},{"type":"address","name":"_recipient","indexed":true},{"type":"uint256","name":"_amount","indexed":false},{"type":"uint256","name":"_fee","indexed":false}],"anonymous":false,"type":"event"},{"name":"ApplyRelay","inputs":[{"type":"address","name":"_from","indexed":true},{"type":"address","name":"_recipient","indexed":true},{"type":"uint256","name":"_amount","indexed":false},{"type":"bytes32","name":"_txHash","indexed":false}],"anonymous":false,"type":"event"},{"name":"Transfer","inputs":[{"type":"address","name":"_from","indexed":true},{"type":"address","name":"_to","indexed":true},{"type":"uint256","name":"_value","indexed":false}],"anonymous":false,"type":"event"},{"name":"__init__","outputs":[],"inputs":[{"type":"address","name":"_token"},{"type":"uint256","name":"_minSingleRelayAmount"},{"type":"uint256","name":"_maxSingleRelayAmount"},{"type":"uint256","name":"_relayFee"}],"constant":false,"payable":false,"type":"constructor"},{"name":"relay","outputs":[],"inputs":[{"type":"address","name":"_recipient"},{"type":"uint256","name":"_amount"}],"constant":false,"payable":false,"type":"function","gas":7362},{"name":"applyRelay","outputs":[],"inputs":[{"type":"address","name":"_from"},{"type":"address","name":"_recipient"},{"type":"uint256","name":"_amount"},{"type":"bytes32","name":"_txHash"}],"constant":false,"payable":false,"type":"function","gas":41512},{"name":"getToken","outputs":[{"type":"address","name":"out"}],"inputs":[],"constant":true,"payable":false,"type":"function","gas":543},{"name":"setToken","outputs":[],"inputs":[{"type":"address","name":"_token"}],"constant":false,"payable":false,"type":"function","gas":35524},{"name":"setAuthority","outputs":[],"inputs":[{"type":"address","name":"_authority"}],"constant":false,"payable":false,"type":"function","gas":35747},{"name":"setMinSingleRelayAmount","outputs":[],"inputs":[{"type":"uint256","name":"_amount"}],"constant":false,"payable":false,"type":"function","gas":36548},{"name":"setMaxSingleRelayAmount","outputs":[],"inputs":[{"type":"uint256","name":"_amount"}],"constant":false,"payable":false,"type":"function","gas":36084},{"name":"setRelayFee","outputs":[],"inputs":[{"type":"uint256","name":"_fee"}],"constant":false,"payable":false,"type":"function","gas":36095},{"name":"setRelayPaused","outputs":[],"inputs":[{"type":"bool","name":"_relayPaused"}],"constant":false,"payable":false,"type":"function","gas":35864},{"name":"maxSingleRelayAmount","outputs":[{"type":"uint256","name":"out"}],"inputs":[],"constant":true,"payable":false,"type":"function","gas":753},{"name":"minSingleRelayAmount","outputs":[{"type":"uint256","name":"out"}],"inputs":[],"constant":true,"payable":false,"type":"function","gas":783},{"name":"relayFee","outputs":[{"type":"uint256","name":"out"}],"inputs":[],"constant":true,"payable":false,"type":"function","gas":813},{"name":"relayTransactions","outputs":[{"type":"bool","name":"out"}],"inputs":[{"type":"bytes32","name":"arg0"}],"constant":true,"payable":false,"type":"function","gas":976},{"name":"authority","outputs":[{"type":"address","name":"out"}],"inputs":[],"constant":true,"payable":false,"type":"function","gas":873},{"name":"relayPaused","outputs":[{"type":"bool","name":"out"}],"inputs":[],"constant":true,"payable":false,"type":"function","gas":903}]'


def apply_relay(provider, contract_address, private_key, sender, recipient, amount, txHash, gas, gasPrice):
    web3 = Web3(provider)

    contract = web3.eth.contract(
        web3.toChecksumAddress(contract_address), abi=json.loads(ABI_JSON))

    account = Account.privateKeyToAccount(private_key).address
    nonce = web3.eth.getTransactionCount(account)

    transaction = contract.functions.applyRelay(web3.toChecksumAddress(sender), web3.toChecksumAddress(recipient), amount, txHash).buildTransaction({
        'nonce': nonce,
        'gas': hex(int(gas)),
        'gasPrice': hex(int(gasPrice))
    })

    signed_transaction = web3.eth.account.signTransaction(
        transaction, private_key=private_key)

    return web3.eth.sendRawTransaction(
        signed_transaction.rawTransaction).hex()


def get_relay_event_logs(provider, contract_address, from_block, to_block="latest"):
    web3 = Web3(provider)

    event_signature_hash = web3.sha3(
        text="Relay(address,address,uint256,uint256)").hex()

    return web3.eth.getLogs({'fromBlock': from_block, 'toBlock': to_block,
                             'address': web3.toChecksumAddress(contract_address),
                             'topics': [event_signature_hash]})


def get_relay_event_log_by_tx_hash(provider, relay_transaction_hash):
    web3 = Web3(provider)

    return web3.eth.getTransactionReceipt(
        relay_transaction_hash)['logs'][1]


def parse_relay_event_log(relay_event_log):
    return {
        "sender": "0x" + relay_event_log['topics'][1].hex()[-40:],
        "recipient": "0x" + relay_event_log['topics'][2].hex()[-40:],
        "amount": int(relay_event_log['data'][2:66], 16),
        "fee": int(relay_event_log['data'][66:130], 16),
        "txHash": relay_event_log['transactionHash'].hex(),
        "blockNumber": relay_event_log['blockNumber']
    }
