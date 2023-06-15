import os
import tempfile
import xhtml2pdf.pisa as pisa
import boto3
import email
from bs4 import BeautifulSoup
import uuid

s3 = boto3.client('s3')


def lambda_handler(event, context):
    # Generate a UUID
    uuid_value = uuid.uuid4()
    # Retrieve the EML file from the event
    eml_file = event['eml_file']

    # Create a temporary directory to store the converted PDF
    temp_dir = tempfile.mkdtemp()

    try:
        # Convert EML to HTML using your preferred method
        html = convert_eml_to_html(eml_file)

        # Generate a unique PDF file name
        pdf_file = os.path.join(temp_dir, 'output.pdf')

        # Convert HTML to PDF using xhtml2pdf
        with open(pdf_file, 'wb') as f:
            pisa.CreatePDF(html, dest=f)

        # Read the generated PDF file
        with open(pdf_file, 'rb') as f:
            pdf_data = f.read()

        # Upload the PDF to an S3 bucket
        s3_bucket = 'your-bucket-name'
        s3_key = 'output.pdf'
        s3.upload_fileobj(pdf_data, s3_bucket, s3_key)

        # Return the S3 URL of the uploaded PDF
        s3_url = f'https://{s3_bucket}.s3.amazonaws.com/{s3_key}'
        return {
            'pdf_url': s3_url
        }
    finally:
        # Clean up temporary files
        for file_name in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, file_name)
            os.remove(file_path)
        os.rmdir(temp_dir)

def convert_eml_to_html(eml_file):
    # Read the EML file
    with open(eml_file, 'r', encoding='utf-8') as file:
        eml_content = file.read()

    # Parse the EML content
    msg = email.message_from_string(eml_content)

    # Extract the HTML content from the EML
    html_content = ''
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == 'text/html':
                html_content = part.get_payload(decode=True).decode('utf-8')
                break
    else:
        content_type = msg.get_content_type()
        if content_type == 'text/html':
            html_content = msg.get_payload(decode=True).decode('utf-8')

    # Perform any additional processing on the HTML content if needed
    # For example, you can use BeautifulSoup to modify or extract specific elements

    # Return the HTML content
    return html_content
