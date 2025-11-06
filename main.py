import os

print("🩺 TERAPI GITHUB: Memeriksa ingatan brankas rahasia...")
print("-" * 60)

# Cetak semua environment variable yang ada
all_env_vars = dict(os.environ)

# Filter untuk hanya menampilkan yang kita pedulikan
keys_to_check = ["TELEGRAM_BOT_TOKEN", "CHAT_ID", "GEMINI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]

found_keys = {}
missing_keys = []

for key in keys_to_check:
    value = all_env_vars.get(key)
    if value:
        found_keys[key] = value
        print(f"✅ DITEMUKAN: {key}")
        print(f"   -> Nilai (20 karakter pertama): '{value[:20]}...'")
    else:
        missing_keys.append(key)
        print(f"❌ HILANG: {key}")

print("-" * 60)

if not missing_keys:
    print("🎉 DIAGNOSIS: Semua kunci ditemukan di ingatan GitHub!")
else:
    print("🚨 DIAGNOSIS: Masih ada kunci yang hilang dari ingatan GitHub!")
    print(f"Kunci yang hilang: {', '.join(missing_keys)}")
