from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from reedsdata.models import Parameter, UserParameter

User = get_user_model()


class Command(BaseCommand):
    help = 'Initialize Parameter and UserParameter data for all users'

    def handle(self, *args, **options):
        # Define all parameters with their display names
        parameters_data = [
            ('reed_ID', 'Reed ID'),
            ('instrument', 'Instrument'),
            ('staple_model', 'Staple Model'),
            ('cane_brand', 'Cane Brand'),
            ('gouging_machine', 'Gouging Machine'),
            ('bed_diameter', 'Bed Diameter'),
            ('blade_diameter', 'Blade Diameter'),
            ('profile_model', 'Profile Model'),
            ('diameter', 'Diameter'),
            ('thickness', 'Thickness'),
            ('hardness', 'Hardness'),
            ('flexibility', 'Flexibility'),
            ('density', 'Density'),
            ('density_auto', 'Density (auto)'),
            ('density_auto_display', 'Density'),
            ('m1', 'M1'),
            ('m2', 'M2'),
            ('date', 'Date'),
            ('shaper', 'Shaper'),
            ('shaper_model', 'Shaper Model'),
            ('harvest_year', 'Harvest Year'),
            ('chamber_temperature', 'Chamber Temperature'),
            ('chamber_humidity', 'Chamber Humidity'),
            ('stiffness', 'Stiffness'),
            ('playing_ease', 'Playing Ease'),
            ('intonation', 'Intonation'),
            ('tone_color', 'Tone Color'),
            ('response', 'Response'),
            ('counts_rehearsal', 'Rehearsal Count'),
            ('counts_concert', 'Concert Count'),
            ('global_quality_first_impression', 'First Impression'),
            ('global_quality_first_impression_date', 'First Impression Date'),
            ('global_quality_second_impression', 'Second Impression'),
            ('global_quality_second_impression_date', 'Second Impression Date'),
            ('global_quality_third_impression', 'Third Impression'),
            ('global_quality_third_impression_date', 'Third Impression Date'),
            ('location', 'Location'),
            ('temperature', 'Temperature'),
            ('humidity', 'Humidity'),
            ('air_pressure', 'Air Pressure'),
            ('weather_description', 'Weather'),
            ('note', 'Notes'),
        ]

        # Create Parameters
        self.stdout.write('Creating Parameters...')
        created_params = 0
        for name, display_name in parameters_data:
            param, created = Parameter.objects.get_or_create(
                name=name,
                defaults={'display_name': display_name}
            )
            if created:
                created_params += 1
                self.stdout.write(f'  Created: {display_name}')

        self.stdout.write(self.style.SUCCESS(f'Parameters: {created_params} created, {Parameter.objects.count()} total'))

        # Create UserParameters for all users
        users = User.objects.all()
        self.stdout.write(f'\nCreating UserParameters for {users.count()} user(s)...')

        # Default order for parameters
        default_order = [
            'reed_ID', 'instrument', 'cane_brand', 'diameter', 'gouging_machine',
            'bed_diameter', 'blade_diameter', 'shaper', 'shaper_model',
            'thickness', 'hardness', 'flexibility', 'density_auto_display', 'm1', 'm2',
            'date', 'playing_ease', 'intonation', 'tone_color', 'response',
            'counts_rehearsal', 'counts_concert',
            'global_quality_first_impression', 'global_quality_second_impression',
            'global_quality_third_impression', 'note'
        ]

        # Default active fields (commonly used ones)
        # Note: M1 and M2 are not included as they're only for Density Auto calculation
        default_active = [
            'reed_ID', 'instrument', 'cane_brand', 'gouging_machine',
            'diameter', 'bed_diameter', 'blade_diameter', 'shaper',
            'shaper_model', 'hardness', 'density_auto', 'date'
        ]

        for user in users:
            created_user_params = 0

            # Get all parameters
            all_params = Parameter.objects.all()

            for idx, param in enumerate(all_params):
                # Determine order based on default_order list
                if param.name in default_order:
                    order = default_order.index(param.name)
                else:
                    order = 1000 + idx  # Put unlisted params at the end

                # Determine if active by default
                active = param.name in default_active

                user_param, created = UserParameter.objects.get_or_create(
                    user=user,
                    parameter=param,
                    defaults={
                        'active': active,
                        'order': order
                    }
                )

                if created:
                    created_user_params += 1

            self.stdout.write(f'  User {user.username}: {created_user_params} UserParameters created')

        self.stdout.write(self.style.SUCCESS('\n=== Initialization Complete ==='))
        self.stdout.write(self.style.SUCCESS(f'Total Parameters: {Parameter.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total UserParameters: {UserParameter.objects.count()}'))
