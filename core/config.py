import os
from dotenv import load_dotenv
load_dotenv()

# V3 Vault is deterministic (Same addr on all chains)
BALANCER_V3_VAULT = "0xbA1333333333a1BA1108E8412f11850A5C319bA9"

CHAINS = {
    137: {
        "name": "polygon",
        "rpc": os.getenv("RPC_POLYGON"),
        "aave_pool": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
        "uniswap_router": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
        "native": "MATIC"
    },
    42161: {
        "name": "arbitrum",
        "rpc": os.getenv("RPC_ARBITRUM"),
        "aave_pool": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
        "uniswap_router": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
        "native": "ETH"
    }
    # Add remaining 8 chains here following the pattern
}