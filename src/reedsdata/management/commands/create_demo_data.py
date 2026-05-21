import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from reedsdata.models import Reedsdata, Parameter, UserParameter


CANE_BRANDS = ['Medir', 'Rigotti', 'Ghys', 'Glotin', 'Pisoni']
GOUGING_MACHINES = ['Reeds \'n Stuff', 'Graf', 'Ross', 'Rieger']
SHAPERS = ['Mack', 'Philadelphia', 'Stevens', 'Pfeiffer', 'Rieger']
LOCATIONS = ['Vienna', 'Berlin', 'Tokyo', 'New York', 'Paris', 'London']
WEATHER_DESCS = ['Clear sky', 'Partly cloudy', 'Light rain', 'Overcast', 'Sunny']
STAPLE_MODELS = ['Chiarugi', 'Reeds n Stuff', 'Pisoni', 'Loree', 'RDG']

# Realistic score distributions per brand (mean, std)
BRAND_QUALITY = {
    'Medir':   {'playing_ease': (7.5, 1.2), 'intonation': (7.8, 1.0), 'tone_color': (8.0, 1.1), 'response': (7.6, 1.3)},
    'Rigotti': {'playing_ease': (7.0, 1.5), 'intonation': (7.2, 1.3), 'tone_color': (7.5, 1.4), 'response': (7.0, 1.5)},
    'Ghys':    {'playing_ease': (8.0, 1.0), 'intonation': (8.2, 0.9), 'tone_color': (8.3, 1.0), 'response': (8.1, 1.1)},
    'Glotin':  {'playing_ease': (6.5, 1.8), 'intonation': (6.8, 1.6), 'tone_color': (7.0, 1.5), 'response': (6.7, 1.7)},
    'Pisoni':  {'playing_ease': (7.8, 1.1), 'intonation': (7.5, 1.2), 'tone_color': (7.9, 1.0), 'response': (7.7, 1.2)},
}


def clamp(val, lo, hi):
    return max(lo, min(hi, int(round(val))))


def make_score(mean, std):
    return clamp(random.gauss(mean, std), 0, 10)


class Command(BaseCommand):
    help = 'Create a demo user and realistic reed data for screenshots'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='demo')
        parser.add_argument('--password', default='demopass123')
        parser.add_argument('--email', default='demo@reedmanage.app')
        parser.add_argument('--count', type=int, default=60)
        parser.add_argument('--clear', action='store_true', help='Delete existing demo reeds first')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        count = options['count']

        # Create or get demo user
        user, created = User.objects.get_or_create(username=username, defaults={'email': email})
        if created or options.get('reset_password'):
            user.set_password(password)
            user.save()
            self.stdout.write(f'Created user: {username} / {password}')
        else:
            self.stdout.write(f'Using existing user: {username}')

        if options['clear']:
            deleted, _ = Reedsdata.objects.filter(reedauthor=user).delete()
            self.stdout.write(f'Deleted {deleted} existing reeds')

        # Set up UserParameters
        param_names = [
            'cane_brand', 'gouging_machine', 'shaper', 'thickness', 'hardness',
            'flexibility', 'density_auto', 'stiffness', 'playing_ease', 'intonation',
            'tone_color', 'response', 'global_quality_first_impression',
            'global_quality_second_impression', 'counts_rehearsal', 'counts_concert', 'note',
        ]
        for i, name in enumerate(param_names):
            param, _ = Parameter.objects.get_or_create(name=name, defaults={'display_name': name.replace('_', ' ').title()})
            UserParameter.objects.get_or_create(user=user, parameter=param, defaults={'active': True, 'order': i})

        now = timezone.now()
        saved = 0

        # 60 reeds spread over 8 months, mostly oboe
        instruments = (['oboe'] * 45) + (['english_horn'] * 10) + (['bassoon'] * 5)
        random.shuffle(instruments)

        for i in range(count):
            instrument = instruments[i % len(instruments)]
            period = random.choice(['modern', 'modern', 'modern', 'baroque', 'classical'])
            brand = random.choice(CANE_BRANDS)

            # Prefix: period + instrument initials
            period_prefix = {'modern': 'M', 'classical': 'C', 'baroque': 'B'}[period]
            instr_prefix = {'oboe': 'O', 'english_horn': 'E', 'bassoon': 'B',
                            'oboe_damore': 'A', 'contrabassoon': 'C'}[instrument]
            reed_id = f'{period_prefix}{instr_prefix}{i+1:03d}'

            # Skip if already exists
            if Reedsdata.objects.filter(reed_ID=reed_id, reedauthor=user).exists():
                continue

            days_ago = random.randint(0, 240)
            reed_date = now - timedelta(days=days_ago)

            # Physical measurements — realistic oboe reed values
            m1 = round(random.uniform(0.18, 0.28), 3)
            m2 = round(random.uniform(0.08, 0.16), 3)
            thickness = round(random.uniform(55, 75), 1)
            hardness = round(random.uniform(40, 70), 1)
            flexibility = round(random.uniform(30, 60), 1)

            # Quality scores — biased by brand
            bq = BRAND_QUALITY.get(brand, BRAND_QUALITY['Medir'])
            stiffness = make_score(5.5, 1.5)
            playing_ease = make_score(*bq['playing_ease'])
            intonation = make_score(*bq['intonation'])
            tone_color = make_score(*bq['tone_color'])
            response = make_score(*bq['response'])

            gq1 = make_score((playing_ease + intonation + tone_color + response) / 4, 0.8)
            gq2 = make_score(gq1 + random.uniform(-1, 1.5), 0.6) if random.random() > 0.3 else None
            gq3 = make_score(gq2 + random.uniform(-0.5, 1.0), 0.5) if gq2 and random.random() > 0.5 else None

            location = random.choice(LOCATIONS)
            temp = round(random.uniform(18, 28), 1)
            humidity = round(random.uniform(40, 75), 1)
            pressure = round(random.uniform(1000, 1025), 1)

            reed = Reedsdata(
                reed_ID=reed_id,
                reedauthor=user,
                instrument=instrument,
                period=period,
                cane_brand=brand,
                gouging_machine=random.choice(GOUGING_MACHINES),
                shaper=random.choice(SHAPERS),
                staple_model=random.choice(STAPLE_MODELS),
                date=reed_date,
                m1=m1,
                m2=m2,
                thickness=thickness,
                hardness=hardness,
                flexibility=flexibility,
                stiffness=stiffness,
                playing_ease=playing_ease,
                intonation=intonation,
                tone_color=tone_color,
                response=response,
                global_quality_first_impression=gq1,
                global_quality_first_impression_date=reed_date + timedelta(days=1),
                global_quality_second_impression=gq2,
                global_quality_second_impression_date=reed_date + timedelta(days=7) if gq2 else None,
                global_quality_third_impression=gq3,
                global_quality_third_impression_date=reed_date + timedelta(days=21) if gq3 else None,
                counts_rehearsal=random.randint(0, 15),
                counts_concert=random.randint(0, 5),
                location=location,
                temperature=temp,
                humidity=humidity,
                air_pressure=pressure,
                weather_description=random.choice(WEATHER_DESCS),
                chamber_temperature=round(temp + random.uniform(-3, 3), 1),
                chamber_humidity=round(humidity + random.uniform(-5, 5), 1),
                note=random.choice(['Good start', 'Needs scraping', 'Concert ready', 'Too soft', '', '', '']),
            )
            reed.save()
            saved += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done! Created {saved} reeds for "{username}".\n'
            f'Login: {username} / {password}'
        ))
