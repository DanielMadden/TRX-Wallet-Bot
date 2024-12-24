# test_pull_usdt.py

import time
from tronpy import Tron
from tronpy.keys import PrivateKey
from tronpy.providers import HTTPProvider
from tronpy.exceptions import AddressNotFound
from my_secrets import PRIVATE_KEY_HEX, API_KEYS

# --- Configuration ---

# Initialize Tron client using API_KEYS from my_secrets
client = Tron(provider=HTTPProvider(api_key=API_KEYS))

# Construct the PrivateKey object from your hex string
private_key = PrivateKey(bytes.fromhex(PRIVATE_KEY_HEX))

# Derive the wallet address from the private key
wallet_address = private_key.public_key.to_base58check_address()

# USDT (TRC20) Contract Address on Tron
USDT_CONTRACT_ADDRESS = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"

def get_usdt_balance(address: str) -> float:
    """
    Retrieves the USDT balance for the specified Tron wallet address.

    :param address: Tron wallet address in Base58Check format.
    :return: USDT balance as a float.
    """
    try:
        usdt_contract = client.get_contract(USDT_CONTRACT_ADDRESS)
        
        # Access the 'balanceOf' function
        balance_function = usdt_contract.functions.balanceOf(address)
        
        # Ensure that 'balance_function' is callable
        if not callable(balance_function):
            raise AttributeError("'balanceOf' is not callable.")
        
        # Call the function to get the balance in SUN (USDT uses 6 decimals)
        usdt_balance_sun = balance_function.call()
        
        # Convert SUN to USDT
        usdt_balance = usdt_balance_sun / 1_000_000
        return usdt_balance
    except AddressNotFound:
        print(f"Address {address} not found on the Tron network.")
        return 0.0
    except Exception as e:
        print(f"An error occurred while fetching USDT balance: {e}")
        return 0.0

def main():
    balance = get_usdt_balance(wallet_address)
    print(f"USDT Balance for {wallet_address}: {balance} USDT")

if __name__ == "__main__":
    main()
