from web3 import Web3
from eth_account import Account
import requests
import time
import json

# ====== Konfigurasi utama ======
RPC_URL = "https://dream-rpc.somnia.network"
FAUCET_URL = "https://testnet.somnia.network/api/faucet"
WALLET_COUNT = 1000
WALLET_OUTPUT_FILE = "wallets.json"
DESTINATION_WALLET = "0x4fa3e39a6be40df0a02b92207957eb964462a696"
SEND_AMOUNT_STT = 0.4
GAS_LIMIT = 31500
GAS_PRICE = Web3.to_wei("7.2", "gwei")

web3 = Web3(Web3.HTTPProvider(RPC_URL))


# ====== Step 1: Generate wallet ======
def generate_wallets(n):
    wallets = []
    for _ in range(n):
        acct = Account.create()
        wallets.append({
            "address": acct.address,
            "private_key": acct.key.hex()
        })
    with open(WALLET_OUTPUT_FILE, "w") as f:
        json.dump(wallets, f, indent=2)
    print(f"{n} wallet disimpan ke {WALLET_OUTPUT_FILE}")


# ====== Step 2: Claim faucet dari API ======
def claim_faucet(address):
    try:
        res = requests.post(FAUCET_URL, json={"address": address})
        print(f"[Faucet] {address[:10]}...: {res.json()}")
        return res.ok
    except Exception as e:
        print(f"[Faucet Error] {address}: {e}")
        return False


# ====== Step 3: Kirim 0.4 STT ke wallet utama ======
def send_token(from_privkey, to_address, amount_stt):
    acct = Account.from_key(from_privkey)
    from_address = acct.address
    nonce = web3.eth.get_transaction_count(from_address)

    tx = {
        "to": to_address,
        "value": web3.to_wei(amount_stt, "ether"),
        "gas": GAS_LIMIT,
        "gasPrice": GAS_PRICE,
        "nonce": nonce,
        "chainId": web3.eth.chain_id,
    }

    signed_tx = web3.eth.account.sign_transaction(tx, from_privkey)
    try:
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"[Send] {from_address[:10]}... → {to_address[:10]}... | TX: {web3.to_hex(tx_hash)}")
        return web3.to_hex(tx_hash)
    except Exception as e:
        print(f"[Send Error] {from_address}: {e}")
        return None


# ====== Step 4: Jalankan semua langkah ======
def run():
    with open(WALLET_OUTPUT_FILE) as f:
        wallets = json.load(f)

    for i, wallet in enumerate(wallets):
        print(f"\n===[ {i+1}/{len(wallets)} ]=== {wallet['address']}")
        success = claim_faucet(wallet["address"])
        if not success:
            continue

        # Tunggu STT masuk (bisa disesuaikan)
        print("Tunggu 10 detik untuk distribusi token...")
        time.sleep(10)

        send_token(wallet["private_key"], DESTINATION_WALLET, SEND_AMOUNT_STT)


if __name__ == "__main__":
    # Step pertama hanya perlu dijalankan sekali
    # generate_wallets(WALLET_COUNT)

    # Setelah wallet dibuat, jalankan loop auto-claim + auto-send
    run()
