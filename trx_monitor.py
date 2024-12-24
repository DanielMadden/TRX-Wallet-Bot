import hmac
import hashlib
from tronpy.keys import PrivateKey
from tronpy import Tron
from mnemonic import Mnemonic

# Constants for BIP-44 path and derivation
TRON_COIN_TYPE = 195  # Tron-specific BIP-44 coin type

def derive_private_key_from_mnemonic(mnemonic_phrase: str) -> PrivateKey:
    """
    Derive a Tron private key from a mnemonic phrase using BIP-44 standards.
    """
    # Generate seed from the mnemonic phrase
    m = Mnemonic("english")
    seed = m.to_seed(mnemonic_phrase)

    # Define the derivation path: m/44'/195'/0'/0/0
    path = "m/44'/195'/0'/0/0"

    # Perform key derivation based on the path
    master_key = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
    private_key = master_key[:32]  # Take the first 32 bytes as the private key

    return PrivateKey(private_key)


# Replace this with your mnemonic phrase from secrets.py
from mysecrets import MNEMONIC_PHRASE

# Initialize the Tron client
client = Tron()

# Derive the private key from the mnemonic phrase
private_key = derive_private_key_from_mnemonic(MNEMONIC_PHRASE)

# Wallet address derived from the private key
wallet_address = private_key.public_key.to_base58check_address()

# Target wallet for funds
target_wallet = "TGfJJ3o5e4eK9P8jZnFJSzJHUHGQeC2mpR"

# Minimum TRX balance required to cover fees
required_trx = 15

def get_balance(address: str) -> float:
    """
    Get TRX balance in a wallet.
    """
    account_info = client.get_account(address)
    balance_sun = account_info.get("balance", 0)  # In SUN
    return balance_sun / 1_000_000  # Convert SUN to TRX

def withdraw_usdt():
    """
    Withdraw all USDT to the target wallet.
    """
    usdt_contract = client.get_contract("TLa2f6VPqDgRE67v1736s7bJ8Ray5wYjU7")
    usdt_balance_sun = usdt_contract.functions.balanceOf(wallet_address)
    usdt_balance = usdt_balance_sun / 1_000_000

    if usdt_balance > 0:
        txn = (
            usdt_contract.functions.transfer(target_wallet, usdt_balance_sun)
            .with_owner(wallet_address)
            .fee_limit(100_000_000)
            .build()
            .sign(private_key)
        )
        tx_hash = txn.broadcast().txid
        print(f"USDT transfer initiated! Transaction hash: {tx_hash}")
    else:
        print("No USDT balance to withdraw.")

        from tronpy.exceptions import AddressNotFound  # Import AddressNotFound

from tronpy.exceptions import AddressNotFound  # Import AddressNotFound

def monitor_wallet():
    """
    Continuously monitor the wallet. If TRX >= required_trx, withdraw all USDT.
    """
    wallet_address = private_key.public_key.to_base58check_address()
    print(f"Monitoring wallet address: {wallet_address}")

    while True:
        try:
            trx_balance = get_balance(wallet_address)
            print(f"Current TRX balance: {trx_balance:.6f} TRX")

            # Check if there's enough TRX to cover fees
            if trx_balance >= required_trx:
                print("Sufficient TRX detected. Proceeding with withdrawal...")
                withdraw_usdt()
                break  # Stop monitoring after one successful withdrawal
        except AddressNotFound:
            print("Wallet address not found on-chain. Make sure it has been activated with a transaction.")
            break  # Exit the loop if the address is not valid
        except Exception as e:
            print(f"Error: {e}")

        # Poll every 5 seconds to avoid rate limits
        time.sleep(5)



if __name__ == "__main__":
    monitor_wallet()
