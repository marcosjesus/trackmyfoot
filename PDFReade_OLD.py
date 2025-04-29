
import os
import re
from datetime import datetime
from PyPDF2 import PdfReader
from dashboard.models import PDFData, PDFKeyword
import json

def extract_values_with_context(pdf_path):
    extracted_data = []
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

            text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)

            # Detecta a data
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

            # Detecta horário e duração
            time_match = re.search(r'Time:\s+(\d{1,2}:\d{2}\s*(?:AM|PM)?)\s+Duration:\s+(\d+\s+min)', text)
            if time_match:
                start_time, duration = time_match.groups()

            # Detecta tempo de jogo
            playing_time_match = re.search(r'Playing Time:\s+(\d+:\d{2})', text)
            if playing_time_match:
                playing_time = playing_time_match.group(1)

            # Carrega padrões do banco
            patterns = [
                (k.pattern, k)
                for k in PDFKeyword.objects.exclude(pattern__isnull=True).exclude(pattern__exact='')
            ]

            for pattern, keyword_obj in patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    try:
                        value_before, value_after = match
                        extracted_data.append((keyword_obj, value_before.strip() if value_before else '', value_after.strip() if value_after else ''))
                    except ValueError:
                        continue  # Ignora correspondência que não tem dois grupos

    return extracted_data, date_str, playing_time, start_time, duration


def export_data_to_json(data_list, output_path='pdfdata_backup.json'):
    data_serialized = []
    for obj in data_list:
        data_serialized.append({
            'user': obj.user.username,
            'description': obj.description,
            'value_before': obj.value_before,
            'value_after': obj.value_after,
            'date': obj.date,
            'playing_time': obj.playing_time,
            'start_time': obj.start_time,
            'duration': obj.duration
        })
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data_serialized, f, indent=4, ensure_ascii=False)


def process_pdfs_in_folder(folder_path, user):
    data_to_save = []

    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            values, date_str, playing_time, start_time, duration = extract_values_with_context(pdf_path)

            for keyword_obj, value_before, value_after in values:
                description = keyword_obj.description.strip() if keyword_obj.description else ''
                value_before = value_before.strip() if value_before else ''
                value_after = value_after.strip() if value_after else ''
                date_str = date_str.strip() if date_str else ''
                playing_time = playing_time.strip() if playing_time else ''
                start_time = start_time.strip() if start_time else ''
                duration = duration.strip() if duration else ''


                data_to_save.append(PDFData(
                    user=user,
                    description=description,
                    value_before=value_before,
                    value_after=value_after,
                    date=date_str,
                    playing_time=playing_time,
                    start_time=start_time,
                    duration=duration
                ))

            # 🔄 Grava todos os dados extraídos de uma vez só
            valid_data = []
            for data in data_to_save:
                if data.description is None:
                    f"[SKIP] keyword_id ausente em: {data}")
                else:
                    valid_data.append(data)


