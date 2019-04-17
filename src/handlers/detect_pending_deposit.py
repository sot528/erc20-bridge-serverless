import os
from src.services import detect_pending_relay
from src.handlers.helpers import helper


def handler(event, content):
    """ 未完了の入金処理の検出
    """
    detect_pending_relay.execute(helper.load_chain_config(True),
                                 event['notificationEnabled'],
                                 int(os.environ['RELAY_FROM_BLOCK_NUM']),
                                 int(os.environ['APPLY_RELAY_FROM_BLOCK_NUM']),
                                 int(os.environ['RELAY_IGNORE_SEC_THRESHOLD']))
