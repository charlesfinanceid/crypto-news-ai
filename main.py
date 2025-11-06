import requests
import feedparser
import google.generativeai as genai
import os
import json

# --- KONFIGURASI ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# RSS FEED UNTUK BERITA BITCOIN DARI COINTELEGRAPH
RSS_FEED_URL = "https://cointelegraph.com/rss/tag/bitcoin"
# -------------------------

# Cek Environment Variable
if not all([TELEGRAM_BOT_TOKEN, CHAT_ID, GEMINI_API_KEY]):
    raise ValueError("Error: Environment Variable tidak ditemukan.")

# Inisialisasi Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Fungsi untuk mengirim pesan ke Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': False
    }
    try:
        requests.post(url, data=payload, timeout=10)
        print("Pesan berhasil dikirim ke Telegram.")
    except requests.exceptions.RequestException as e:
        print(f"Error mengirim pesan ke Telegram: {e}")

# Fungsi utama
def main():
    print("Memulai proses membaca RSS Feed...")
    try:
        # 1. Ambil feed dari RSS
        feed = feedparser.parse(RSS_FEED_URL)
        
        # Ambil artikel pertama (terbaru)
        latest_entry = feed.entries[0]
        article_title = latest_entry.title
        article_link = latest_entry.link
        article_content = latest_entry.summary # RSS sudah menyediakan ringkasan

        print(f"Berita ditemukan: {article_title}")

        # 2. Meringkas dengan Gemini AI (membuat ringkasan yang lebih baik)
        prompt = f"Tolong ringkas artikel berikut dalam Bahasa Indonesia dengan gaya yang santai dan mudah dimengerti. Berikan 3 poin penting. Judul: {article_title}. Isi: {article_content}"
        summary_response = model.generate_content(prompt)
        summary_text = summary_response.text
        print("Ringkasan berhasil dibuat.")

        # 3. Format pesan dan kirim ke Telegram
        final_message = f"📰 **Berita Bitcoin Terbaru (Cointelegraph)**\n\n"
        final_message += f"🔗 [{article_title}]({article_link})\n\n"
        final_message += f"📝 *Ringkasan:*\n{summary_text}"
        
        send_telegram_message(final_message)
        print("Proses selesai.")
        
    except Exception as e:
        error_message = f"Error terjadi: {e}"
        print(error_message)
        send_telegram_message(f"Maaf, ada error: {e}")

if __name__ == "__main__":
    main()
