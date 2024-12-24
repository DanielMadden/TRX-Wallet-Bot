import time
from tronpy import Tron
from tronpy.keys import PrivateKey
from tronpy.exceptions import AddressNotFound
from tronpy.providers import HTTPProvider
from my_secrets import PRIVATE_KEY_HEX, API_KEYS

# 1. Initialize Tron client
print("Initializing Tron client...")
client = Tron(provider=HTTPProvider(api_key=API_KEYS))

# 2. Construct the PrivateKey object from your hex string
print("Constructing private key...")
private_key = PrivateKey(bytes.fromhex(PRIVATE_KEY_HEX))

# 3. Derive the wallet address from the private key
wallet_address = private_key.public_key.to_base58check_address()
print(f"Wallet address derived: {wallet_address}")

# 4. Target wallet where you want to send USDT
target_wallet = "TGfJJ3o5e4eK9P8jZnFJSzJHUHGQeC2mpR"
print(f"Target wallet address: {target_wallet}")

# 5. Minimum TRX balance needed to cover fees (adjust as needed)
required_trx = 15

def withdraw_usdt():
    """
    Withdraw ALL USDT from the current wallet to the target wallet.
    """
    try:
        print("Fetching USDT contract...")
        # Official Tether USDT TRC20 contract on Tron
        usdt_contract = client.get_contract("TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t")
        print(dir(usdt_contract.functions))
        # print(usdt_contract.functions.balanceOf.call)


        print("Accessing balanceOf function...")
        balance_of_func = usdt_contract.functions["balanceOf"]
        print(f"balanceOf function: {balance_of_func}, Type: {type(balance_of_func)}")

        print(f"Calling balanceOf for wallet: {wallet_address}...")
        usdt_balance_sun = balance_of_func(wallet_address)
        print(f"Raw USDT balance (in SUN): {usdt_balance_sun}, Type: {type(usdt_balance_sun)}")

        # Convert to USDT units
        usdt_balance = usdt_balance_sun / 1_000_000
        print(f"USDT balance: {usdt_balance}")

        if usdt_balance > 0:
            print(f"Detected {usdt_balance} USDT. Initiating withdrawal...")
            txn = (
                usdt_contract.functions["transfer"](target_wallet, usdt_balance_sun)
                .with_owner(wallet_address)
                .fee_limit(100_000_000)  # Adjust fee as needed
                .build()
                .sign(private_key)
            )

            print("Broadcasting transaction...")
            tx_hash = txn.broadcast().txid
            print(f"USDT transfer initiated! Transaction hash: {tx_hash}")
        else:
            print("No USDT balance to withdraw.")

    except Exception as e:
        print(f"Error during withdrawal: {e}")

# Additional debugging for TRX balance (optional)
def get_balance(address: str) -> float:
    """
    Return the TRX balance (in TRX units) of the specified wallet address.
    """
    try:
        print(f"Fetching TRX balance for address: {address}...")
        account_info = client.get_account(address)
        print(f"Account info: {account_info}")

        balance_sun = account_info.get("balance", 0)  # 'balance' in SUN
        trx_balance = balance_sun / 1_000_000  # convert SUN to TRX
        print(f"TRX balance: {trx_balance}")
        return trx_balance
    except AddressNotFound:
        print("Wallet address not found on-chain.")
        return 0.0
    except Exception as e:
        print(f"Unexpected error when fetching TRX balance: {e}")
        return 0.0

withdraw_usdt()

# Optional: Monitor wallet for sufficient TRX balance
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
        except Exception as e:
            print(f"Unexpected error during monitoring: {e}")

        # Poll every 15 seconds (adjust to avoid hitting daily limits)
        time.sleep(15)

# Uncomment to enable monitoring
# if __name__ == "__main__":
#     monitor_wallet()
