import json
import time
import os
import requests
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.getenv("RPC_URL")
FAUCET_URL = os.getenv("FAUCET_URL")
COLLECTOR_ADDRESS = os.getenv("COLLECTOR_ADDRESS")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Load daftar private key
with open("wallets.json") as f:
    PRIVATE_KEYS = json.load(f)

def claim_faucet(wallet_address, index):
    try:
        payload = {"address": wallet_address}
        res = requests.post(FAUCET_URL, json=payload)
        if res.status_code == 200 and res.json().get("success"):
            print(f"✅ [{index}] Faucet berhasil diklaim: {wallet_address}")
        else:
            print(f"❌ [{index}] Gagal klaim faucet: {res.text}")
    except Exception as e:
        print(f"❌ [{index}] Error klaim faucet: {e}")

def wait_balance(wallet_address, min_stt=0.45, max_wait=300):
    waited = 0
    while waited < max_wait:
        balance = w3.eth.get_balance(wallet_address)
        eth = w3.fromWei(balance, 'ether')
        if eth >= min_stt:
            return eth
        time.sleep(10)
        waited += 10
    return w3.fromWei(w3.eth.get_balance(wallet_address), 'ether')

def send_0_4_stt(private_key, index):
    acct = w3.eth.account.from_key(private_key)
    from_addr = acct.address
    print(f"\n🔁 [{index}] Proses: {from_addr}")

    claim_faucet(from_addr, index)
    balance = wait_balance(from_addr)

    if balance < 0.45:
        print(f"⚠️  [{index}] Saldo belum cukup (saat ini: {balance} STT)")
        return

    amount = w3.toWei(0.4, 'ether')
    gas_price = w3.eth.gas_price
    nonce = w3.eth.get_transaction_count(from_addr)

    tx = {
        'to': COLLECTOR_ADDRESS,
        'value': amount,
        'gas': 21000,
        'gasPrice': gas_price,
        'nonce': nonce,
        'chainId': w3.eth.chain_id
    }

    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"📤 [{index}] Kirim 0.4 STT → {COLLECTOR_ADDRESS}")
    print(f"🔗 TX: https://shannon-explorer.somnia.network/tx/{tx_hash.hex()}")

def main():
    for i, pk in enumerate(PRIVATE_KEYS):
        try:
            send_0_4_stt(pk, i + 1)
            time.sleep(2)  # delay antar wallet
        except Exception as e:
            print(f"❌ [{i + 1}] Error: {e}")

if __name__ == "__main__":
    main()
