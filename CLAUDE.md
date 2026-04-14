# TRX-Wallet-Bot — CLAUDE.md

## What This Is
A Python bot that monitors a TRON (TRX) blockchain wallet and automatically transfers USDT to a target wallet when the TRX balance meets a threshold. Designed to sweep funds automatically.

## Stack
- Python 3
- `tronpy` — TRON blockchain client library
- Private key management via `my_secrets.py` (gitignored)

## Files
```
trx_monitor.py        # Main monitoring loop — watches balance, triggers transfer
test_transfer.py      # Test script for transfer logic
my_test_transfer.py   # Personal test variant
client_manager.py     # Tron client initialization/management
```

## Key Concepts
- Wallet address is derived from the private key at runtime (not hardcoded)
- Balances are in SUN (1 TRX = 1,000,000 SUN) — always divide by 1,000,000
- Target wallet: `TGfJJ3o5e4eK9P8jZnFJSzJHUHGQeC2mpR`
- Requires minimum TRX balance (default: 15 TRX) to cover transaction fees before sweeping USDT

## Secrets
`my_secrets.py` is gitignored and must contain:
```python
PRIVATE_KEY_HEX = "..."   # Wallet private key
API_KEYS = "..."           # TRON API key(s) for HTTPProvider
```

## Running
```bash
pip install tronpy
python trx_monitor.py
```

## Warning
This bot manages real cryptocurrency. Never commit `my_secrets.py` or any file containing private keys.
