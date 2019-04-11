from unittest import TestCase
from unittest.mock import patch, MagicMock, call, ANY
from .context import src
from .helper import create_erc20_bridge_info_db_table
from .mock_data.relay_log_data import relay_event_logs
from .mock_data.apply_relay_log_data import apply_relay_event_logs
from src.operator import execute_bridge
from src.operator import execute_apply_relay_by_tx_hashes
from src.operator import execute_detect_pending_relay
from src.contract import parse_relay_event_log

CHAIN_CONFIG = {
    'publicToPrivate': True,
    'chainRpcUrlFrom': 'http://example.com',
    'bridgeContractAddressFrom': '0x' + 'a' * 40,
    'chainRpcUrlTo': 'http://example.com',
    'bridgeContractAddressTo': '0x' + 'b' * 40,
    'gas': '5500000',
    'gasPrice': '1000000000'
}

PRIVATE_KEY = "0x" + "c" * 64


class TestOperator(TestCase):
    def setUp(self):
        self.db_table = create_erc20_bridge_info_db_table()

    def tearDown(self):
        self.db_table.delete()

    @patch('src.contract.get_relay_event_logs')
    @patch('src.contract.apply_relay')
    @patch('src.operator._get_latest_block_number')
    def test_ok_execute_bridge(self, mock_get_latest_block_number, mock_apply_relay, mock_get_relay_event_logs):
        # constants
        LATEST_BLOCK_NUMBER = 100000

        # Setup mock
        mock_get_relay_event_logs.return_value = relay_event_logs
        mock_apply_relay.return_value = '0x' + 'a' * 64
        mock_get_latest_block_number.return_value = LATEST_BLOCK_NUMBER

        # Execute
        execute_bridge(CHAIN_CONFIG, self.db_table, PRIVATE_KEY)

        # Assert call count
        self.assertEqual(mock_apply_relay.call_count, len(relay_event_logs))

        # Assert parameters
        apply_relay_calls = []
        for relay_event_log in relay_event_logs:
            apply_relay_calls.append(call(
                ANY,
                CHAIN_CONFIG['bridgeContractAddressTo'],
                PRIVATE_KEY,
                "0x" + relay_event_log['topics'][1].hex()[-40:],
                "0x" + relay_event_log['topics'][2].hex()[-40:],
                int(relay_event_log['data'][2:66], 16),
                relay_event_log['transactionHash'].hex(),
                CHAIN_CONFIG['gas'], CHAIN_CONFIG['gasPrice']
            ))
        mock_apply_relay.assert_has_calls(apply_relay_calls)

        # Assert DynamoDB's value
        get_item_result = self.db_table.get_item(Key={
            'key': "public_to_private_offset"
        })
        self.assertEqual(
            int(get_item_result['Item']['value']), LATEST_BLOCK_NUMBER + 1)

    @patch('src.contract.get_relay_event_log_by_tx_hash')
    @patch('src.contract.apply_relay')
    def test_ok_execute_apply_relay_by_tx_hashes(self, mock_apply_relay, mock_get_relay_event_log_by_tx_hash):
        # Setup mock
        mock_apply_relay.return_value = '0x' + 'a' * 64

        def relay_event_log_side_effect(provider, hash):
            for log in relay_event_logs:
                if log['transactionHash'].hex() == hash:
                    return log
            return None
        mock_get_relay_event_log_by_tx_hash.side_effect = relay_event_log_side_effect

        # Execute
        relay_transactions = [log['transactionHash'].hex()
                              for log in relay_event_logs]
        execute_apply_relay_by_tx_hashes(
            CHAIN_CONFIG, PRIVATE_KEY, relay_transactions)

        # Assert call count
        self.assertEqual(
            mock_apply_relay.call_count, len(relay_event_logs))

        # Assert parameters
        apply_relay_calls = []
        for relay_event_log in relay_event_logs:
            apply_relay_calls.append(call(
                ANY,
                CHAIN_CONFIG['bridgeContractAddressTo'],
                PRIVATE_KEY,
                "0x" + relay_event_log['topics'][1].hex()[-40:],
                "0x" + relay_event_log['topics'][2].hex()[-40:],
                int(relay_event_log['data'][2:66], 16),
                relay_event_log['transactionHash'].hex(),
                CHAIN_CONFIG['gas'], CHAIN_CONFIG['gasPrice']
            ))
        mock_apply_relay.assert_has_calls(apply_relay_calls)

    @patch('src.contract.get_relay_event_logs')
    @patch('src.contract.get_apply_relay_event_logs')
    @patch('src.notification_util.notify_pending_relays')
    def test_ok_execute_detect_pending_relay(self, mock_notify_pending_relays, mock_get_apply_relay_event_logs, mock_get_relay_event_logs):
        # Setup mock
        mock_get_relay_event_logs.return_value = relay_event_logs
        mock_get_apply_relay_event_logs.return_value = apply_relay_event_logs

        # Execute
        execute_detect_pending_relay(CHAIN_CONFIG, True, 1, 1, 0)

        # Assert call count and parameters
        parsed_relay_event = parse_relay_event_log(relay_event_logs[2])
        mock_notify_pending_relays.assert_called_once_with(True, [{'sender': parsed_relay_event['sender'],
                                                                   'recipient': parsed_relay_event['recipient'],
                                                                   'amount': parsed_relay_event['amount'],
                                                                   'fee': parsed_relay_event['fee'],
                                                                   'timestamp': parsed_relay_event['timestamp'],
                                                                   'txHash': parsed_relay_event['txHash'],
                                                                   'blockNumber': parsed_relay_event['blockNumber']}], 1, 1)
