import os

print("🕵️‍♂️ MULAI Misi SPY: Mengintip Brankas Rahasia GitHub...")
print("-" * 60)

# Daftar semua kunci yang kita harapkan ada
expected_keys = [
    "TELEGRAM_BOT_TOKEN",
    "CHAT_ID",
    "GEMINI_API_KEY",
    "SUPABASE_URL",
    "SUPABASE_KEY"
]

all_found = True

for key in expected_keys:
    # Ambil nilai dari environment
    value = os.environ.get(key)
    
    # Cek apakah ada dan tidak kosong
    if value is None or value.strip() == "":
        print(f"❌ SPY REPORT: Kunci '{key}' HILANG atau KOSONG!")
        print(f"   -> Nilai yang ditemukan: '{value}'")
        all_found = False
    else:
        print(f"✅ SPY REPORT: Kunci '{key}' DITEMUKAN.")
        print(f"   -> Nilai (10 karakter pertama): '{value[:10]}...'")

print("-" * 60)

if all_found:
    print("🎉 SPY REPORT: SEMUA KUNCI AMAN! Script utama seharusnya bisa berjalan.")
else:
    print("🚨 SPY REPORT: MASALAH DITEMUKAN! Ada kunci yang hilang. Tidak bisa lanjut.")
