import json
from google_auth_oauthlib.flow import InstalledAppFlow

# Scope izin untuk mengelola postingan Blogger
SCOPES = ["https://www.googleapis.com/auth/blogger"]


def main():
    try:
        # Membaca file client_secret.json dari Google Cloud Console
        flow = InstalledAppFlow.from_client_secrets_file(
            "client_secret.json", SCOPES
        )

        # MENGATUR OFFLINE ACCESS & PROMPT CONSENT
        # Ini Wajib agar Google menerbitkan 'refresh_token' yang bertahan lama untuk bot!
        creds = flow.run_local_server(
            port=0, access_type="offline", prompt="consent"
        )

        # Menyusun data kredensial menjadi bentuk JSON
        token_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
        }

        print("\n" + "=" * 50)
        print("✅ SALIN SELURUH TEKS DI BAWAH INI (DARI { SAMPAI }):")
        print("=" * 50)
        print(json.dumps(token_data))
        print("=" * 50 + "\n")

    except FileNotFoundError:
        print("\n❌ ERROR: File 'client_secret.json' tidak ditemukan!")
        print(
            "Pastikan kamu sudah menaruh file 'client_secret.json' di folder yang sama dengan skrip ini.\n"
        )


if __name__ == "__main__":
    main()
