import psycopg2
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from datetime import date, datetime

class DatabaseManager:
    def __init__(self, dbname, user, password, host, port):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.conn.cursor()

    def execute_query(self, query, params=None):
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetch_one(self, query, params=None):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def close(self):
        self.cursor.close()
        self.conn.close()


class EmailManager:
    def __init__(self, from_email, from_password):
        self.from_email = from_email
        self.from_password = from_password

    def send_email(self, to_email, subject, body, attachment_path):
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with open(attachment_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
            msg.attach(part)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.set_debuglevel(1)  # Tambahkan debugging level
            server.starttls()
            server.login(self.from_email, self.from_password)
            server.sendmail(self.from_email, to_email, msg.as_string())
            server.quit()
        print(f"Email sent to {to_email}")


class InvoiceManager:
    def __init__(self, db_manager, email_manager):
        self.db_manager = db_manager
        self.email_manager = email_manager

    def save_user(self, type_user, email, password_hash):
        query = """
            INSERT INTO public."user" (type_user, email, password_hash)
            VALUES (%s, %s, %s)
        """
        self.db_manager.execute_query(query, (type_user, email, password_hash))

    def save_invoice(self, invoice_id, email, invoice_data, pdf_path):
        with open(pdf_path, 'rb') as pdf_file:
            pdf_data = pdf_file.read()
        creation_date = datetime.today().date()

        query = """
            INSERT INTO public.invoice_input (invoice_id, email, json_file_input, pdf_file_name, pdf_file_input, creation_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.db_manager.execute_query(query, (invoice_id, email, json.dumps(invoice_data), os.path.basename(pdf_path), psycopg2.Binary(pdf_data), creation_date))
        self.email_manager.send_email(email, "Invoice PDF", "Please find attached the invoice PDF.", pdf_path)

    def get_invoice(self, invoice_id, output_pdf_path):
        query = """
            SELECT json_file_input, pdf_file_input
            FROM public.invoice_input
            WHERE invoice_id = %s
        """
        record = self.db_manager.fetch_one(query, (invoice_id,))
        
        if record:
            invoice_data, pdf_data = record
            print("Invoice Data:", invoice_data)  # invoice_data sudah berupa dictionary

            with open(output_pdf_path, 'wb') as pdf_file:
                pdf_file.write(pdf_data)
            print(f"PDF file saved to {output_pdf_path}")
        else:
            print(f"Invoice with ID {invoice_id} not found.")


# Pengaturan dan koneksi
db_manager = DatabaseManager(
    dbname=os.getenv("DB_NAME", "einvoice"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASS", "renbo123"),
    host=os.getenv("DB_HOST", "db"),  # Note the host is 'db' as defined in docker-compose
    port="5432"
)

email_manager = EmailManager(
    from_email="kerenomad@gmail.com",
    from_password="udvqfubocncnqbki"  # Sandi aplikasi
)

invoice_manager = InvoiceManager(db_manager, email_manager)

# Insert users
invoice_manager.save_user('admin', 'kerenomad@gmail.com', 'hashed_password_1')
invoice_manager.save_user('user', 'henry_sab@yahoo.com', 'hashed_password_2')

# Contoh penggunaan
invoice_id = "INV003"
email = "henry_sab@yahoo.com"
invoice_data = {
    "customer": "John Wick",
    "amount": 1500,
    "items": [
        {"item": "Laptop", "price": 1000},
        {"item": "Mouse", "price": 500}
    ]
}
pdf_path = "input_invoice.pdf"
output_pdf_path = "retrieved_invoice.pdf"

# Simpan data JSON dan file PDF ke database
invoice_manager.save_invoice(invoice_id, email, invoice_data, pdf_path)

# Ambil dan tampilkan data dari database
invoice_manager.get_invoice(invoice_id, output_pdf_path)

# Tutup koneksi
db_manager.close()
