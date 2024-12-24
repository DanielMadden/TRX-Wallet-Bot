import time
from bip_utils import (
    Bip39SeedGenerator,
    Bip44,
    Bip44Coins,
    Bip44Changes
)
from tronpy import Tron
from tronpy.keys import PrivateKey
from mnemonic import Mnemonic
from tronpy.exceptions import AddressNotFound

# 1. Your 12/24-word mnemonic phrase (BIP39)
MNEMONIC_PHRASE = "replace this with your actual mnemonic words"

# 2. Derive a Tron private key from the mnemonic phrase using bip_utils
def derive_tron_private_key(mnemonic_phrase: str) -> PrivateKey:
    """
    Derive a Tron (TRC20) private key from a BIP39 mnemonic using bip_utils BIP44 approach.
    Path: m/44'/195'/0'/0/0
    """
    # Generate seed from mnemonic
    seed_bytes = Bip39SeedGenerator(mnemonic_phrase).Generate()

    # Create a BIP44 master context for Tron
    bip44_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.TRON)

    # Derive the first address: m/44'/195'/0'/0/0
    account = (
        bip44_ctx
        .Purpose()
        .Coin()
        .Account(0)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(0)
    )

    # Extract the raw private key bytes
    private_key_bytes = account.PrivateKey().Raw().ToBytes()
    # Wrap in tronpy's PrivateKey object
    return PrivateKey(private_key_bytes)

# 3. Initialize Tron client and your derived key
client = Tron()
private_key = derive_tron_private_key(MNEMONIC_PHRASE)
wallet_address = private_key.public_key.to_base58check_address()

print(f"Derived Tron Wallet Address: {wallet_address}")

# 4. Monitoring and withdrawal parameters
target_wallet = "TGfJJ3o5e4eK9P8jZnFJSzJHUHGQeC2mpR"  # Where to send USDT
required_trx = 15  # Minimum TRX needed to cover fees (adjust as needed)

def get_balance(address: str) -> float:
    """
    Get TRX balance (in TRX units) of a given address.
    """
    account_info = client.get_account(address)
    balance_sun = account_info.get("balance", 0)  # in SUN
    return balance_sun / 1_000_000  # Convert to TRX

def withdraw_usdt():
    """
    Withdraw all USDT from this wallet to the target wallet.
    """
    usdt_contract = client.get_contract("TLa2f6VPqDgRE67v1736s7bJ8Ray5wYjU7")  # Official TRC20-USDT
    usdt_balance_sun = usdt_contract.functions.balanceOf(wallet_address)
    usdt_balance = usdt_balance_sun / 1_000_000  # USDT has 6 decimals

    if usdt_balance > 0:
        print(f"Detected {usdt_balance} USDT. Initiating withdrawal...")

        txn = (
            usdt_contract.functions.transfer(target_wallet, usdt_balance_sun)
            .with_owner(wallet_address)
            # fee_limit is in SUN. 100_000_000 = 100 TRX max fee allowance.
            .fee_limit(100_000_000)
            .build()
            .sign(private_key)
        )

        # Broadcast the transaction
        tx_hash = txn.broadcast().txid
        print(f"USDT transfer initiated! Transaction hash: {tx_hash}")
    else:
        print("No USDT balance to withdraw.")

def monitor_wallet():
    """
    Monitor the wallet; if TRX >= required_trx, withdraw USDT once.
    """
    print(f"Monitoring wallet: {wallet_address}")
    while True:
        try:
            trx_balance = get_balance(wallet_address)
            print(f"Current TRX balance: {trx_balance:.6f} TRX")

            if trx_balance >= required_trx:
                print("Sufficient TRX detected. Proceeding with withdrawal...")
                withdraw_usdt()
                break  # Stop after one withdrawal
        except AddressNotFound:
            print("Address not found on-chain. Fund the address with some TRX first.")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")

        time.sleep(5)  # Wait 5 seconds before checking again

# 5. Main entry point
if __name__ == "__main__":
    monitor_wallet()
