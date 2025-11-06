import os

print("--- MULAI PENCARIAN KUNCI RAHASIA YANG HILANG ---")

# Daftar semua kunci yang harus ada
required_keys = [
    "TELEGRAM_BOT_TOKEN",
    "CHAT_ID",
    "GEMINI_API_KEY",
    "SUPABASE_URL",
    "SUPABASE_KEY"
]

missing_keys = []

for key in required_keys:
    value = os.environ.get(key)
    if value is None or value == "":
        print(f"❌ KUNCI HILANG: `{key}`")
        missing_keys.append(key)
    else:
        print(f"✅ KUNCI DITEMUKAN: `{key}`")

print("--- PENCARIAN SELESAI ---")

if missing_keys:
    print("\nMASALAH DITEMUKAN! Kunci berikut ini tidak ada atau kosong:")
    for key in missing_keys:
        print(f"- {key}")
    print("\nSilakan periksa kembali Settings > Secrets di GitHub.")
else:
    print("\nSEMUA KUNCI RAHASIA DITEMUKAN. Script utama seharusnya bisa berjalan.")
