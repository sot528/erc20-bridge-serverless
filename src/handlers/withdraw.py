from src.services import bridge
from src.handlers.helpers import helper


def handler(event, content):
    """ 出金処理の実行
    """
    bridge.execute(helper.load_chain_config(
        False), helper.get_db_table(), helper.get_private_key(False))
