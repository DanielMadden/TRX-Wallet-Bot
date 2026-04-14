# TRX-Wallet-Bot

A Python bot that monitors a TRON (TRX) wallet and auto-sweeps USDT to a target address when balance conditions are met.

## How It Works

1. Derives wallet address from private key at runtime
2. Polls the wallet balance via the TRON API
3. When TRX balance exceeds the threshold (covers fees), transfers available USDT to the target wallet
4. Logs activity and loops

## Setup

```bash
pip install tronpy
```

Create `my_secrets.py` (gitignored):
```python
PRIVATE_KEY_HEX = "your_private_key_hex"
API_KEYS = "your_tron_api_key"
```

```bash
python trx_monitor.py
```

## Files

- `trx_monitor.py` — main monitoring loop
- `client_manager.py` — TRON client setup
- `test_transfer.py` / `my_test_transfer.py` — transfer test scripts

## Security

Never commit `my_secrets.py`. The private key gives full control of the wallet.
