
import os
import re
from datetime import datetime
from PyPDF2 import PdfReader
from django.db import connection
from dashboard.models import PDFKeyword, PDFData
from django.conf import settings

def get_next_session_number(user, date, activity_type):
    return PDFData.objects.filter(user=user, date=date, activity_type=activity_type).count() + 1

def salvar_pdfdata_sql(user_id, description, value_before, value_after, date, playing_time, start_time, duration, activity_type, session_number ):
    with connection.cursor() as cursor:
        cursor.execute('''
            INSERT INTO dashboard_pdfdata (
                user_id, description, value_before, value_after, date, playing_time, start_time, duration, activity_type, session_number
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', [user_id, description, value_before, value_after, date, playing_time, start_time, duration, activity_type, session_number])


def extract_values_with_context(pdf_path):
    values = []
    date_str = None
    playing_time = None
    start_time = None
    duration = None

    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text = page.extract_text()
            if not text:
                continue
          
            first_line = text.strip().split('\n')[0]
            
            if 'MATCH' in first_line.upper():
                activity_type = 'Game'
            elif 'TRAINING' in first_line.upper():
                activity_type = 'Training'
            else:
                activity_type = 'Game'  # Padrão
        
            text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)

            date_match = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\b\s+(\d{1,2})', text, re.IGNORECASE)
            if date_match:
                month_str, day_str = date_match.groups()
                month_map = {
                    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05',
                    'Jun': '06', 'Jul': '07', 'Aug': '08', 'Sep': '09', 'Sept': '09',
                    'Oct': '10', 'Nov': '11', 'Dec': '12'
                }
                month_str = month_str[:3].capitalize()
                if month_str in month_map:
                    month = month_map[month_str]
                    day = day_str.zfill(2)
                    year = datetime.now().year
                    date_str = f"{year}-{month}-{day}"

            time_match = re.search(r'Time:\s+(\d{1,2}:\d{2}\s*(?:AM|PM)?)\s+Duration:\s+(\d+\s+min)', text)
            if time_match:
                start_time, duration = time_match.groups()

            playing_time_match = re.search(r'Playing Time:\s+(\d+:\d{2})', text)
            if playing_time_match:
                playing_time = playing_time_match.group(1)

            patterns = [
                (k.pattern, k)
                for k in PDFKeyword.objects.exclude(pattern__isnull=True).exclude(pattern__exact='')
            ]

            for pattern, keyword_obj in patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    value_before, value_after = match
                    values.append((keyword_obj.id, value_before, value_after, keyword_obj.description))
            
          

    return values, date_str, playing_time, start_time, duration, activity_type

def process_pdfs_in_folder(folder_path, user):
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)

            values, date_str, playing_time, start_time, duration, activity_type = extract_values_with_context(pdf_path)
            
            session_number = get_next_session_number(user, date_str, activity_type)
            
            for keyword_id, value_before, value_after, description in values:
                try:
                    
    
                    salvar_pdfdata_sql(
                        user.id, description,
                        value_before, value_after,
                        date_str, playing_time, start_time, duration,
                         activity_type, session_number
                    )
                except Exception as e:
                    print(f"Erro ao gravar: {e}")
