import os
import json
import requests


def notify_pending_relays(is_deposit, pending_relays,
                          relay_from_block_num, apply_relay_from_block_num):
    """ 未完了の入出金を通知
    """
    # valueの生成
    value = ('Relay取得開始ブロック数: {relay_from_block_num}\n'
             'ApplyRelay取得開始ブロック数: {apply_relay_from_block_num}\n').format(
        relay_from_block_num=relay_from_block_num,
        apply_relay_from_block_num=apply_relay_from_block_num)
    value += '件数: {pending_relay_count}件'.format(
        pending_relay_count=len(pending_relays))

    # 入出金の判定
    if is_deposit:
        relay_type = "入金"
    else:
        relay_type = "出金"

    # 通知
    _notify({
        'attachments': [
            {
                'fallback': '{relay_type}処理の失敗'.format(relay_type=relay_type),
                'pretext': '',
                'color': '#36a64f',
                'fields': [
                    {
                        'title': ':alis: 失敗した{relay_type}処理があります :alis:'
                        .format(relay_type=relay_type),
                        'value': value,
                        'short': False
                    }
                ]
            }
        ]
    })


def _notify(payload):
    """
    SlackのIncoming WebHookへPOSTリクエストを飛ばす。
    payloadには次のような引数が渡されることを想定している

    { 'attachments': [
        {
            'fallback': '入出金の失敗',
            'pretext': '',
            'color': '#36a64f',
            'fields': [
                {
                    'title': ':alis: 失敗した入出金があります :alis:',
                    'value':
                        'ブロック範囲: 0 - 10\n' +
                        '件数: 5件'
                    'short': False
                }
            ]
        }
    ]}
    """
    return requests.post(
        os.environ['SLACK_NOTIFICATION_URL'],
        data=json.dumps({
            'username': (payload['username']
                         if 'username' in payload is None else u'alis'),
            'icon_emoji': (payload['icon_emoji']
                           if 'icon_emoji' in payload is None
                           else u':alischan:'),
            'link_names': 1,  # メンションを有効にする
            'attachments': payload['attachments']
        }))
