import json
from django.core.management.base import BaseCommand
from dashboard.models import PDFData, PDFKeyword, User
from django.utils.dateparse import parse_date


class Command(BaseCommand):
    help = 'Restaura os dados PDFData a partir de um arquivo JSON.'

    def add_arguments(self, parser):
        parser.add_argument('json_path', type=str, help='Caminho para o arquivo JSON.')

    def handle(self, *args, **kwargs):
        json_path = kwargs['json_path']

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Erro ao abrir o arquivo: {e}"))
            return

        try:
            user = User.objects.get(username='marcos')
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR("Usuário 'marcos' não encontrado."))
            return

        to_create = []

        for item in data:
            try:
                keyword_obj = PDFKeyword.objects.get(description=item['description'])
            except PDFKeyword.DoesNotExist:
                self.stderr.write(self.style.WARNING(f"Keyword não encontrada: {item['description']}"))
                continue

            to_create.append(PDFData(
                user=user,
                keyword=keyword_obj,
                value_before=item['value_before'],
                value_after=item['value_after'],
                date=parse_date(item['date']),
                playing_time=item.get('playing_time') or None,
                start_time=item.get('start_time') or None,
                duration=item.get('duration') or None
            ))

        PDFData.objects.bulk_create(to_create)
        self.stdout.write(self.style.SUCCESS(f"{len(to_create)} registros inseridos com sucesso."))
