import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
import json

# --- KONFIGURASI (Diambil dari Secrets GitHub) ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# -----------------------------------------

# Cek apakah semua environment variable sudah terisi
if not all([TELEGRAM_BOT_TOKEN, CHAT_ID, GEMINI_API_KEY]):
    raise ValueError("Error: Satu atau lebih Environment Variable (TOKEN/CHAT_ID/API_KEY) tidak ditemukan. Silakan periksa Settings > Secrets di GitHub.")

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
    print("Memulai proses scraping dan summarizing...")
    try:
        # 1. Scraping halaman utama berita
        news_url = "https://www.cryptocraft.com/news"
        # --- HEADERS BARU UNTUK MENYAMAR ---
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Dnt': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        # ------------------------------------
        response = requests.get(news_url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # 2. Mencari artikel terbaru
        first_article_container = soup.find('div', class_='jeg_postblock_content')
        if not first_article_container:
            raise Exception("Tidak bisa menemukan container artikel. Mungkin struktur web sudah berubah.")
        
        first_article = first_article_container.find('a')
        if not first_article:
            raise Exception("Tidak bisa menemukan link artikel pertama.")

        article_title = first_article.get_text(strip=True)
        article_link = first_article['href']
        print(f"Berita ditemukan: {article_title}")

        # 3. Mengambil isi artikel lengkap
        article_response = requests.get(article_link, headers=headers, timeout=15)
        article_response.raise_for_status()
        article_soup = BeautifulSoup(article_response.content, 'html.parser')
        
        content_div = article_soup.find('div', class_='content-inner')
        if not content_div:
            raise Exception("Tidak bisa menemukan isi artikel. Mungkin struktur web sudah berubah.")
        
        article_content = content_div.get_text(strip=True)

        # 4. Meringkas dengan Gemini AI
        prompt = f"Tolong ringkas artikel berikut dalam Bahasa Indonesia dengan gaya yang santai dan mudah dimengerti. Berikan 3 poin penting. Judul: {article_title}. Isi: {article_content}"
        summary_response = model.generate_content(prompt)
        summary_text = summary_response.text
        print("Ringkasan berhasil dibuat.")

        # 5. Format pesan dan kirim ke Telegram
        final_message = f"📰 **Berita Terbaru dari CryptoCraft**\n\n"
        final_message += f"🔗 [{article_title}]({article_link})\n\n"
        final_message += f"📝 *Ringkasan:*\n{summary_text}"
        
        send_telegram_message(final_message)
        print("Proses selesai.")
        
    except Exception as e:
        error_message = f"Error terjadi: {e}"
        print(error_message)
        send_telegram_message(f"Maaf, ada error saat mengambil berita: {e}")

if __name__ == "__main__":
    main()
