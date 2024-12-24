# test_pull_usdt.py

from tronpy import Tron
from tronpy.keys import PrivateKey
from tronpy.providers import HTTPProvider
from tronpy.exceptions import AddressNotFound
from my_secrets import PRIVATE_KEY_HEX, API_KEYS
import json

# --- Configuration ---

# Initialize Tron client using API_KEYS from my_secrets
client = Tron(provider=HTTPProvider(api_key=API_KEYS))

# Construct the PrivateKey object from your hex string
private_key = PrivateKey(bytes.fromhex(PRIVATE_KEY_HEX))

# Derive the wallet address from the private key
wallet_address = private_key.public_key.to_base58check_address()

# USDT (TRC20) Contract Address on Tron Mainnet
USDT_CONTRACT_ADDRESS = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"

# Minimal TRC20 ABI
USDT_ABI = [
    {
        "constant": True,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "name": "balance",
                "type": "uint256"
            }
        ],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [
            {
                "name": "",
                "type": "uint8"
            }
        ],
        "type": "function"
    }
]

def get_usdt_balance(address: str) -> float:
    """
    Retrieves the USDT balance for the specified Tron wallet address using the provided ABI.

    :param address: Tron wallet address in Base58Check format.
    :return: USDT balance as a float.
    """
    try:
        # Load the contract with ABI
        usdt_contract = client.get_contract(USDT_CONTRACT_ADDRESS)
        print(f"USDT Contract Loaded: {usdt_contract.address}")

        # Call the balanceOf function
        usdt_balance_sun = usdt_contract.functions.balanceOf(address)()
        print(f"Raw USDT Balance (SUN): {usdt_balance_sun}")

        # Convert SUN to USDT (6 decimals)
        usdt_balance = usdt_balance_sun / 1_000_000
        print(f"Converted USDT Balance: {usdt_balance} USDT")
        return usdt_balance
    except AddressNotFound:
        print(f"Address {address} not found on the Tron network.")
        return 0.0
    # except ContractNotFound:
    #     print(f"USDT Contract at {USDT_CONTRACT_ADDRESS} not found.")
    #     return 0.0
    except Exception as e:
        print(f"An error occurred while fetching USDT balance: {e}")
        return 0.0

def get_usdt_balance_tronpy(address: str) -> float:
    """
    Retrieves the USDT TRC20 balance using TronPy's built-in methods.

    :param address: Tron wallet address in Base58Check format.
    :return: USDT balance as a float.
    """
    try:
        usdt = client.get_contract(USDT_CONTRACT_ADDRESS)  # USDT TRC20
        balance = usdt.functions.balanceOf(address)()
        usdt_balance = balance / 1_000_000
        print(f"USDT Balance using TronPy's built-in method: {usdt_balance} USDT")
        return usdt_balance
    except Exception as e:
        print(f"An error occurred while fetching USDT balance using TronPy's built-in method: {e}")
        return 0.0

def main():
    print(f"Wallet Address: {wallet_address}\n")
    
    # Fetch balance using contract interaction
    balance_contract = get_usdt_balance(wallet_address)
    print(f"USDT Balance for {wallet_address}: {balance_contract} USDT\n")
    
    # Fetch balance using TronPy's built-in method
    balance_tronpy = get_usdt_balance_tronpy(wallet_address)
    print(f"USDT Balance for {wallet_address} (TronPy Built-in): {balance_tronpy} USDT")

if __name__ == "__main__":
    main()
