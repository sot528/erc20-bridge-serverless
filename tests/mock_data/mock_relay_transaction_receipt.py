from hexbytes import HexBytes
from attrdict import AttrDict as AttributeDict

data = AttributeDict({
    'transactionHash': HexBytes(
        '0x95d127f4c1b5a78146de49656360674803390196300c6aef537c8fcd31e56a27'),
    'transactionIndex': 0,
    'blockHash': HexBytes(
        '0xed60a6c7da38092a35bfb3802a30704ec3f01ec38fe3c97d9ef36efcca8be949'),
    'blockNumber': 7,
    'from': '0x39b8ee32b47444995e9ece77db091952d63d0507',
    'to': '0xb35a7a53fb70c8be7bc7faf0c57a83982f2f329c',
    'gasUsed': 63050,
    'cumulativeGasUsed': 63050,
    'contractAddress': None,
    'logs': [
        AttributeDict({
            'logIndex': 0,
            'transactionIndex': 0,
            'transactionHash': HexBytes(
                '0x95d127f4c1b5a78146de496563606748'
                '03390196300c6aef537c8fcd31e56a27'),
            'blockHash': HexBytes('0xed60a6c7da38092a35bfb3802a30704'
                                  'ec3f01ec38fe3c97d9ef36efcca8be949'),
            'blockNumber': 7,
            'address': '0x0531be32b85FEd81e13e61004E32FAAe4aE66E98',
            'data': ('0x00000000000000000000000000000000'
                     '0000000000000000000000000000000a'),
            'topics': [
                HexBytes(
                    '0xddf252ad1be2c89b69c2b068fc378d'
                    'aa952ba7f163c4a11628f55a4df523b3ef'),
                HexBytes(
                    '0x00000000000000000000000039b8ee'
                    '32b47444995e9ece77db091952d63d0507'),
                HexBytes(
                    '0x000000000000000000000000b35a7a'
                    '53fb70c8be7bc7faf0c57a83982f2f329c')
            ],
            'type': 'mined'
        }),
        AttributeDict({
            'logIndex': 1,
            'transactionIndex': 0,
            'transactionHash': HexBytes(
                '0x95d127f4c1b5a78146de496563606748'
                '03390196300c6aef537c8fcd31e56a27'),
            'blockHash': HexBytes(
                '0xed60a6c7da38092a35bfb3802a30704e'
                'c3f01ec38fe3c97d9ef36efcca8be949'),
            'blockNumber': 7,
            'address': '0xB35A7A53fB70C8bE7BC7faf0c57a83982F2F329c',
            'data': ('0x00000000000000000000000000000000'
                     '00000000000000000000000000000005'
                     '00000000000000000000000000000000'
                     '00000000000000000000000000000005'
                     '00000000000000000000000000000000'
                     '0000000000000000000000005cb7da7d'),
            'topics': [
                HexBytes(
                    '0xb77c820b3a0ee4da03c984a58bfe43cb'
                    '27cd3297d424e1025014ce0b7de08cc4'),
                HexBytes(
                    '0x000000000000000000000000'
                    '39b8ee32b47444995e9ece77db091952d63d0507'),
                HexBytes(
                    '0x000000000000000000000000'
                    '1111111111111111111111111111111111111111')
            ],
            'type': 'mined'
        })
    ],
    'status': 1,
    'logsBloom': HexBytes('0x00000000000000000000000000000000'
                          '00000000000000000000000000000000'
                          '00000000000000000000000000020000'
                          '00000000000000040000000000000000'
                          '00000000000000000000000800000000'
                          '00000000000000000000080000000000'
                          '00000000000000000000000000000000'
                          '00000000000000000000001000000010'
                          '00000000000000000000000000000000'
                          '00000000000000100000000000000000'
                          '00000000000000010000000000000000'
                          '00000000000000000000000000000000'
                          '00000002000000000000080000000010'
                          '00000000100008000000000000200000'
                          '00000400004000020000000000000000'
                          '00000000000000000000000000000010'),
    'v': '0x1c',
    'r': '0xd490a4a0cd94ca0a56fa3663bdb5197d076e7d02276553c3d1aeb74e98540b1b',
    's': '0x3c3433956baf6c97d139b104984184c3c88c6b5ea090c382a09e342e3a40ace6'})
