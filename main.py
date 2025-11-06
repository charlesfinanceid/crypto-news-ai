# 4. SIMPAN KE DATABASE SUPABASE (INI BARU!)
print("📹 CCTV: Menyimpan analisis ke database Supabase...")
data_to_insert = {
    "article_title": article_title,
    "article_link": article_link,
    "analysis_result": summary_text,
    "sentiment": sentiment
}
# --- PERUBAHAN INI ---
# Gunakan fungsi RPC (Remote Procedure Call) untuk memanggil fungsi di database
response = supabase.rpc("call_function", {"function_name": "allow_anon_insert"})
if response.data:
    print("✅ CCTV: Izin dari 'penjaga master' didapatkan.")
else:
    print("❌ CCTV: Tidak dapat izin dari 'penjaga master'.")
    return

# Coba insert data menggunakan izin dari 'penjaga master'
try:
    response = supabase.table("berita_harian").insert(data_to_insert).execute()
    print("✅ CCTV: Analisis berhasil disimpan ke Supabase.")
except Exception as e:
    print(f"❌ CCTV: Error saat menyimpan ke Supabase: {e}")
