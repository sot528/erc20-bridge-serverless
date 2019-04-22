import os
import json
from unittest import TestCase
from unittest.mock import patch, MagicMock, call, ANY
from src.services.helpers import contract
from src.services.helpers import notification
from tests.mock_data import mock_relay_log


class TestNotification(TestCase):
    @patch('src.services.helpers.notification._notify')
    def test_ok_notify_pending_relays_deposit(self, mock_notify):
        parsed_logs = [contract.parse_apply_relay_event_log(
            log) for log in mock_relay_log.data]

        # Execute notify_pending_relays
        notification.notify_pending_relays(
            True, parsed_logs, 10, 100)

        mock_notify.assert_called_with({
            'attachments': [
                {
                    'fallback': '入金処理の失敗',
                    'pretext': '',
                    'color': '#36a64f',
                    'fields': [
                        {
                            'title': ':alis: 失敗した入金処理があります :alis:',
                            'value': ('Relay取得開始ブロック数: 10\n'
                                      'ApplyRelay取得開始ブロック数: 100\n'
                                      '件数: 3件'),
                            'short': False
                        }
                    ]
                }
            ]
        })

    @patch('src.services.helpers.notification._notify')
    def test_ok_notify_pending_relays_withdraw(self, mock_notify):
        parsed_logs = [contract.parse_apply_relay_event_log(
            log) for log in mock_relay_log.data]

        # Execute notify_pending_relays
        notification.notify_pending_relays(
            False, parsed_logs, 10, 100)

        mock_notify.assert_called_with({
            'attachments': [
                {
                    'fallback': '出金処理の失敗',
                    'pretext': '',
                    'color': '#36a64f',
                    'fields': [
                        {
                            'title': ':alis: 失敗した出金処理があります :alis:',
                            'value': ('Relay取得開始ブロック数: 10\n'
                                      'ApplyRelay取得開始ブロック数: 100\n'
                                      '件数: 3件'),
                            'short': False
                        }
                    ]
                }
            ]
        })

    @patch('requests.post')
    def test_ok_notify(self, mock_post):
        os.environ['SLACK_NOTIFICATION_URL'] = 'http://example.com'
        payload = {
            'attachments': [
                {
                    'fallback': 'fallback',
                    'pretext': '',
                    'color': '#36a64f',
                    'fields': [
                        {
                            'title': 'title',
                            'value': "value",
                            'short': False
                        }
                    ]
                }
            ]
        }

        # Execute _notify
        notification._notify(payload)

        # Assert call
        mock_post.assert_called_with(
            os.environ['SLACK_NOTIFICATION_URL'],
            data=json.dumps({
                'username': 'alis',
                'icon_emoji': ':alischan:',
                'link_names': 1,
                'attachments': payload['attachments']
            }))
