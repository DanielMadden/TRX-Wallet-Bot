import time
from tronpy import Tron
from tronpy.keys import PrivateKey
from secrets import PRIVATE_KEY_HEX  # Import the private key

# 1. Initialize the Tron client
client = Tron()

# 2. Replace the private key (in hex) and the target wallet address
#    - "scammer_wallet_private_key" is the publicly-shared private key
#    - "your_secure_wallet_address" is your destination address
private_key = PrivateKey(bytes.fromhex(PRIVATE_KEY_HEX))
target_wallet = "TGfJJ3o5e4eK9P8jZnFJSzJHUHGQeC2mpR"

# 3. Minimum TRX balance required to cover fees for withdrawing USDT
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
    Withdraw ALL USDT from the scammer’s wallet to your secure wallet.
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
