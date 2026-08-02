import random
import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google import genai

# ==========================================
# 1. KONFIGURASI BOT & DAFTAR IDE RESEP
# ==========================================
BLOG_ID = "9018939718289832902"  # <--- Pastikan ID Blog kamu sudah benar di sini

DAFTAR_RESEP = [
    "Ayam Goreng Lengkuas Gurih Renyah",
    "Rendang Daging Sapi Khas Padang Empuk",
    "Soto Ayam Lamongan Kuah Gurih Kets",
    "Bumbu Bali Telur Tahu Pedas Manis",
    "Nasi Goreng Kampung Spesial Telur Ceplok",
    "Tongseng Kambing Tanpa Bau Prengus",
    "Pecel Lele Sambal Terasi Khas Lamongan",
    "Gado-Gado Surabaya Bumbu Kacang Kental",
    "Sate Ayam Madura Daging Empuk Bumbu Rengkuh",
    "Sup Buntut Sapi Bening Gurih Kaya Rempah",
    "Pepes Ikan Mas Bumbu Kuning Kemangi",
    "Gulai Cumi Isi Tahu Telur Khas Minang",
    "Rawon Daging Sapi Khas Jawa Timur Hitam Pekat",
]

# ==========================================
# 2. GENERATE KONTEN RESEP PAKAI GEMINI AI
# ==========================================
def buat_artikel_resep_gemini(topik_resep):
    print(f"🤖 Gemini sedang membuat artikel resep: {topik_resep}...")
    
    # Mengambil API Key dari GitHub Secrets
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    prompt = f"""
    Kamu adalah seorang Chef Profesional dan Food Blogger berpengalaman di Indonesia.
    Buatkan artikel resep masakan lengkap untuk blog dengan topik: '{topik_resep}'.
    
    ATURAN FORMAT OUTPUT:
    1. Berikan respon HANYA berupa format HTML murni (tanpa pembungkus ```html ... ```, langsung tag HTML seperti <h2>, <p>, <ul>, <ol>).
    2. Jangan sertakan judul h1 di dalam isi HTML (karena judul dipisah).
    3. Struktur artikel harus rapi, terdiri dari:
       - Paragraf Pembuka yang menggugah selera dan penjelasan singkat masakan.
       - <h3>Bahan-bahan Utama & Bumbu Halus</h3> dalam bentuk unordered list <ul>.
       - <h3>Langkah-Langkah Memasak</h3> dalam bentuk ordered list <ol> detail.
       - <h3>Tips Rahasia Anti Gagal</h3> dalam bentuk bullet points <ul>.
    4. Gunakan bahasa Indonesia yang ramah, hangat, dan menggiurkan khas Food Blogger.
    """
    
# Menggunakan model gemini-2.0-flash
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt
    )
    
    return response.text

# ==========================================
# 3. POSTING KE BLOGGER VIA API
# ==========================================
def post_ke_blogger(judul, isi_html):
    print("🚀 Mengirim artikel ke Blogspot...")
    
    token_info = json.loads(os.environ["BLOGGER_TOKEN"])

    creds = Credentials(
        token=token_info["token"],
        refresh_token=token_info["refresh_token"],
        token_uri=token_info["token_uri"],
        client_id=token_info["client_id"],
        client_secret=token_info["client_secret"],
        scopes=token_info["scopes"],
    )

    service = build("blogger", "v3", credentials=creds)

    body = {
        "kind": "blogger#post",
        "title": judul,
        "content": isi_html,
        "labels": ["Resep Masakan", "Kuliner Nusantara", "Ide Jualan"],
    }

    posts = service.posts()
    hasil = posts.insert(blogId=BLOG_ID, body=body).execute()

    print(f"🎉 BERHASIL! Artikel terbit di: {hasil['url']}")

# ==========================================
# 4. JALANKAN PROGRAM UTAMA
# ==========================================
if __name__ == "__main__":
    # Pilih resep acak dari daftar
    resep_pilihan = random.choice(DAFTAR_RESEP)
    judul_artikel = f"Resep {resep_pilihan} - Praktis, Lezat, dan Bikin Nagih!"
    
    # Generate isi artikel dari Gemini AI
    konten_html = buat_artikel_resep_gemini(resep_pilihan)
    
    # Terbitkan ke Blogspot
    post_ke_blogger(judul_artikel, konten_html)