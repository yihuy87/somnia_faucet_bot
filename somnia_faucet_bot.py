import os
import json
import time
import random
import requests
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

FAUCET_URL = "https://testnet.somnia.network/api/faucet"
RPC_URL = "https://dream-rpc.somnia.network"
web3 = Web3(Web3.HTTPProvider(RPC_URL))

MASTER_PRIVATE_KEY = os.getenv("MASTER_PRIVATE_KEY")
MASTER_WALLET = web3.eth.account.from_key(MASTER_PRIVATE_KEY).address

GAS_LIMIT = 31500
MAX_FEE_PER_GAS = web3.to_wei(7.2, 'gwei')
PRIORITY_FEE = 0
AMOUNT_TO_SEND = 0.4  # STT
TOKEN_DECIMALS = 18

def generate_wallets(n=1000):
    wallets = []
    for _ in range(n):
        acct = web3.eth.account.create()
        wallets.append({
            "address": acct.address,
            "private_key": acct.key.hex()
        })
    with open("wallets.json", "w") as f:
        json.dump(wallets, f, indent=2)
    print(f"{n} wallets generated.")

def claim_faucet(wallet_address):
    try:
        res = requests.post(FAUCET_URL, json={"address": wallet_address}, timeout=10)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

def send_to_master(private_key):
    account = web3.eth.account.from_key(private_key)
    nonce = web3.eth.get_transaction_count(account.address)
    tx = {
        "to": MASTER_WALLET,
        "value": int(AMOUNT_TO_SEND * 10**TOKEN_DECIMALS),
        "gas": GAS_LIMIT,
        "maxFeePerGas": MAX_FEE_PER_GAS,
        "maxPriorityFeePerGas": PRIORITY_FEE,
        "nonce": nonce,
        "chainId": web3.eth.chain_id,
        "type": 2,
    }
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return web3.to_hex(tx_hash)

def run():
    with open("wallets.json") as f:
        wallets = json.load(f)

    for i, wallet in enumerate(wallets):
        address = wallet["address"]
        pk = wallet["private_key"]

        print(f"[{i+1}] Claiming faucet for {address}...")
        result = claim_faucet(address)
        print("Faucet result:", result)

        if "error" in result:
            continue

        print(f"Waiting 5s before sending from {address} to master...")
        time.sleep(5)

        try:
            tx_hash = send_to_master(pk)
            print(f"Sent 0.4 STT to master: {tx_hash}")
        except Exception as e:
            print("Send failed:", str(e))

        delay = random.randint(15, 25)
        print(f"Waiting {delay}s before next wallet...")
        time.sleep(delay)

if __name__ == "__main__":
    if not os.path.exists("wallets.json"):
        generate_wallets(1000)
    run()
