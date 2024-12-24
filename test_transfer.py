import time
import sys
from tronpy import Tron
from tronpy.providers import HTTPProvider
from tronpy.keys import PrivateKey
from my_secrets import PRIVATE_KEY_HEX, API_KEYS

def test_usdt_transfer():
    """
    Attempts a single USDT transfer from the private key's wallet
    to the target wallet address, ignoring TRX balance checks.
    """
    # 1. Initialize Tron client with multiple API keys (if you have them)
    try:
        client = Tron(provider=HTTPProvider(api_key=API_KEYS))
    except Exception as e:
        print(f"Error initializing Tron client: {e}")
        sys.exit(1)

    # 2. Construct the PrivateKey object from your hex string
    try:
        private_key = PrivateKey(bytes.fromhex(PRIVATE_KEY_HEX))
    except ValueError as e:
        print(f"Invalid PRIVATE_KEY_HEX: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error while creating PrivateKey: {e}")
        sys.exit(1)

    # 3. Get the wallet address in hexadecimal format
    try:
        wallet_address_hex = private_key.public_key.to_hex_address()
        print(f"Wallet Address (Hex): {wallet_address_hex}")
    except Exception as e:
        print(f"Error deriving wallet address: {e}")
        sys.exit(1)

    # 4. The target wallet for the USDT
    target_wallet = "TGfJJ3o5e4eK9P8jZnFJSzJHUHGQeC2mpR"
    try:
        target_wallet_hex = client.address.to_hex(target_wallet)
        print(f"Target Wallet Address (Hex): {target_wallet_hex}")
    except Exception as e:
        print(f"Error converting target wallet address to hex: {e}")
        sys.exit(1)

    print(f"\nAttempting USDT transfer from {wallet_address_hex} to {target_wallet_hex}...\n")

    try:
        # 5. Get the USDT contract on Tron
        usdt_contract = client.get_contract("TLa2f6VPqDgRE67v1736s7bJ8Ray5wYjU7")
        print("USDT Contract loaded successfully.")

        # 6. Fetch USDT balance of this wallet using .call()
        try:
            usdt_balance_sun = usdt_contract.functions.balanceOf(wallet_address_hex).call()
            usdt_balance = usdt_balance_sun / 1_000_000  # Convert to human-readable USDT
            print(f"Current USDT balance: {usdt_balance} USDT (Balance in SUN: {usdt_balance_sun})\n")
        except Exception as e:
            print(f"Error fetching USDT balance: {e}")
            sys.exit(1)

        if usdt_balance > 0:
            print("Building USDT transfer transaction...")
            try:
                txn = (
                    usdt_contract.functions.transfer(target_wallet_hex, usdt_balance_sun)
                    .with_owner(wallet_address_hex)
                    # fee_limit is in SUN. 100,000,000 SUN = 100 TRX max fee.
                    .fee_limit(100_000_000)
                    .build()
                    .sign(private_key)
                )
                print("Transaction built and signed successfully.")
            except Exception as e:
                print(f"Error building/signing transaction: {e}")
                sys.exit(1)

            # Optional: Display transaction details before broadcasting
            print(f"Transaction Details:\n{txn}\n")

            # 7. Broadcast the transaction
            try:
                print("Broadcasting the transaction...")
                tx_response = txn.broadcast()

                # Wait for the transaction to be confirmed
                tx_receipt = tx_response.wait()

                print(f"Transaction broadcasted successfully!")
                print(f"Transaction Hash: {tx_receipt['txid']}")
                print(f"Status: {tx_receipt['receipt']['result']}")
                print(f"Energy Used: {tx_receipt['receipt']['energy_usage']}\n")
            except Exception as e:
                print(f"Error broadcasting transaction: {e}")
                sys.exit(1)

        else:
            print("No USDT to transfer. Transfer aborted.\n")

    except Exception as e:
        print(f"An error occurred during the USDT transfer process: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    test_usdt_transfer()
