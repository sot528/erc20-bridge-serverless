from src.services import bridge
from src.handlers.helpers import helper


def handler(event, context):
    """ 入金処理の実行
    """
    bridge.execute(helper.load_chain_config(True),
                   helper.db_table, helper.get_private_key(True))
