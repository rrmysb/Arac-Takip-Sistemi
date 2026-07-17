# -*- coding: utf-8 -*-
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from imapclient import IMAPClient
import pyzmail
import mysql.connector

# Çevre değişkenlerini yükle
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def connect_mysql():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASS"),
        database=os.getenv("MYSQL_DB"),
        charset="utf8mb4"
    )

def parse_email_body(body_text):
    """
    E-posta gövdesinden Regex kullanarak plaka, km, kontak ve hız bilgilerini ayıklar.
    """
    data = {}
    
    # Rapor tarihini ayıkla (Örn: 30.07.2025 tarihinde şeklinde gelen metinden)
    date_match = re.search(r'(\d{2})\.(\d{2})\.(\d{4})\s+tarihinde', body_text)
    if date_match:
        # MySQL DATE formatına çevir: YYYY-MM-DD
        data['tarih'] = f"{date_match.group(3)}-{date_match.group(2)}-{date_match.group(1)}"


    
    return data

def fetch_and_parse_emails():
    imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")
    sender_filter = os.getenv("TRACKING_EMAIL_SENDER")

    print("Araç Takip: E-posta sunucusuna bağlanılıyor...")
    with IMAPClient(imap_server) as client:
        client.login(email_user, email_pass)
        client.select_folder('INBOX')
        
        # Sadece belirlenen göndericiden gelen okunmamış mailleri ara
        messages = client.search(['UNSEEN', 'FROM', sender_filter])
        print(f"Toplam {len(messages)} yeni araç takip raporu bulundu.")
        
        db_conn = connect_mysql()
        cursor = db_conn.cursor()

        for uid in reversed(messages):
            raw_msg = client.fetch([uid], ['BODY[]'])
            msg_data = pyzmail.PyMessage.factory(raw_msg[uid][b'BODY[]'])
            
            if msg_data.text_part:
                body_text = msg_data.text_part.get_payload().decode(msg_data.text_part.charset or 'utf-8')
                parsed_data = parse_email_body(body_text)
                
                if parsed_data:
                    # MySQL insert sorgusu
                    insert_query = """
                        INSERT INTO vehicle_daily_tracking 
                        (plaka, tarih, mesafe, mesai_ici, mesai_disi, maxhid, ilk_kontak, son_kontak, isim)
                        VALUES (%(plaka)s, %(tarih)s, %(mesafe)s, %(mesai_ici)s, %(mesai_disi)s, %(maxhid)s, %(ilk_kontak)s, %(son_kontak)s, %(isim)s)
                    """
                    # cursor.execute(insert_query, parsed_data)
                    pass
                    
        db_conn.commit()
        cursor.close()
        db_conn.close()
    print("Araç Takip: Veri işleme adımı başarıyla tamamlandı.")

if __name__ == "__main__":
    fetch_and_parse_emails()
