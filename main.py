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
# --- INI ADALAH BAGIAN KRUSIAL ---
SUPABASE_URL = "https://dcdxctcckfpayhnaeolt.supabase.co"
SUPABASE_KEY = "sb_secret_LFK4GNyfSetzoIBOUYYLVg_rEVyT0FX" # GANTI DENGAN SECRET KEY LENGKAPMU
# -----------------------------------------

# RSS Feed
RSS_FEED_URL = "https://cointelegraph.com/rss/tag/bitcoin"

# Cek Environment Variable (kita lewati dulu untuk debug)
# if not all([TELEGRAM_BOT_TOKEN, CHAT_ID, GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY]):
#     raise ValueError("Error: Environment Variable tidak ditemukan.")

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
    print("🚀 SCRIPT NUKLIR SEDANG BERJALAN...") # Ini penanda bahwa script yang benar yang jalan
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
        prompt = f"""
Bertindak sebagai seorang analis keuangan kuantitatif senior dengan 15+ tahun pengalaman di institusi tier-1. Lakukan analisis mendalam dan objektif terhadap artikel berikut dengan fokus pada implikasi pasar yang actionable. Sajikan output dalam Bahasa Indonesia dengan format Markdown yang terstruktur, padat, dan mudah dipindai untuk decision-making cepat.

**Prinsip Analisis:**
- Hindari kalimat pembuka/penutup umum atau disclaimer berlebihan
- Gunakan bahasa presisi teknis tanpa mengorbankan kejelasan
- Berikan konteks historis ketika relevan dengan signifikansi pasar
- Prioritaskan data konkret atas spekulasi
- Identifikasi tail risks dan black swan scenarios

---

Lakukan analisis mendalam mengikuti format di bawah ini dengan presisi analisis Bloomberg-grade:

### **Analisis Utama**
[Satu kalimat kesimpulan inti yang menjawab: apa berita ini, mengapa penting sekarang, dan dampak makro/mikronya]

### **Fokus Aset**
[Aset utama yang terpengaruh: BTC / ETH / Altcoins / Forex / Equities / Commodities / Multi-Aset / Sektor Spesifik]

### **Timeframe Relevan**
[Jangka Pendek (Intraday/1D) / Menengah (3D-2W) / Panjang (>1 Bulan) / Multi-Horizon]

### **Sentimen Pasar**
[Positif / Negatif / Netral / Mixed — dengan tingkat kepercayaan 1-5]

### **Katalisator Utama**
[Apa penyebab fundamental/teknis utama dari berita ini dalam 1-2 kalimat. Bedakan antara surprise element vs priced-in element]

### **Data Kunci & Metrik**
[Daftar angka, perubahan persentase, rasio, volume, atau metrik penting yang disebutkan atau dapat disimpulkan. Format: 
- Metrik 1: X unit
- Metrik 2: Y%
- Metrik 3: Z perubahan vs periode referensi]

### **Implikasi Harga & Mekanisme**
[Jelaskan dampak potensial pada harga aset utama melalui:
1. Channel fundamental (valuasi, cash flows, risk premium)
2. Channel teknikal (breakout, rejection, volume confirmation)
3. Channel behavioral (momentum, position unwind, volatility regime change)
Gunakan 2-4 kalimat dengan logika causal yang jelas]

### **Estimasi Pengaruh Intraperiode**
[Estimasi jangka pendek dampak harga:
- Skenario Base: [+/- X%]
- Skenario Bull: [+Y%]
- Skenario Bear: [-Z%]
Berikan probability-weighted outcome atau range yang masuk akal]

### **Level Watch Teknikal**
[Sebutkan support/resistance levels yang relevan berdasarkan:
- Current price action dan struktur
- Fibonacci retracements atau pivot points jika relevan
- Volume cluster atau historical levels
Format: 
- Resistance 1: Level A ($XXX)
- Resistance 2: Level B ($XXX)
- Support 1: Level C ($XXX)
- Support 2: Level D ($XXX)
- Break level (critical): Level E ($XXX)]

### **Sudut Pandang Kontrarian & Hidden Risks**
[Identifikasi 1-2 risiko atau interpretasi berlawanan dari narasi pasar mainstream:
1. Apa yang bisa salah dari consensus bullish/bearish?
2. Apa second-order effects yang sering diabaikan?
3. Adakah historical precedent yang mengindikasikan outcome berbeda?]

### **Aset & Sektor Terkait**
[Sebutkan aset lain yang likely terpengaruh via correlation/causation:
- Aset 1 (korelasi: +0.X / dampak: Positif/Negatif)
- Aset 2 (mekanisme: risk-on/risk-off, flight-to-safety, dll)
- Sektor 3 (exposure via: supply chain, regulatory, dll)
Berikan logika penularannya]

### **Catatan Probabilitas & Confidence Level**
[Optional tapi recommended: Sebutkan tingkat confidence analisis ini (60% / 75% / 85%+) dan asumsi kunci yang membuat analisis ini valid atau tidak valid]

---

**Judul Artikel:** {article_title}

**Isi Artikel:**
{article_content}
"""
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
