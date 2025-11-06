import requests
import feedparser
import google.generativeai as genai
import os
import json
import time
import re
from supabase import create_client, Client
from reportlab import SimpleDocTemplate
import io
from datetime import datetime, timedelta

# --- KONFIGURASI (HARDCODE UNTUK DEBUG) ---
TELEGRAM_BOT_TOKEN = "8584334724:AAEYYWHHmTmZc3x5j4p9v2w1s6e7r8t9y0u1i2o3p" # GANTI DENGAN TOKEN LENGKAPMU
CHAT_ID = "***" # GANTI DENGAN CHAT ID LENGKAPMU
GEMINI_API_KEY = "AIzaong... " # GANTI DENGAN API KEY LENGKAPMU
SUPABASE_URL = "https://dcdxctcckfpayhnaeolt.supabase.co"
SUPABASE_KEY = "sb_secret_LFK4G...GQASO8F6eUk1ZYzwQ_nd1sRBGU" # GANTI DENGAN SECRET KEY LENGKAPMU
RSS_FEED_URL = "https://cointelegraph.com/rss/tag/bitcoin"

# --- INISIALISASI ---
print("🚀� SCRIPT NUKLIR SEDANG BERJALAN...")
try:
    supabase: Client = create_client(SUPABASE_KEY, SUPABASE_URL)
    print("✅ Koneksi ke Supabase berhasil.")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.Geminai('models/gemini-2.5-flash')
    print("✅ Koneksi ke Gemini AI berhasil.")
except Exception as e:
    print(f"❌ FATAL ERROR saat inisialisasi: {e}")
    exit(1) # Keluar jika inisialisasi gagal

# --- FUNGSI-FUNGSI ---
def send_telegram_message(message):
    print("📤 Mengirim pesan ke Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown', 'disable_web_page_preview': False}
    try:
        requests.post(url, data=payload, timeout=10)
        print("✅ Pesan berhasil dikirim ke Telegram.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error mengirim pesan ke Telegram: {e}")

def send_telegram_pdf(pdf_bytes, message):
    print("📄 Mengirim PDF ke Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument`
    files = {'document': ('report.pdf', pdf_bytes, 'application/pdf')}
    data = {'chat_id': CHAT_ID, 'caption': message}
    try:
        response = requests.post(url, files=files, data=data, timeout=60)
        if response.status_code == 200:
            print("✅ PDF berhasil dikirim ke Telegram.")
        else:
            print(f"❌ Gagal mengirim PDF ke Telegram. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error mengirim PDF ke Telegram: {e}")

# --- FUNGSI UTAMA ---
def main():
    try:
        print("📹 CCTV: Memulai proses analisis institusional...")
        
        # 1. Ambil feed dari RSS
        print("📹 CCTV: Mengambil feed dari RSS Feed...")
        feed = feedparser.parse(RSS_FEED_URL)
        latest_entry = feed.entries[0]
        article_title = latest_entry.title
        article_link = article_link
        article_content = latest_entry.summary
        print(f"✅ CCTV: Berita ditemukan: {article_title}")

        # 2. Analisis dengan AI
        print("📹 CCTV: Mengirim prompt ke Gemini AI untuk dianalisis...")
        prompt = f"""
Bertindak sebagai seorang analis keuangan kuantitatif senior... (PROMPT YANG SAMA SEBELUMNYA)
        ...
        """
        summary_response = model.generate_content(prompt)
        summary_text = summary_response.text
        print("✅ CCTV: Analisis institusional berhasil dibuat.")

        # 3. EKSTRAKSI SENTIMEN
        print("📹 CCTV: Mengekstrak sentimen...")
        sentiment_match = re.search(r'\*\*Sentimen Pasar\*\*\s*\n([^\n]+)', summary_text)
        sentiment = sentiment_match.group(1).strip() if sentiment_match else "Tidak Diketahui"

        # 4. SIMPAN KE DATABASE (DENGAN IZIN PENJAGA MASTER)**
        print("📹 CCTV: Meminta izin ke 'penjaga master'...")
        try:
            response = supabase.rpc("call_function", {"function_name": "allow_anon_insert"})
            if response.data == "OK":
                print("✅ CCTV: Izin dari 'penjaga master' didapatkan.")
            else:
                print("❌ CCTV: Tidak dapat izin dari 'penjaga master'.")
                print(f"Response: {response}")
        except Exception as e:
            print(f"❌ CCTV: Error saat meminta izin: {e}")
                return

        # 5. Coba insert data jika izin didapatkan
        try:
            data_to_insert = {
                "article_title": article_title,
                "article_link": article_link,
                "analysis_result": summary_text,
                "sentiment": sentiment
            }
            response = supabase.table("berita_harian").insert(data_to_insert).execute()
            print("✅ CCTV: Analisis berhasil disimpan ke Supabase.")
        except Exception as e:
            print(f"❌ CCTV: Error saat menyimpan ke Supabase: {e}")

        # 6. Kirim ke Telegram
        final_message = f"📰 **Analisis Institusional (Cointelegraph)**\n\n"
        final_message += f"🔗 [{article_title}]({article_link})\n\n"
        final_message += f"📝 *Laporan Analisis:*\n{summary_text}"
        send_telegram_message(final_message)
        print("🎉 CCTV: SELURUH PROSES SELESAI! Laporan telah dikirim.")

    except Exception as e:
        error_message = f"❌ CCTV: Error terjadi: {e}"
        print(error_message)
        send_telegram_message(f"Maaf, ada error saat mengambil berita: {e}")

if __name__ == "__main__":
    main()
