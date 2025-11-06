import requests
import feedparser
import google.generativeai as genai
import os
import json
import time
import re
from supabase import create_client, Client

# --- KONFIGURASI ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
RSS_FEED_URL = "https://cointelegraph.com/rss/tag/bitcoin"
# -------------------------

# Cek Environment Variable
if not all([TELEGRAM_BOT_TOKEN, CHAT_ID, GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY]):
    raise ValueError("Error: Environment Variable tidak ditemukan.")

# Inisialisasi Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Inisialisasi Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

# Fungsi untuk mengirim pesan panjang ke Telegram (dipotong jika perlu)
def send_telegram_message(message):
    # ... (fungsi ini sama seperti sebelumnya, tidak perlu diubah)
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    MAX_MESSAGE_LENGTH = 4000
    if len(message) <= MAX_MESSAGE_LENGTH:
        payload = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown', 'disable_web_page_preview': False}
        try:
            requests.post(url, data=payload, timeout=10)
            print("Pesan berhasil dikirim ke Telegram.")
        except requests.exceptions.RequestException as e:
            print(f"Error mengirim pesan ke Telegram: {e}")
        return
    print(f"Pesan terlalu panjang ({len(message)} karakter). Memotong menjadi beberapa bagian...")
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
        print(f"Mengirim bagian {i+1}/{len(parts)}...")
        payload = {'chat_id': CHAT_ID, 'text': f"📄 ({i+1}/{len(parts)})\n\n{part}", 'parse_mode': 'Markdown', 'disable_web_page_preview': False}
        try:
            requests.post(url, data=payload, timeout=10)
            if i < len(parts) - 1:
                time.sleep(1)
        except requests.exceptions.RequestException as e:
            print(f"Error mengirim bagian {i+1}: {e}")

# Fungsi utama
def main():
    print("Memulai proses analisis institusional...")
    try:
        # 1. Ambil feed dari RSS
        feed = feedparser.parse(RSS_FEED_URL)
        latest_entry = feed.entries[0]
        article_title = latest_entry.title
        article_link = latest_entry.link
        article_content = latest_entry.summary
        print(f"Berita ditemukan: {article_title}")

        # 2. Analisis dengan AI
        prompt = f"""... (PROMPT BLOOMBERG-MU YANG PANJANG) ..."""
        summary_response = model.generate_content(prompt)
        summary_text = summary_response.text
        print("Analisis institusional berhasil dibuat.")

        # 3. EKSTRAK SENTIMEN (untuk kolom database)
        sentiment_match = re.search(r'\*\*Sentimen Pasar\*\*\s*\n([^\n]+)', summary_text)
        sentiment = sentiment_match.group(1).strip() if sentiment_match else "Tidak Diketahui"

        # 4. SIMPAN KE DATABASE SUPABASE (INI BARU!)
        print("Menyimpan analisis ke database...")
        data_to_insert = {
            "article_title": article_title,
            "article_link": article_link,
            "analysis_result": summary_text,
            "sentiment": sentiment
        }
        supabase.table("berita_harian").insert(data_to_insert).execute()
        print("Analisis berhasil disimpan ke Supabase.")

        # 5. Kirim ke Telegram
        final_message = f"📰 **Analisis Institusional (Cointelegraph)**\n\n"
        final_message += f"🔗 [{article_title}]({article_link})\n\n"
        final_message += f"📝 *Laporan Analisis:*\n{summary_text}"
        send_telegram_message(final_message)
        print("Proses selesai.")
        
    except Exception as e:
        error_message = f"Error terjadi: {e}"
        print(error_message)

if __name__ == "__main__":
    main()
