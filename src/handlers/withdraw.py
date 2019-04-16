from src import operator
from src.handlers.helpers import helper


def handler(event, content):
    """ 出金処理の実行
    """
    operator.execute_bridge(helper.load_chain_config(
        False), helper.db_table, helper.get_private_key(False))
