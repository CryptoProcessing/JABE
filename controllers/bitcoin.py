import io
import bitcoin.rpc
from bitcoin import SelectParams
from pycoin.block import Block
from pycoin.serialize import h2b, b2h_rev
from tenacity import retry, stop_after_attempt

SelectParams("testnet")


class MyProxy(bitcoin.rpc.Proxy):

    def decoderawtransaction(self, hexstring, verbose=False):
        """Return transaction with hash txid

        Raises IndexError if transaction not found.

        verbose - If true a dict is returned instead with additional
        information on the transaction.

        Note that if all txouts are spent and the transaction index is not
        enabled the transaction may not be available.
        """
        try:
            r = self._call('decoderawtransaction', hexstring)
        except bitcoin.rpc.InvalidAddressOrKeyError as ex:
            raise IndexError('%s.decoderawtransaction(): %s (%d)' %
                    (self.__class__.__name__, ex.error['message'], ex.error['code']))
        return r

    def get_raw_block(self, block_hash):
        """Get block <block_hash>

        Raises IndexError if block_hash is not valid.
        """
        try:
            block_hash = bitcoin.rpc.b2lx(block_hash)
        except TypeError:
            raise TypeError('%s.getblock(): block_hash must be bytes; got %r instance' %
                            (self.__class__.__name__, block_hash.__class__))
        try:
            r = self._call('getblock', block_hash, False)
            return r
        except bitcoin.rpc.InvalidAddressOrKeyError as ex:
            raise IndexError('%s.getblock(): %s (%d)' %
                             (self.__class__.__name__, ex.error['message'], ex.error['code']))


@retry
def get_block(block):
    """
    Get block by hash
    :param block:
    :return:
    """
    mrpc = MyProxy()

    try:
        blockinfo = mrpc.get_raw_block(bitcoin.rpc.lx(block))
        block_header = mrpc.getblockheader(bitcoin.rpc.lx(block), True)
        if block_header:
            block_height = block_header['height']
        else:
            block_height = None
    except TimeoutError as e:
        raise e

    block_data = h2b(blockinfo)
    block_object = Block.parse(io.BytesIO(block_data))

    return block_object, block_height


@retry
def get_block_hash(block_number):
    """
    Get block hash by number
    :param block_number:
    :return:
    """
    mrpc = MyProxy()

    try:
        block_hash = mrpc.getblockhash(block_number)
        return b2h_rev(block_hash)

    except TimeoutError as e:
        raise e


@retry
def get_blockcount():
    """
    :return:
    """
    mrpc = MyProxy()

    try:
        blockcount = mrpc.getblockcount()
        return blockcount

    except TimeoutError as e:
        raise e


