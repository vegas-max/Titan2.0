import requests
import os

class BridgeAggregator:
    # Li.Fi API - The Google Flights of Bridges
    URL = "https://li.quest/v1/quote"

    def __init__(self):
        self.api_key = os.getenv("LIFI_API_KEY")

    def get_best_route(self, src_chain, dst_chain, token, amount, user):
        """
        Finds the absolute best bridge (Stargate, Across, Hop, etc.)
        """
        params = {
            "fromChain": src_chain,
            "toChain": dst_chain,
            "fromToken": token,
            "toToken": token,
            "fromAmount": amount,
            "fromAddress": user,
            "order": "RECOMMENDED"
        }
        headers = {"x-lifi-api-key": self.api_key}
        
        try:
            res = requests.get(self.URL, params=params, headers=headers)
            if res.status_code == 200:
                data = res.json()
                return {
                    "bridge": data['tool'],
                    "est_output": data['estimate']['toAmount'],
                    "fee_usd": data['estimate']['feeCosts'][0]['amountUSD'],
                    "tx_data": data['transactionRequest'] # Raw TX to sign
                }
        except Exception as e:
            print(f"Bridge Error: {e}")
        return None