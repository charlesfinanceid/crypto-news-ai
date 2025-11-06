import requests
import os
import reportlab
from supabase import create_client, Client
from datetime import datetime, timedelta
import json

# --- KONFIGURASI (HARDCODE UNTUK DEBUG) ---
TELEGRAM_BOT_TOKEN = "8584334724:AAEYYWHHmMLCZ0JLYPF28OzO8nEzTx5l-tA" # GANTI DENGAN TOKEN LENGKAPMU
CHAT_ID = "6594017815" # GANTI DENGAN CHAT_ID LENGKAPMU
GEMINI_API_KEY = "AIzaSyDgEo7ovZuCEZe7cFcAJ4fdlD1DDo5a4qk" # GANTI DENGAN API KEY LENGKAPMU
SUPABASE_URL = "https://dcdxctcckfpayhnaeolt.supabase.co"
SUPABASE_KEY = "sb_publishable_TPP--GQASO8F6eUk1ZYzwQ_nd1sRBGU" # GANTI DENGAN SECRET KEY LENGKAPMU
# ---------------------------------------

# Inisialisasi
print("📰 MEMULAI PROSES ARSIPAR HARIAN...")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

# Fungsi untuk membuat PDF
def create_pdf_report(content):
    print("📄 Mencetak laporan PDF...")
    try:
        # Membuat PDF
        pdf_bytes = reportlab.SimpleDocTemplate()
        pdf_bytes.build(content)
        return pdf_bytes
    except Exception as e:
        print(f"❌ Error membuat PDF: {e}")
        return None

# Fungsi untuk mengirim PDF ke Telegram
def send_telegram_message(message):
    print("📤 Mengirim PDF ke Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument`
    files = {'document': ('report.pdf', pdf_bytes, 'application/pdf')}
    data = {'chat_id': CHAT_ID, 'caption': message}
    try:
        response = requests.post(url, files=files, data=data, timeout=60)
        if response.status_code == 200:
            print("✅ PDF berhasil dikirim ke Telegram.")
        else:
            print(f"❌ Gagal mengirim PDF ke Telegram. Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error mengirim PDF ke Telegram: {e}")

# Fungsi utama
def main():
    try:
        # 1. Ambil semua berita dari database
        print("📥 Mengambil semua berita dari database...")
        response = supabase.table("berita_harian").select("*").eq("is_reported", False).order("created_at", desc=True).execute()
        articles = response.data
        print(f"✅ Ditemukan {len(articles)} berita untuk dibuat laporan.")

        if not articles:
            print("Tidak ada berita baru untuk dilaporkan.")
            return

        # 2. Buat konten laporan
        report_content = f"""
        📊 **LAPORAN ANALISIS BITCOIN HARIAN**
        📅 Tanggal: {datetime.now().strftime('%d %B %Y')}
        🕐 Waktu Pembuatan: {datetime.now().strftime('%H:%M:%S WIB')}
        
        ---
        
        **RINGKASAN EKSEKUTIF**
        {datetime.now().strftime('%A')}, tidak ada berita signifikan yang mendorong pergerakan pasar secara signifikan. Pasar cenderung bergerak sideways menunggu trigger dari pasar makro ekonomi minggu depan. Analis memprediksi dampak dari inflasi AS masih menjadi faktor utama. Sentimen pasar cenderung netral hingga ada kejelasan yang jelas dari The Fed.
        
        ---
        
        **BERITA TERPENTING HARI INI**
        """
        
        for i, article in articles:
            # Ambil judul dan link
            title = article.get('article_title', 'Tidak ada judul')
            link = article.get('article_link', '#')
            # Ambil ringkasan yang sudah ada
            summary = article.get('analysis_result', 'Tidak ada ringkasan')
            
            # Cek agar tidak terlalu panjang
            if len(summary) > 300:
                summary = summary[:300] + "..."
            
            report_content += f"\n\n**{i+1}. {title}**\n{summary}\n"
            if i < len(articles) - 1:
                report_content += "\n---"

        report_content += f"""
        
        **ANALISIS SENTIMEN**
        """
        
        # Hitung sentimen dari semua berita
        sentiments = [a.get('sentiment', 'Tidak Diketahui') for a in articles]
        if sentiments:
            positive_count = sentiments.count('Positif')
            negative_count = sentiments.count('Negatif')
            if positive_count > negative_count:
                sentimen_text = f"Secara umum, sentimen cenderung **Positif** ({positive_count} berita positif, {negative_count} berita negatif)."
            elif negative_count > positive_count:
                sentimen_text = f"Secara umum, sentimen cenderung **Negatif** ({negative_count} berita positif, {positive_count} berita negatif)."
            else:
                sentimen_text = "Secara umum, sentimen cenderung **Netral**."
        else:
            sentimen_text = "Tidak ada data sentimen."
        
        report_content += f"""
        
        **REKOMENDASI**
        
        {sentiment_text}
        
        ---
        
        **Sistem ini adalah analisis berbasis AI. Selalu lakukan riset mandiri sebelum membuat keputusan investasi.**
        """
        
        # 3. Buat PDF
        pdf_bytes = create_pdf_report(report_content)
        if pdf_bytes:
            # 4. Kirim ke Telegram
            message = f"📄 Laporan Analisis Harian ({datetime.now().strftime('%d %B %Y')})"
            send_telegram_message(message, files={'document': ('report.pdf', pdf_bytes, 'application/pdf')})
            # 5. Update status di database
            for article in articles:
                supabase.table("berita_harian").update({"is_reported": True}).eq("id", article["id"]).execute()
            print("✅ Semua data sudah ditandai sebagai sudah dilaporkan.")
        else:
            print("❌ Gagal membuat PDF, laporan tidak dikirim.")
        
    except Exception as e:
        print(f"❌ Error dalam proses arsip harian: {e}")

if __name__ == "__main__":
    main()
