from web3 import Web3, Account
import json

Account.enable_unaudited_hdwallet_features()

TOTAL_WALLETS = 1000
wallets = []
wallets_full = []

for i in range(TOTAL_WALLETS):
    acct = Account.create()
    wallets.append(acct.key.hex())  # hanya private key
    wallets_full.append({
        "address": acct.address,
        "private_key": acct.key.hex()
    })

# Simpan hanya private keys
with open("wallets.json", "w") as f:
    json.dump(wallets, f, indent=2)

# Simpan versi lengkap (optional)
with open("wallets_full.json", "w") as f:
    json.dump(wallets_full, f, indent=2)

print(f"✅ Berhasil generate {TOTAL_WALLETS} wallet")
