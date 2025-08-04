import json, time, os
import requests
from web3 import Web3
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

load_dotenv()

RPC_URL = os.getenv("RPC_URL")
FAUCET_URL = os.getenv("FAUCET_URL")
COLLECTOR_ADDRESS = os.getenv("COLLECTOR_ADDRESS")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Load wallets
with open("wallets.json") as f:
    PRIVATE_KEYS = json.load(f)

def claim_faucet_selenium(wallet_address):
    try:
        options = uc.ChromeOptions()
        options.headless = True
        driver = uc.Chrome(options=options)
        driver.get("https://faucet.somnia.network/")

        time.sleep(5)  # tunggu loading

        # Masukkan address ke input
        addr_input = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
        addr_input.clear()
        addr_input.send_keys(wallet_address)

        # Klik tombol claim
        claim_btn = driver.find_element(By.CSS_SELECTOR, "button")
        claim_btn.click()

        time.sleep(10)  # tunggu proses klaim selesai
        driver.quit()
        print(f"✅ Faucet klaim untuk {wallet_address}")
    except Exception as e:
        print(f"❌ Gagal klaim faucet untuk {wallet_address}: {e}")

def wait_for_balance(wallet_address, min_balance_eth=0.45, max_wait_sec=300):
    waited = 0
    while waited < max_wait_sec:
        balance = w3.eth.get_balance(wallet_address)
        eth_balance = w3.fromWei(balance, 'ether')
        if eth_balance >= min_balance_eth:
            return eth_balance
        time.sleep(15)
        waited += 15
    return w3.fromWei(w3.eth.get_balance(wallet_address), 'ether')

def send_to_collector(private_key, index):
    acct = w3.eth.account.from_key(private_key)
    address = acct.address
    print(f"[{index}] Memproses {address}")

    claim_faucet_selenium(address)
    balance = wait_for_balance(address)

    if balance < 0.45:
        print(f"⚠️  Saldo {balance} kurang dari 0.45 STT")
        return

    amount = w3.toWei(0.4, 'ether')
    gas_price = w3.eth.gas_price
    nonce = w3.eth.get_transaction_count(address)

    tx = {
        'to': COLLECTOR_ADDRESS,
        'value': amount,
        'gas': 21000,
        'gasPrice': gas_price,
        'nonce': nonce,
        'chainId': w3.eth.chain_id
    }

    signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"📤 TX sent: https://explorer.somnia.network/tx/{tx_hash.hex()}")

def main():
    for i, pk in enumerate(PRIVATE_KEYS):
        try:
            send_to_collector(pk, i + 1)
            time.sleep(5)  # delay antar wallet
        except Exception as e:
            print(f"❌ Error pada wallet [{i + 1}]: {e}")

if __name__ == "__main__":
    main()
