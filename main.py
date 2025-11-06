import google.generativeai as genai
import os

# --- KONFIGURASI ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# -------------------------

# Cek Environment Variable
if not GEMINI_API_KEY:
    raise ValueError("Error: GEMINI_API_KEY tidak ditemukan.")

# Inisialisasi Gemini
genai.configure(api_key=GEMINI_API_KEY)

print("--- MULAI PENCARIAN MODEL YANG TERSEDIA ---")

# Tugasnya cuma mencetak daftar model
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
    print("--- PENCARIAN SELESAI ---")
except Exception as e:
    print(f"Error saat mencari model: {e}")
