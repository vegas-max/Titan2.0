---
# Fill in the fields below to create a basic custom agent for your repository.
# The Copilot CLI can be used for local testing: https://gh.io/customagents/cli
# To make this agent available, merge this file into the default repository branch.
# For format details, see: https://gh.io/customagents/config

# Apex OmegaPolygon Arbitrage Copilot ("Git Hhub Agent")

This repository scaffolds an arbitrage agent/codex for Polygon networks — the "Apex Omegapolygon Arbitrage Copilot" (aka "Git Hhub Agent"). It is intentionally minimal and safe by default: dry-run and testnet modes are supported.

Features (initial):
- Node + TypeScript starter
- Ethers.js-based chain connectivity
- Agent skeleton with opportunity discovery and execution hooks
- CI workflow for building and testing
- Environment config template

Important: This project may control funds. Start on testnet and use dry-run mode. Read docs before providing private keys.

Requirements:
- Node 18+
- yarn or npm
- Alchemy/Infura/RPC provider for Polygon (testnet or mainnet)

Quick start:
1. Copy `.env.example` to `.env` and fill values.
2. Install dependencies:
   - yarn install
3. Build and run in simulation mode:
   - yarn start:dry

Environment variables (from .env.example):
- RPC_URL - RPC endpoint (Polygon)
- PRIVATE_KEY - deployer/keeper private key (use GitHub secrets for CI)
- MODE - dry | live
- WATCH_TOKENS - comma-separated token addresses to monitor
