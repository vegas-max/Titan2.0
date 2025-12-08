import logging
from core.config import CHAINS

# Setup Logging
logger = logging.getLogger("TitanCommander")

class TitanCommander:
    def __init__(self, chain_id):
        self.chain_id = chain_id
        self.chain_config = CHAINS.get(chain_id)

    def optimize_loan_size(self, token_address, target_amount_raw, decimals=18):
        """
        Returns the requested loan amount without any restrictions.
        """
        requested_amount = int(target_amount_raw)
        logger.info(f"✅ Loan Amount Approved: {requested_amount}")
        return requested_amount