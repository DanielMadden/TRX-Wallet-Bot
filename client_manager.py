# client_manager.py
from tronpy import Tron
from tronpy.providers import HTTPProvider
from tronpy.exceptions import TronError
import itertools

class TronClientManager:
    def __init__(self, api_keys):
        if not api_keys:
            raise ValueError("API_KEYS list cannot be empty.")
        
        self.api_keys = api_keys
        self.key_cycle = itertools.cycle(self.api_keys)
        self.current_key = next(self.key_cycle)
        self.client = self._initialize_client(self.current_key)
    
    def _initialize_client(self, api_key):
        return Tron(provider=HTTPProvider(api_key=api_key))
    
    def get_client(self):
        return self.client
    
    def switch_to_next_key(self):
        self.current_key = next(self.key_cycle)
        print(f"Switching to next API key: {self.current_key}")
        self.client = self._initialize_client(self.current_key)
