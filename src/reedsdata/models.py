from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator


# Create your models here.
class Reedsdata(models.Model):
    reed_ID = models.CharField(
        null=True, 
        max_length=20,
        validators=[RegexValidator(
            regex=r'^[A-Za-z0-9_-]+$',
            message='Reed ID can only contain letters, numbers, hyphens, and underscores'
        )]
    )
    instrument = models.CharField(null=True, max_length=20)
    staple_model = models.CharField(null=True, max_length=20)

    def __str__(self):
        return self.reed_ID

    CANE_BRAND_CHOICES = [
        ('', ''),
        ('Medir', 'Medir'),
        ('Rigotti', 'Rigotti'),
        ('Ghys', 'Ghys'),
        ('Glotin', 'Glotin'),
        ('Pisoni', 'Pisoni'),
        ('Reeds \'n Stuff', 'Reeds \'n Stuff'),
        ('Danzi', 'Danzi'),
        ('Arundo Donax', 'Arundo Donax'),
        ('Marca', 'Marca'),
        ('Gonzalez', 'Gonzalez'),
        ('Silvacane', 'Silvacane'),
        ('Emerald', 'Emerald'),
        ('Baron', 'Baron'),
        ('Milliet', 'Milliet'),
        ('Vandoren', 'Vandoren'),
        ('Jones', 'Jones'),
        ('Gilbert', 'Gilbert'),
        ('Marigaux', 'Marigaux'),
        ('Loree', 'Loree'),
        ('Fox', 'Fox'),
        ('Hiniker', 'Hiniker'),
        ('Bonazza', 'Bonazza'),
        ('Chartier', 'Chartier'),
        ('Other', 'Other'),
    ]
    
    cane_brand = models.CharField(choices=CANE_BRAND_CHOICES,
                                  null=False,
                                  blank=False,
                                  max_length=20)
    
    GOUGING_MACHINE_CHOICES = [
        ('', ''),
        ('Reeds \'n Stuff', 'Reeds \'n Stuff'),
        ('Graf', 'Graf'),
        ('Ross', 'Ross'),
        ('Rieger', 'Rieger'),
        ('Innoledy', 'Innoledy'),
        ('Weber', 'Weber'),
        ('Kunibert Michel', 'Kunibert Michel'),
        ('Prestini', 'Prestini'),
        ('Other', 'Other'),
    ]
    
    gouging_machine = models.CharField(choices=GOUGING_MACHINE_CHOICES,
                                      null=True, blank=True, max_length=20)
    bed_diameter = models.FloatField(null=True, blank=True, help_text="in mm")
    blade_diameter = models.FloatField(null=True, blank=True, help_text="in mm")
    
    PROFILE_MODEL_CHOICES = [
        ('', ''),
        ('Reeds \'n Stuff -1', 'Reeds \'n Stuff -1'),
        ('Reeds \'n Stuff -1N', 'Reeds \'n Stuff -1N'),
        ('Reeds \'n Stuff -2', 'Reeds \'n Stuff -2'),
        ('Reeds \'n Stuff -2N', 'Reeds \'n Stuff -2N'),
        ('Philadelphia', 'Philadelphia'),
        ('Mack', 'Mack'),
        ('Rieger 1A', 'Rieger 1A'),
        ('Rieger 2A', 'Rieger 2A'),
        ('Stevens', 'Stevens'),
        ('Klopfer', 'Klopfer'),
        ('Jeanne', 'Jeanne'),
        ('Other', 'Other'),
    ]
    
    profile_model = models.CharField(choices=PROFILE_MODEL_CHOICES,
                                    null=True, blank=True, max_length=20)
    #date = models.DateTimeField(auto_now_add=True)
    diameter = models.IntegerField(null=True, blank=True, default=None)
    thickness = models.FloatField(
        null=True, blank=True, default=None,
        validators=[MinValueValidator(0), MaxValueValidator(200)]
    )
    hardness = models.FloatField(
        null=True, blank=True, default=None,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    flexibility = models.FloatField(
        null=True, blank=True, default=None,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    density = models.FloatField(
        null=True, blank=True, default=None,
        validators=[MinValueValidator(0), MaxValueValidator(2.0)]
    )

    # for density auto calculation
    m1 = models.FloatField(null=True, blank=True)
    m2 = models.FloatField(null=True, blank=True)

    @property
    def density_auto(self):
        if self.m1 is not None and self.m2:
            try:
                return round(self.m1 / (self.m1 + self.m2), 4)
            except ZeroDivisionError:
                return None
        return None

    reedauthor = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    SHAPER_CHOICES = [
        ('', ''),
        ('Mack', 'Mack'),
        ('Philadelphia', 'Philadelphia'),
        ('Stevens', 'Stevens'),
        ('Pfeiffer', 'Pfeiffer'),
        ('Klopfer', 'Klopfer'),
        ('Jeanne', 'Jeanne'),
        ('Rieger', 'Rieger'),
        ('Reeds \'n Stuff', 'Reeds \'n Stuff'),
        ('Gilbert', 'Gilbert'),
        ('Prestini', 'Prestini'),
        ('Other', 'Other'),
    ]
    
    shaper = models.CharField(choices=SHAPER_CHOICES,
                              null=True,
                              blank=True,
                              max_length=20,
                              default=None)
    shaper_model = models.CharField(null=True,
                                   blank=True,
                                   max_length=20,
                                   default=None,
                                   help_text="Specific model or shape number")
    harvest_year = models.CharField(null=True,
                                    blank=True,
                                    max_length=20,
                                    default=None)
    chamber_temperature = models.FloatField(null=True, blank=True, default=None, help_text="Chamber temperature in Celsius")
    chamber_humidity = models.FloatField(null=True, blank=True, default=None, help_text="Chamber humidity percentage")
    CHOICES = [(i, i) for i in range(11)]
    stiffness = models.IntegerField(choices=CHOICES,
                                    blank=True,
                                    null=True,
                                    default=None)
    playing_ease = models.IntegerField(choices=CHOICES,
                                       blank=True,
                                       null=True,
                                       default=None)
    intonation = models.IntegerField(choices=CHOICES,
                                     blank=True,
                                     null=True,
                                     default=None)
    tone_color = models.IntegerField(choices=CHOICES,
                                     blank=True,
                                     null=True,
                                     default=None)
    response = models.IntegerField(choices=CHOICES,
                                   blank=True,
                                   null=True,
                                   default=None)
    counts_rehearsal = models.IntegerField(blank=True,
                                          null=True,
                                          default=None)
    counts_concert = models.IntegerField(blank=True,
                                        null=True,
                                        default=None)
    global_quality_first_impression = models.IntegerField(choices=CHOICES,
                                                          blank=True,
                                                          null=True,
                                                          default=None)
    global_quality_first_impression_date = models.DateTimeField(null=True, blank=True)
    global_quality_second_impression = models.IntegerField(choices=CHOICES,
                                                           blank=True,
                                                           null=True,
                                                           default=None)
    global_quality_second_impression_date = models.DateTimeField(null=True, blank=True)
    global_quality_third_impression = models.IntegerField(choices=CHOICES,
                                                          blank=True,
                                                          null=True,
                                                          default=None)
    global_quality_third_impression_date = models.DateTimeField(null=True, blank=True)
    
    # Weather snapshots for each Global Quality impression
    # First impression weather
    global_quality_first_weather_location = models.CharField(max_length=100, null=True, blank=True, help_text="Location when 1st impression was recorded")
    global_quality_first_weather_temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="Temperature when 1st impression recorded (°C)")
    global_quality_first_weather_humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Humidity when 1st impression recorded (%)")
    global_quality_first_weather_pressure = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Air pressure when 1st impression recorded (hPa)")
    global_quality_first_weather_altitude = models.IntegerField(null=True, blank=True, help_text="Altitude when 1st impression recorded (meters)")
    global_quality_first_weather_description = models.CharField(max_length=50, null=True, blank=True, help_text="Weather when 1st impression recorded")
    
    # Second impression weather
    global_quality_second_weather_location = models.CharField(max_length=100, null=True, blank=True, help_text="Location when 2nd impression was recorded")
    global_quality_second_weather_temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="Temperature when 2nd impression recorded (°C)")
    global_quality_second_weather_humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Humidity when 2nd impression recorded (%)")
    global_quality_second_weather_pressure = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Air pressure when 2nd impression recorded (hPa)")
    global_quality_second_weather_altitude = models.IntegerField(null=True, blank=True, help_text="Altitude when 2nd impression recorded (meters)")
    global_quality_second_weather_description = models.CharField(max_length=50, null=True, blank=True, help_text="Weather when 2nd impression recorded")
    
    # Third impression weather
    global_quality_third_weather_location = models.CharField(max_length=100, null=True, blank=True, help_text="Location when 3rd impression was recorded")
    global_quality_third_weather_temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="Temperature when 3rd impression recorded (°C)")
    global_quality_third_weather_humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Humidity when 3rd impression recorded (%)")
    global_quality_third_weather_pressure = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Air pressure when 3rd impression recorded (hPa)")
    global_quality_third_weather_altitude = models.IntegerField(null=True, blank=True, help_text="Altitude when 3rd impression recorded (meters)")
    global_quality_third_weather_description = models.CharField(max_length=50, null=True, blank=True, help_text="Weather when 3rd impression recorded")
    
    # Location and Weather Data
    location = models.CharField(max_length=100, null=True, blank=True, help_text="City or venue name")
    
    # Weather conditions when reed was made/tested
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="Temperature in Celsius")
    humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Humidity percentage")
    air_pressure = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Air pressure in hPa")
    weather_description = models.CharField(max_length=50, null=True, blank=True, help_text="e.g., 'Clear sky', 'Light rain'")
    
    note = models.CharField(max_length=45, null=True, blank=True, help_text="Additional notes")

    @property
    def latest_global_quality(self):
        """Returns the most recent global quality value (3rd > 2nd > 1st)"""
        if self.global_quality_third_impression is not None:
            return self.global_quality_third_impression
        elif self.global_quality_second_impression is not None:
            return self.global_quality_second_impression
        elif self.global_quality_first_impression is not None:
            return self.global_quality_first_impression
        return None

    class Meta:
        unique_together = ['reed_ID', 'reedauthor']

    def get_fields(self):
        return [(field.name, getattr(self, field.name))
                for field in Reedsdata._meta.fields]


# =====================
# New model for parameters
# =====================
class Parameter(models.Model):
    name = models.CharField(max_length=50,
                            unique=True)  # 内部的な名前 (e.g. "density_auto")
    display_name = models.CharField(
        max_length=100)  # UI に表示する名前 (e.g. "Density (auto)")

    def __str__(self):
        return self.display_name


class UserParameter(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reedsdata_userparameters"  # ← これを追加
    )
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)


class Cane(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reed_ID = models.CharField(max_length=20)
    instrument = models.CharField(max_length=20)
    staple_model = models.CharField(max_length=20, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)


class CaneMeasurement(models.Model):
    cane = models.ForeignKey(Cane, on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE)
    value_float = models.FloatField(null=True, blank=True)
    value_text = models.CharField(max_length=20, null=True, blank=True)
    step = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)  # ユーザーが決める順番

    class Meta:
        unique_together = ('cane', 'parameter')
        ordering = ['order']
