#!/usr/bin/env python
"""
Import reed data from Excel file to Django database
"""
import os
import sys
import django
import pandas as pd
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reedmanage.settings')
django.setup()

from django.contrib.auth.models import User
from reedsdata.models import Reedsdata

def parse_diameter(value):
    """Parse diameter value, handling '?' and other issues"""
    if pd.isna(value) or value == '?':
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None

def parse_float(value):
    """Parse float value safely"""
    if pd.isna(value):
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def parse_date(value):
    """Parse date from various formats"""
    if pd.isna(value):
        return None
    try:
        if isinstance(value, str):
            # Try DD.MM.YY format
            return datetime.strptime(value, '%d.%m.%y')
        elif isinstance(value, datetime):
            return value
    except (ValueError, TypeError):
        pass
    return None

def map_cane_brand(roseau):
    """Map French cane brand names to choices"""
    if pd.isna(roseau):
        return 'Other'

    roseau = str(roseau).upper()

    # Mapping logic
    if 'RIGOT' in roseau or 'R923' in roseau or 'R23' in roseau:
        return 'Rigotti'
    elif 'MEDIR' in roseau or 'MEDI' in roseau:
        return 'Medir'
    elif 'GHYS' in roseau:
        return 'Ghys'
    elif 'GLOTIN' in roseau:
        return 'Glotin'
    elif 'PISONI' in roseau:
        return 'Pisoni'
    elif 'DANZI' in roseau:
        return 'Danzi'
    elif 'EMERALD' in roseau:
        return 'Emerald'
    elif 'HO' in roseau:
        return 'Other'
    else:
        return 'Other'

def map_gouging_machine(gouge):
    """Map gouge values to choices"""
    if pd.isna(gouge):
        return None

    gouge = str(gouge).upper()

    if 'RS' in gouge or 'REED' in gouge:
        return 'Reeds \'n Stuff'
    elif 'GRAF' in gouge:
        return 'Graf'
    elif 'ROSS' in gouge:
        return 'Ross'
    elif 'RIEGER' in gouge:
        return 'Rieger'
    elif 'WEBER' in gouge:
        return 'Weber'
    else:
        return 'Other'

def combine_notes(row):
    """Combine all note fields into one"""
    notes_parts = []

    if pd.notna(row.get('notes')):
        notes_parts.append(f"Notes: {row['notes']}")
    if pd.notna(row.get('notes premier grattage')):
        notes_parts.append(f"1er grattage: {row['notes premier grattage']}")
    if pd.notna(row.get('Notes 2e jour')):
        notes_parts.append(f"2e jour: {row['Notes 2e jour']}")
    if pd.notna(row.get('notes 3e jour')):
        notes_parts.append(f"3e jour: {row['notes 3e jour']}")

    return ' | '.join(notes_parts) if notes_parts else None

def import_data(excel_path, user):
    """Import data from Excel file"""
    print(f"Reading Excel file: {excel_path}")
    df = pd.read_excel(excel_path)

    print(f"Total rows: {len(df)}")

    # Filter rows with reed number
    df = df[df['numéro'].notna()]
    print(f"Rows with reed number: {len(df)}")

    imported_count = 0
    skipped_count = 0
    error_count = 0

    for idx, row in df.iterrows():
        try:
            # Extract reed ID
            reed_id = str(int(row['numéro']))

            # Check if already exists
            if Reedsdata.objects.filter(reed_ID=reed_id, reedauthor=user).exists():
                print(f"  Skipping #{reed_id} - already exists")
                skipped_count += 1
                continue

            # Create reed data object
            reed = Reedsdata(
                reed_ID=reed_id,
                reedauthor=user,
                cane_brand=map_cane_brand(row.get('roseau')),
                diameter=parse_diameter(row.get('diamètre')),
                gouging_machine=map_gouging_machine(row.get('gouge')),
                hardness=parse_float(row.get('dureté extérieure (duromètre)')),
                counts_rehearsal=parse_float(row.get('Répèt (nombre de répèt)')),
                counts_concert=parse_float(row.get('Concerts (nombre de concert)')),
                instrument=row.get('instrument') if pd.notna(row.get('instrument')) else None,
                note=combine_notes(row),
            )

            # Try to parse date
            date = parse_date(row.get('date premier grattage'))
            if date:
                reed.date = date
                reed.global_quality_first_impression_date = date

            reed.save()
            imported_count += 1

            if imported_count % 50 == 0:
                print(f"  Imported {imported_count} reeds...")

        except Exception as e:
            print(f"  Error importing row {idx} (reed #{row.get('numéro')}): {e}")
            error_count += 1
            continue

    print(f"\n{'='*60}")
    print(f"Import complete!")
    print(f"  Imported: {imported_count}")
    print(f"  Skipped (already exists): {skipped_count}")
    print(f"  Errors: {error_count}")
    print(f"{'='*60}")

if __name__ == '__main__':
    # Get user
    try:
        user = User.objects.get(username='takako')
        print(f"Importing data for user: {user.username}")
    except User.DoesNotExist:
        print("Error: User 'takako' not found!")
        sys.exit(1)

    # Import data
    excel_path = '/Users/takako/Documents/anches_reeds_log_Lanthier.xlsx'
    import_data(excel_path, user)
