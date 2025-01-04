import imaplib
import email
from email.header import decode_header
import re

def get_otp_from_email(username, password, subject_keyword="MeshChain Account Verification", imap_server="imap.gmail.com"):
    """
    Mengambil OTP dari email berdasarkan subjek tertentu.

    Args:
        username (str): Alamat email (misalnya, email@gmail.com).
        password (str): Password aplikasi untuk akun email.
        subject_keyword (str): Kata kunci dalam subjek email (default: "Verification Code").
        imap_server (str): Server IMAP (default: "imap.gmail.com" untuk Gmail).

    Returns:
        str: OTP yang ditemukan, atau None jika tidak ada OTP.
    """
    try:
        # Hubungkan ke server IMAP
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(username, password)
        mail.select("INBOX")
        
        # Cari email dengan subjek tertentu
        status, messages = mail.search(None, f'SUBJECT "{subject_keyword}"')
        email_ids = messages[0].split()
        
        if email_ids:
            # Ambil email terbaru
            latest_email_id = email_ids[-1]
            status, msg_data = mail.fetch(latest_email_id, "(RFC822)")
            
            # Parsing email
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Ambil isi email
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = msg.get_payload(decode=True).decode()
                    
                    # Ekstraksi OTP menggunakan regex
                    otp_match = re.search(r' <p>Your verification code is: <strong>(\d+)</strong></p>',body)  # Pola untuk 6 karakter alfanumerik
                    if otp_match:
                        return ''.join(char for char in otp_match.group() if char.isdigit())  # Return OTP pertama yang ditemukan

        # Logout dari server
        mail.logout()
        
    except Exception as e:
        print("Error:", e)

    return None  # Jika tidak ada OTP
