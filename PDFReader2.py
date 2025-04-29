import PyPDF2
import re
import os
from datetime import datetime
from dashboard.models import PDFKeyword, PDFData
from django.db import connection

def get_next_session_number(user, date, activity_type):
    return PDFData.objects.filter(user=user, date=date, activity_type=activity_type).count() + 1

def salvar_pdfdata_sql(user_id, description, value_before, value_after, date, playing_time, start_time, duration, activity_type, session_number):
    with connection.cursor() as cursor:
        try:
            cursor.execute('''
                INSERT INTO dashboard_pdfdata (
                    user_id, description, value_before, value_after, date, playing_time, start_time, duration, activity_type, session_number
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', [user_id, description, value_before, value_after, date, playing_time, start_time, duration, activity_type, session_number])
        except Exception as e:
            print(f"Erro ao gravar: {e}")

def extract_leg_use_value(pdf_path):
    values = []

    date_value = None
    time_value = None
    start_time_value = None
    duration_value = None

    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)

        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)
        
            first_line = text.strip().split('\n')[0]
            
            if 'MATCH' in first_line.upper():
                activity_type = 'Game'
            elif 'TRAINING' in first_line.upper():
                activity_type = 'Training'
            else:
                activity_type = 'Game'  # Padrão

            # 📆 Extrai MES e DIA do conteúdo
            date_match = re.search(r'DATE\s*([A-Za-z]+)\s+(\d{1,2})', text)
            if date_match:
                month_str, day_str = date_match.groups()
                try:
                    date_value = datetime.strptime(f"{month_str} {day_str} {datetime.now().year}", "%b %d %Y").date()
                except ValueError:
                    date_value = None

            time_match = re.search(r'PLAYING\s*TIME\s*(\d{1,2}\s*Min\.)', text)
            start_time_match = re.search(r'START\s*TIME\s*(\d{1,2}:\d{2})', text)
            duration_match = re.search(r'DURATION\s*(\d+)\s*Min\.', text)

            if time_match:
                time_value = time_match.group(1)
            if start_time_match:
                start_time_value = start_time_match.group(1)
            if duration_match:
                duration_value = duration_match.group(1)

            leg_use_index = text.find("Leg Use (%)")
            if leg_use_index != -1:
                after = text[leg_use_index:]
                before = text[:leg_use_index]

                match_after = re.search(r'L\s*(\d+)\s*\|\s*R\s*(\d+)', after)
                match_before = re.search(r'L\s*(\d+)\s*\|\s*R\s*(\d+)', before)

                if match_after and match_before:
                    leg_use_value_L = match_after.group(1)
                    leg_use_value_R = match_after.group(2)
                    leg_use_before_value_L = match_before.group(1)
                    leg_use_before_value_R = match_before.group(2)

                    values.append(("Leg Use (%) L", leg_use_before_value_L, leg_use_value_L))
                    values.append(("Leg Use (%) R", leg_use_before_value_R, leg_use_value_R))

    return values, date_value, time_value, start_time_value, duration_value, activity_type

def process_pdfs_in_folder(folder_path, user):
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            print(f"📄 Processando {filename}...")

            values, date_value, time_value, start_time_value, duration_value, activity_type = extract_leg_use_value(pdf_path)

            if not date_value:
                print(f"⚠️ Data ausente — dados de {filename} não serão salvos.")
                continue

            for keyword_text, before, after in values:
                try:
                    keyword_obj = PDFKeyword.objects.get(description=keyword_text)
                except PDFKeyword.DoesNotExist:
                    print(f"❌ Keyword '{keyword_text}' não encontrada na tabela PDFKeyword.")
                    continue
                
                session_number = get_next_session_number(user, date_value, activity_type)

                salvar_pdfdata_sql(
                    user_id=user.id,
                    description=keyword_obj.description,
                    value_before=before,
                    value_after=after,
                    date=date_value,
                    playing_time=time_value,
                    start_time=start_time_value,
                    duration=duration_value,
                    activity_type=activity_type,
                    session_number=session_number,
                )

            print(f"✅ Dados gravados no banco para {filename}")
