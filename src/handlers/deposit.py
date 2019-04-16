from src import operator
from src.handlers.helpers import helper


def handler(event, context):
    """ 入金処理の実行
    """
    operator.execute_bridge(helper.load_chain_config(True),
                            helper.db_table, helper.get_private_key(True))
