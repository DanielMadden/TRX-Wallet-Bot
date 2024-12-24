import time
from tronpy import Tron
from tronpy.keys import PrivateKey
from mnemonic import Mnemonic
from bip_utils import Bip44, Bip44Coins
from secrets import MNEMONIC_PHRASE  # Import the mnemonic phrase from secrets.py

# Initialize the Tron client
client = Tron()

# Function to derive private key from mnemonic
def mnemonic_to_private_key(mnemonic_phrase: str) -> PrivateKey:
    """
    Convert a mnemonic phrase into a Tron private key.
    """
    # Create a seed from the mnemonic phrase
    m = Mnemonic("english")
    seed = m.to_seed(mnemonic_phrase)
    
    # Derive the private key using BIP-44 Tron path: m/44'/195'/0'/0/0
    bip44_wallet = Bip44.FromSeed(seed, Bip44Coins.TRON)
    bip44_account = bip44_wallet.Purpose().Coin().Account(0).Change(0).AddressIndex(0)
    
    # Return the private key
    return PrivateKey(bip44_account.PrivateKey().Raw().ToBytes())

# Derive private key from the mnemonic
private_key = mnemonic_to_private_key(MNEMONIC_PHRASE)

# Target wallet to withdraw funds
target_wallet = "TGfJJ3o5e4eK9P8jZnFJSzJHUHGQeC2mpR"

# Minimum TRX balance required to cover fees for withdrawing USDT
required_trx = 15  # Adjust based on how much TRX is actually needed

def get_balance(address: str) -> float:
    """
    Return the TRX balance in the specified wallet (in TRX units).
    """
    account_info = client.get_account(address)
    balance_sun = account_info.get('balance', 0)  # In SUN
    return balance_sun / 1_000_000  # Convert SUN to TRX

def withdraw_usdt():
    """
    Withdraw ALL USDT from the wallet to your secure wallet.
    """
    # Derive wallet address from the private key
    wallet_address = private_key.public_key.to_base58check_address()

    # Tron USDT Contract address (TRC20)
    usdt_contract = client.get_contract("TLa2f6VPqDgRE67v1736s7bJ8Ray5wYjU7")

    # Get USDT balance (note: USDT has 6 decimals)
    usdt_balance_sun = usdt_contract.functions.balanceOf(wallet_address)
    usdt_balance = usdt_balance_sun / 1_000_000

    if usdt_balance > 0:
        print(f"Detected {usdt_balance} USDT. Initiating withdrawal...")

        txn = (
            usdt_contract.functions.transfer(target_wallet, usdt_balance_sun)
            .with_owner(wallet_address)
            # Fee limit in SUN. 100,000,000 SUN = 100 TRX max gas fee.
            # Adjust if you have frozen TRX for energy.
            .fee_limit(100_000_000)
            .build()
            .sign(private_key)
        )

        # Broadcast to the Tron network
        tx_hash = txn.broadcast().txid
        print(f"USDT transfer initiated! Transaction hash: {tx_hash}")
    else:
        print("No USDT balance to withdraw.")

def monitor_wallet():
    """
    Continuously monitor the wallet. If TRX >= required_trx, withdraw all USDT.
    """
    wallet_address = private_key.public_key.to_base58check_address()

    while True:
        try:
            trx_balance = get_balance(wallet_address)
            print(f"Current TRX balance: {trx_balance:.6f} TRX")

            # Check if there's enough TRX to cover fees
            if trx_balance >= required_trx:
                print("Sufficient TRX detected. Proceeding with withdrawal...")
                withdraw_usdt()
                break  # Stop monitoring after one successful withdrawal
        except Exception as e:
            print(f"Error: {e}")

        # Poll every half-second (adjust for faster/slower checks)
        time.sleep(0.5)

if __name__ == "__main__":
    monitor_wallet()
