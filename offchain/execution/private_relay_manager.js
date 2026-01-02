require('dotenv').config();
const { ethers } = require('ethers');
const { FlashbotsBundleProvider } = require('@flashbots/ethers-provider-bundle');
const { BloxRouteManager } = require('./bloxroute_manager');

/**
 * Private Relay Manager
 * Unified interface for private transaction submission across multiple chains
 * Supports: Flashbots (Ethereum), MEV Blocker (BSC), BloxRoute (Multi-chain)
 */
class PrivateRelayManager {
    constructor() {
        this.flashbotsProvider = null;
        this.bloxroute = new BloxRouteManager();
        this.chainRelayConfig = this.getChainRelayConfig();
        this.initialized = {};
    }

    /**
     * Configuration for private relays per chain
     */
    getChainRelayConfig() {
        return {
            // Ethereum Mainnet - Flashbots
            1: {
                name: 'Ethereum',
                relayType: 'flashbots',
                endpoint: 'https://relay.flashbots.net',
                enabled: true
            },
            // Goerli Testnet - Flashbots
            5: {
                name: 'Goerli',
                relayType: 'flashbots',
                endpoint: 'https://relay-goerli.flashbots.net',
                enabled: true
            },
            // BSC - MEV Blocker
            56: {
                name: 'BSC',
                relayType: 'mev-blocker',
                endpoint: 'https://rpc.mevblocker.io',
                enabled: true
            },
            // Polygon - BloxRoute
            137: {
                name: 'Polygon',
                relayType: 'bloxroute',
                endpoint: 'https://polygon.blxrbdn.com',
                enabled: true
            },
            // Arbitrum - BloxRoute
            42161: {
                name: 'Arbitrum',
                relayType: 'bloxroute',
                endpoint: 'https://arbitrum.blxrbdn.com',
                enabled: true
            },
            // Optimism - Standard RPC (no private relay yet)
            10: {
                name: 'Optimism',
                relayType: 'standard',
                endpoint: null,
                enabled: false
            },
            // Base - Standard RPC
            8453: {
                name: 'Base',
                relayType: 'standard',
                endpoint: null,
                enabled: false
            }
        };
    }

    /**
     * Initialize Flashbots provider for Ethereum
     */
    async initFlashbots(chainId, provider) {
        if (this.initialized[`flashbots-${chainId}`]) {
            return this.flashbotsProvider;
        }

        try {
            const config = this.chainRelayConfig[chainId];
            if (!config || config.relayType !== 'flashbots') {
                throw new Error(`Flashbots not configured for chain ${chainId}`);
            }

            // Create reputation/auth signer (can be any wallet, doesn't need funds)
            const authSigner = process.env.FLASHBOTS_AUTH_KEY
                ? new ethers.Wallet(process.env.FLASHBOTS_AUTH_KEY)
                : ethers.Wallet.createRandom();

            // Initialize Flashbots provider
            this.flashbotsProvider = await FlashbotsBundleProvider.create(
                provider,
                authSigner,
                config.endpoint
            );

            this.initialized[`flashbots-${chainId}`] = true;
            console.log(`✅ Flashbots Provider initialized for ${config.name}`);
            
            return this.flashbotsProvider;
        } catch (error) {
            console.error(`❌ Failed to initialize Flashbots for chain ${chainId}:`, error.message);
            return null;
        }
    }

    /**
     * Submit transaction via Flashbots bundle
     */
    async submitFlashbotsBundle(signedTx, targetBlock, chainId, provider) {
        try {
            if (!this.flashbotsProvider) {
                await this.initFlashbots(chainId, provider);
            }

            if (!this.flashbotsProvider) {
                throw new Error('Flashbots provider not initialized');
            }

            const bundleSubmission = await this.flashbotsProvider.sendBundle(
                [{ signedTransaction: signedTx }],
                targetBlock
            );

            console.log('🚀 Flashbots bundle submitted');

            // Wait for bundle to be included
            if ('wait' in bundleSubmission) {
                const waitResponse = await bundleSubmission.wait();
                
                if (waitResponse === 0) {
                    console.log('✅ Bundle included in block');
                    return { success: true, included: true };
                } else if (waitResponse === 1) {
                    console.log('⚠️ Bundle valid but not included');
                    return { success: true, included: false };
                } else {
                    console.log('❌ Bundle rejected');
                    return { success: false, reason: 'Bundle rejected' };
                }
            }

            return { success: true, pending: true };
        } catch (error) {
            console.error('❌ Flashbots submission failed:', error.message);
            return { success: false, error: error.message };
        }
    }

    /**
     * Submit transaction via MEV Blocker (BSC)
     */
    async submitMEVBlocker(signedTx, chainId) {
        try {
            const config = this.chainRelayConfig[chainId];
            if (!config || config.relayType !== 'mev-blocker') {
                throw new Error(`MEV Blocker not configured for chain ${chainId}`);
            }

            // MEV Blocker uses standard eth_sendRawTransaction but via their RPC
            const provider = new ethers.JsonRpcProvider(config.endpoint);
            const response = await provider.broadcastTransaction(signedTx);
            
            console.log('🚀 MEV Blocker transaction submitted:', response.hash);
            
            return { success: true, hash: response.hash, response };
        } catch (error) {
            console.error('❌ MEV Blocker submission failed:', error.message);
            return { success: false, error: error.message };
        }
    }

    /**
     * Submit transaction via BloxRoute
     */
    async submitBloxRoute(signedTx, blockNumber, chainId) {
        try {
            const config = this.chainRelayConfig[chainId];
            if (!config || config.relayType !== 'bloxroute') {
                throw new Error(`BloxRoute not configured for chain ${chainId}`);
            }

            const result = await this.bloxroute.submitBundle([signedTx], blockNumber);
            
            console.log('🚀 BloxRoute bundle submitted:', result);
            
            return { success: true, result };
        } catch (error) {
            console.error('❌ BloxRoute submission failed:', error.message);
            return { success: false, error: error.message };
        }
    }

    /**
     * Main submission method - auto-selects best relay for chain
     */
    async submitPrivateTransaction(signedTx, chainId, provider, blockNumber) {
        const config = this.chainRelayConfig[chainId];
        
        if (!config || !config.enabled) {
            console.log(`⚠️ No private relay configured for chain ${chainId}, using standard RPC`);
            return { success: false, reason: 'No private relay available' };
        }

        console.log(`🔐 Submitting private transaction via ${config.relayType} on ${config.name}`);

        switch (config.relayType) {
            case 'flashbots':
                return await this.submitFlashbotsBundle(signedTx, blockNumber, chainId, provider);
            
            case 'mev-blocker':
                return await this.submitMEVBlocker(signedTx, chainId);
            
            case 'bloxroute':
                return await this.submitBloxRoute(signedTx, blockNumber, chainId);
            
            default:
                console.log(`⚠️ Unknown relay type: ${config.relayType}`);
                return { success: false, reason: 'Unknown relay type' };
        }
    }

    /**
     * Check if private relay is available for chain
     */
    isPrivateRelayAvailable(chainId) {
        const config = this.chainRelayConfig[chainId];
        return config && config.enabled;
    }

    /**
     * Get relay info for chain
     */
    getRelayInfo(chainId) {
        return this.chainRelayConfig[chainId] || null;
    }

    /**
     * Simulate bundle before submission (Flashbots only)
     */
    async simulateBundle(signedTx, targetBlock, chainId, provider) {
        try {
            if (!this.flashbotsProvider) {
                await this.initFlashbots(chainId, provider);
            }

            if (!this.flashbotsProvider) {
                throw new Error('Flashbots provider not initialized');
            }

            const simulation = await this.flashbotsProvider.simulate(
                [{ signedTransaction: signedTx }],
                targetBlock
            );

            if ('error' in simulation) {
                console.log('❌ Bundle simulation failed:', simulation.error);
                return { success: false, error: simulation.error };
            }

            console.log('✅ Bundle simulation successful');
            return { success: true, simulation };
        } catch (error) {
            console.error('❌ Bundle simulation error:', error.message);
            return { success: false, error: error.message };
        }
    }
}

module.exports = { PrivateRelayManager };
