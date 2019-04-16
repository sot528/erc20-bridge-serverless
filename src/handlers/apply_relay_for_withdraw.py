from src import operator
from src.handlers.helpers import helper


def handler(event, content):
    """ Relayイベントのトランザクションハッシュを指定して出金処理を実行(未完了の出金処理をリトライする際に利用)
    """
    operator.execute_apply_relay_by_tx_hashes(helper.load_chain_config(False), helper.get_private_key(
        False), event['relayTransactions'])
