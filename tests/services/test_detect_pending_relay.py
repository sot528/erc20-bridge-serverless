from web3 import Web3
from unittest import TestCase
from unittest.mock import patch, MagicMock, call, ANY
from src.services import detect_pending_relay
from src.services.helpers import contract
from tests import helper
from tests.mock_data import mock_relay_log
from tests.mock_data import mock_apply_relay_log


class TestDetectPendingRelay(TestCase):

    @patch('src.services.helpers.contract.get_relay_event_logs')
    @patch('src.services.helpers.contract.get_apply_relay_event_logs')
    @patch('src.services.helpers.notification.notify_pending_relays')
    def test_ok_detect_pending_relay(self, mock_notify_pending_relays,
                                     mock_get_apply_relay_event_logs,
                                     mock_get_relay_event_logs):
        # Setup mock
        mock_get_relay_event_logs.return_value \
            = mock_relay_log.data
        mock_get_apply_relay_event_logs.return_value \
            = mock_apply_relay_log.data

        # Execute
        detect_pending_relay.execute(helper.CHAIN_CONFIG, True, 1, 1, 0)

        # Assert call count and parameters
        mock_get_apply_relay_event_logs_args \
            = mock_get_apply_relay_event_logs.call_args[0]
        self.assertEqual(
            mock_get_apply_relay_event_logs_args[0].endpoint_uri,
            helper.CHAIN_CONFIG['chainRpcUrlTo'])
        self.assertEqual(
            mock_get_apply_relay_event_logs_args[1],
            helper.CHAIN_CONFIG['bridgeContractAddressTo'])
        self.assertEqual(
            mock_get_apply_relay_event_logs_args[2], 1)

        parsed_relay_event = contract.parse_relay_event_log(
            mock_relay_log.data[2])
        mock_notify_pending_relays.assert_called_once_with(
            True,
            [{'sender': parsed_relay_event['sender'],
              'recipient': parsed_relay_event['recipient'],
              'amount': parsed_relay_event['amount'],
              'fee': parsed_relay_event['fee'],
              'timestamp': parsed_relay_event['timestamp'],
              'txHash': parsed_relay_event['txHash'],
              'blockNumber': parsed_relay_event['blockNumber']}], 1, 1)
