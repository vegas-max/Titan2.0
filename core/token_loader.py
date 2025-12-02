import requests
import json

class TokenLoader:
    # 1inch Token Registry (Aggregates standard tokens across chains)
    URL = "https://tokens.1inch.io/v1.1"

    @staticmethod
    def get_tokens(chain_id):
        """
        Dynamically fetches top 100+ tokens for a chain. No hardcoding.
        """
        print(f"📥 Fetching tokens for Chain {chain_id}...")
        try:
            res = requests.get(f"{TokenLoader.URL}/{chain_id}")
            data = res.json()
            
            # Convert dict to clean list [ {symbol, address, decimals} ]
            tokens = []
            for addr, details in data.items():
                tokens.append({
                    "symbol": details['symbol'],
                    "address": addr,
                    "decimals": details['decimals']
                })
            
            print(f"   ✅ Loaded {len(tokens)} tokens.")
            return tokens
        except Exception as e:
            print(f"   ❌ Failed to load tokens: {e}")
            return []