import time
from tronpy import Tron
from tronpy.providers import HTTPProvider
from tronpy.keys import PrivateKey
from tronpy.exceptions import AddressNotFound, TransactionError, TronError
from my_secrets import PRIVATE_KEY_HEX, API_KEYS

def test_usdt_transfer():
    """
    Attempts a single USDT transfer from the private key's wallet
    to the target wallet address, ignoring TRX balance checks.
    """
    # 1. Initialize Tron client with multiple API keys (if you have them)
    client = Tron(provider=HTTPProvider(api_key=API_KEYS))

    # 2. Construct the PrivateKey object from your hex string
    private_key = PrivateKey(bytes.fromhex(PRIVATE_KEY_HEX))

    # 3. Get the wallet address
    wallet_address = private_key.public_key.to_base58check_address()

    # 4. The target wallet for the USDT
    target_wallet = "TGfJJ3o5e4eK9P8jZnFJSzJHUHGQeC2mpR"

    print(f"Attempting USDT transfer from {wallet_address} to {target_wallet}...")

    try:
        # 5. Get the USDT contract on Tron
        usdt_contract = client.get_contract("TLa2f6VPqDgRE67v1736s7bJ8Ray5wYjU7")

        # 6. Fetch USDT balance of this wallet
        usdt_balance_sun = usdt_contract.functions.balanceOf(wallet_address)
        usdt_balance = usdt_balance_sun / 1_000_000  # Convert to human-readable USDT

        print(f"Current USDT balance: {usdt_balance} USDT")

        if usdt_balance > 0:
            print("Building and broadcasting USDT transfer transaction...")
            txn = (
                usdt_contract.functions.transfer(target_wallet, usdt_balance_sun)
                .with_owner(wallet_address)
                # fee_limit is in SUN. 100,000,000 SUN = 100 TRX max fee.
                .fee_limit(100_000_000)
                .build()
                .sign(private_key)
            )

            # 7. Broadcast the transaction
            tx_hash = txn.broadcast().txid
            print(f"Transaction broadcast! TX hash: {tx_hash}")

        else:
            print("No USDT to transfer. Transfer aborted.")

    except AddressNotFound:
        print("Error: Wallet address not found on-chain. Make sure it has at least 1 TRX transaction.")
    except TransactionError as tx_err:
        print(f"TransactionError: {tx_err}")
    except TronError as tron_err:
        print(f"TronError: {tron_err}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    test_usdt_transfer()
