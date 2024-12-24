import time
from tronpy import Tron
from tronpy.keys import PrivateKey
from tronpy.exceptions import AddressNotFound
from mysecrets import PRIVATE_KEY_HEX
from tronpy.providers import HTTPProvider
from mysecrets import API_KEYS

# 1. Initialize Tron client
client = Tron(provider=HTTPProvider(api_key=API_KEYS))

# 2. Construct the PrivateKey object from your hex string
private_key = PrivateKey(bytes.fromhex(PRIVATE_KEY_HEX))

# 3. Derive the wallet address from the private key
wallet_address = private_key.public_key.to_base58check_address()

# 4. Target wallet where you want to send USDT
target_wallet = "TGfJJ3o5e4eK9P8jZnFJSzJHUHGQeC2mpR"

# 5. Minimum TRX balance needed to cover fees (adjust as needed)
required_trx = 15

def get_balance(address: str) -> float:
    """
    Return the TRX balance (in TRX units) of the specified wallet address.
    """
    account_info = client.get_account(address)
    balance_sun = account_info.get("balance", 0)  # 'balance' in SUN
    return balance_sun / 1_000_000  # convert SUN to TRX

def withdraw_usdt():
    """
    Withdraw ALL USDT from the current wallet to the target wallet.
    """
    # Official Tether USDT TRC20 contract on Tron
    usdt_contract = client.get_contract("TLa2f6VPqDgRE67v1736s7bJ8Ray5wYjU7")

    # Get USDT balance in SUN (contract uses 6 decimal places)
    usdt_balance_sun = usdt_contract.functions.balanceOf(wallet_address)
    usdt_balance = usdt_balance_sun / 1_000_000

    if usdt_balance > 0:
        print(f"Detected {usdt_balance} USDT. Initiating withdrawal...")
        txn = (
            usdt_contract.functions.transfer(target_wallet, usdt_balance_sun)
            .with_owner(wallet_address)
            # fee_limit is in SUN (1 TRX = 1_000_000 SUN).
            # 100_000_000 = 100 TRX as a max fee buffer (adjust as desired).
            .fee_limit(100_000_000)
            .build()
            .sign(private_key)
        )

        tx_hash = txn.broadcast().txid
        print(f"USDT transfer initiated! Transaction hash: {tx_hash}")
    else:
        print("No USDT balance to withdraw.")

def monitor_wallet():
    """
    Continuously monitor the wallet for sufficient TRX; if reached, withdraw USDT.
    """
    print(f"Monitoring wallet: {wallet_address}")

    while True:
        try:
            trx_balance = get_balance(wallet_address)
            print(f"Current TRX balance: {trx_balance:.6f} TRX")

            if trx_balance >= required_trx:
                print("Sufficient TRX detected. Proceeding with withdrawal...")
                withdraw_usdt()
                break  # stop after one successful withdrawal
        except AddressNotFound:
            print("Wallet address not found on-chain. Fund it with some TRX first.")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")

        # Poll every 15 seconds (adjust to avoid daily limits)
        time.sleep(15)

if __name__ == "__main__":
    monitor_wallet()
