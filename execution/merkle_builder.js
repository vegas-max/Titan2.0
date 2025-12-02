const { MerkleTree } = require('merkletreejs');
const keccak256 = require('keccak256');
const { ethers } = require('ethers');

class MerkleBlockBuilder {
    constructor() {
        this.tree = null;
        this.leaves = [];
    }

    /**
     * Encodes a trade instruction into a leaf hash.
     * @param {string} token - Token Address
     * @param {string} amount - Amount
     * @param {string} router - Router Address
     * @param {string} calldata - Swap Calldata
     */
    createLeaf(token, amount, router, calldata) {
        // Equivalent to Solidity: keccak256(abi.encodePacked(token, amount, router, calldata))
        const leaf = ethers.solidityPackedKeccak256(
            ['address', 'uint256', 'address', 'bytes'],
            [token, amount, router, calldata]
        );
        return leaf;
    }

    /**
     * Builds the Merkle Tree from a list of trade objects.
     * @param {Array} trades - List of trade objects {token, amount, router, data}
     */
    buildBatch(trades) {
        console.log(`🌳 Merkle: Compressing ${trades.length} trades into block...`);
        
        // 1. Generate Leaves
        this.leaves = trades.map(t => this.createLeaf(t.token, t.amount, t.router, t.data));
        
        // 2. Build Tree
        this.tree = new MerkleTree(this.leaves, keccak256, { sortPairs: true });
        
        const root = this.tree.getHexRoot();
        console.log(`✅ Merkle Root Generated: ${root}`);
        
        return root;
    }

    /**
     * Generates the Proof for a specific trade index.
     * Required for the smart contract to verify the trade is part of the batch.
     */
    getProof(tradeIndex) {
        if (!this.leaves[tradeIndex]) return [];
        const leaf = this.leaves[tradeIndex];
        return this.tree.getHexProof(leaf);
    }
    
    /**
     * Verifies a leaf locally (Sanity Check)
     */
    verify(root, leaf, proof) {
        return this.tree.verify(proof, leaf, root);
    }
}

module.exports = { MerkleBlockBuilder };