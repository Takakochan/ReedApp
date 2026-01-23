import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from reedsdata.models import Reedsdata
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Import reed data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='actual_data_lab/oboe_reeds_log_Lanthier_cleaned_english.csv',
            help='Path to CSV file relative to project root'
        )
        parser.add_argument(
            '--user',
            type=str,
            default='takako',
            help='Username to assign as reed author'
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip records that already exist'
        )

    def parse_date(self, date_str):
        """Parse various date formats from CSV"""
        if not date_str or date_str.strip() in ['', '?', '-']:
            return None

        # Try different date formats
        date_formats = [
            '%d.%m.%y',     # 03.11.23
            '%d/%m/%y',     # 03/11/23
            '%m/%d/%y',     # 11/03/23
            '%d.%m.%Y',     # 03.11.2023
            '%d/%m/%Y',     # 03/11/2023
            '%Y-%m-%d',     # 2023-11-03
        ]

        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                # If year is < 100, assume it's 20xx
                if dt.year < 100:
                    dt = dt.replace(year=2000 + dt.year)
                return timezone.make_aware(dt)
            except ValueError:
                continue

        self.stdout.write(self.style.WARNING(f'Could not parse date: {date_str}'))
        return None

    def parse_int(self, value):
        """Parse integer values, handling empty strings and special characters"""
        if not value or str(value).strip() in ['', '?', '-', 'many']:
            return None
        try:
            # Handle "many" as a high number
            if str(value).lower() == 'many':
                return 999
            return int(float(str(value).strip()))
        except (ValueError, TypeError):
            return None

    def parse_float(self, value):
        """Parse float values, handling empty strings and special characters"""
        if not value or str(value).strip() in ['', '?', '-']:
            return None
        try:
            # Replace comma with period for European number format
            value_str = str(value).replace(',', '.')
            return float(value_str.strip())
        except (ValueError, TypeError):
            return None

    def combine_notes(self, row):
        """Combine all note fields into one"""
        note_fields = [
            ('notes', row.get('notes', '')),
            ('first_scraping_notes', row.get('first_scraping_notes', '')),
            ('day_2_notes', row.get('day_2_notes', '')),
            ('day_3_notes', row.get('day_3_notes', '')),
            ('day_4_notes', row.get('day_4_notes', '')),
            ('additional_notes', row.get('additional_notes', '')),
        ]

        combined = []
        for label, value in note_fields:
            if value and str(value).strip() not in ['', '?', '-']:
                if label == 'notes':
                    combined.append(f'{value}')
                elif label == 'first_scraping_notes':
                    combined.append(f'1er grattage: {value}')
                elif label == 'day_2_notes':
                    combined.append(f'2e jour: {value}')
                elif label == 'day_3_notes':
                    combined.append(f'3e jour: {value}')
                elif label == 'day_4_notes':
                    combined.append(f'4e jour: {value}')
                else:
                    combined.append(f'{value}')

        return ' | '.join(combined) if combined else None

    def map_cane_brand(self, cane_value):
        """Map cane values to standardized brand names"""
        if not cane_value or str(cane_value).strip() in ['', '?', '-']:
            return 'Other'

        cane_str = str(cane_value).upper()

        # Check for known brands
        if 'RL' in cane_str or 'RIGOTTI' in cane_str:
            return 'Rigotti'
        elif 'MA' in cane_str or 'MEDIR' in cane_str:
            return 'Medir'
        elif 'R2' in cane_str:
            return 'Rigotti'
        else:
            return 'Other'

    def handle(self, *args, **options):
        file_path = options['file']
        username = options['user']
        skip_existing = options['skip_existing']

        # Get user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} not found'))
            return

        # Check if file exists
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Importing from: {file_path}'))
        self.stdout.write(f'Author: {user.username}')

        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0

        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row_num, row in enumerate(reader, start=2):  # Start at 2 because row 1 is header
                try:
                    reed_number = row.get('number', '').strip()

                    # Skip empty rows
                    if not reed_number or reed_number in ['', '?', '-']:
                        continue

                    # Check if record exists
                    if skip_existing:
                        if Reedsdata.objects.filter(reed_ID=reed_number, reedauthor=user).exists():
                            skipped_count += 1
                            continue

                    # Parse data
                    date_value = self.parse_date(row.get('first_scraping_date', ''))
                    if not date_value:
                        date_value = timezone.now()

                    # Create or update reed
                    reed, created = Reedsdata.objects.update_or_create(
                        reed_ID=reed_number,
                        reedauthor=user,
                        defaults={
                            'instrument': row.get('instrument', '').strip() or None,
                            'cane_brand': self.map_cane_brand(row.get('cane', '')),
                            'diameter': self.parse_int(row.get('diameter', '')),
                            'gouging_machine': row.get('gouge', '').strip() or None,
                            'hardness': self.parse_float(row.get('exterior_hardness', '')),
                            'counts_rehearsal': self.parse_int(row.get('rehearsal_count', '')),
                            'counts_concert': self.parse_int(row.get('concert_count', '')),
                            'date': date_value,
                            'note': self.combine_notes(row),
                        }
                    )

                    if created:
                        created_count += 1
                        self.stdout.write(f'Created reed #{reed_number}')
                    else:
                        updated_count += 1
                        self.stdout.write(f'Updated reed #{reed_number}')

                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f'Error on row {row_num}: {str(e)}'))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== Import Summary ==='))
        self.stdout.write(self.style.SUCCESS(f'Created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'Updated: {updated_count}'))
        if skipped_count:
            self.stdout.write(self.style.WARNING(f'Skipped: {skipped_count}'))
        if error_count:
            self.stdout.write(self.style.ERROR(f'Errors: {error_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total: {created_count + updated_count}'))
