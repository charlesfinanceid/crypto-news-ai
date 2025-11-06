import requests
import feedparser
import google.generativeai as genai
import os
import json
import time
import re
from supabase import create_client, Client

# --- KONFIGURASI (HARDCODE UNTUK DEBUG) ---
TELEGRAM_BOT_TOKEN = "8584334724:AAEYYWHHmMLCZ0JLYPF28OzO8nEzTx5l-tA" # GANTI DENGAN TOKEN LENGKAPMU
CHAT_ID = "6594017815" # GANTI DENGAN CHAT ID LENGKAPMU
GEMINI_API_KEY = "AIzaSyDgEo7ovZuCEZe7cFcAJ4fdlD1DDo5a4qk" # GANTI DENGAN API KEY LENGKAPMU
SUPABASE_URL = "https://dcdxctcckfpayhnaeolt.supabase.co"
SUPABASE_KEY = "sb_publishable_TPP--GQASO8F6eUk1ZYzwQ_nd1sRBGU" # GANTI DENGAN SECRET KEY LENGKAPMU
# -----------------------------------------

# RSS Feed
RSS_FEED_URL = "https://cointelegraph.com/rss/tag/bitcoin"

# Inisialisasi Supabase Client
print("📹 CCTV: Menghubungkan ke Supabase...")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("✅ CCTV: Koneksi ke Supabase berhasil.")

# Inisialisasi Gemini AI
print("📹 CCTV: Menghubungkan ke Gemini AI...")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')
print("✅ CCTV: Koneksi ke Gemini AI berhasil.")

# Fungsi untuk mengirim pesan panjang ke Telegram (dipotong jika perlu)
def send_telegram_message(message):
    # ... (fungsi ini sama, tidak perlu diubah)
    print("📹 CCTV: Mengirim pesan ke Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    MAX_MESSAGE_LENGTH = 4000
    if len(message) <= MAX_MESSAGE_LENGTH:
        payload = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown', 'disable_web_page_preview': False}
        try:
            requests.post(url, data=payload, timeout=10)
            print("✅ CCTV: Pesan berhasil dikirim ke Telegram.")
        except requests.exceptions.RequestException as e:
            print(f"❌ CCTV: Error mengirim pesan ke Telegram: {e}")
        return
    print(f"📹 CCTV: Pesan terlalu panjang, memotong menjadi beberapa bagian...")
    parts = []
    while len(message) > 0:
        if len(message) > MAX_MESSAGE_LENGTH:
            part = message[:MAX_MESSAGE_LENGTH]
            last_period_index = part.rfind('.')
            if last_period_index > MAX_MESSAGE_LENGTH * 0.8:
                part = part[:last_period_index + 1]
            parts.append(part)
            message = message[len(part):].lstrip()
        else:
            parts.append(message)
            break
    for i, part in enumerate(parts):
        print(f"📹 CCTV: Mengirim bagian {i+1}/{len(parts)}...")
        payload = {'chat_id': CHAT_ID, 'text': f"📄 ({i+1}/{len(parts)})\n\n{part}", 'parse_mode': 'Markdown', 'disable_web_page_preview': False}
        try:
            requests.post(url, data=payload, timeout=10)
            if i < len(parts) - 1:
                time.sleep(1)
        except requests.exceptions.RequestException as e:
            print(f"❌ CCTV: Error mengirim bagian {i+1}: {e}")

# Fungsi utama
def main():
    print("🚀 SCRIPT NUKLIR SEDANG BERJALAN...")
    print("📹 CCTV: Memulai proses analisis institusional...")
    try:
        # 1. Ambil feed dari RSS
        print("📹 CCTV: Mengambil feed dari RSS Feed...")
        feed = feedparser.parse(RSS_FEED_URL)
        latest_entry = feed.entries[0]
        article_title = latest_entry.title
        article_link = latest_entry.link
        article_content = latest_entry.summary
        print(f"✅ CCTV: Berita ditemukan: {article_title}")

        # 2. Analisis dengan AI
        print("📹 CCTV: Mengirim prompt ke Gemini AI untuk dianalisis...")
        prompt = f"""... (PROMPT YANG SAMA) ..."""
        summary_response = model.generate_content(prompt)
        summary_text = summary_response.text
        print("✅ CCTV: Analisis institusional berhasil dibuat.")

        # 3. EKSTRAK SENTIMEN
        print("📹 CCTV: Mengekstrak sentimen dari hasil analisis...")
        sentiment_match = re.search(r'\*\*Sentimen Pasar\*\*\s*\n([^\n]+)', summary_text)
        sentiment = sentiment_match.group(1).strip() if sentiment_match else "Tidak Diketahui"
        print(f"✅ CCTV: Sentimen yang ditemukan: {sentiment}")

        # 4. SIMPAN KE DATABASE SUPABASE
        print("📹 CCTV: Menyimpan analisis ke database Supabase...")
        data_to_insert = {
            "article_title": article_title,
            "article_link": article_link,
            "analysis_result": summary_text,
            "sentiment": sentiment
        }
        supabase.table("berita_harian").insert(data_to_insert).execute()
        print("✅ CCTV: Analisis berhasil disimpan ke Supabase.")

        # 5. Kirim ke Telegram
        final_message = f"📰 **Analisis Institusional (Cointelegraph)**\n\n"
        final_message += f"🔗 [{article_title}]({article_link})\n\n"
        final_message += f"📝 *Laporan Analisis:*\n{summary_text}"
        send_telegram_message(final_message)
        print("🎉 CCTV: SELURUH PROSES SELESAI! Laporan telah dikirim.")
        
    except Exception as e:
        error_message = f"❌ CCTV: Error terjadi: {e}"
        print(error_message)

if __name__ == "__main__":
    main()
