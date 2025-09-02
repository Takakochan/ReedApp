from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.
class Reedsdata(models.Model):
    reed_ID = models.CharField(null=True, max_length=220)
    instrument = models.CharField(null=True, max_length=20)
    staple_model = models.CharField(null=True, max_length=20)

    def __str__(self):
        return self.reed_ID

    cane_brand = models.CharField(null=True,
                                  blank=True,
                                  max_length=220,
                                  default=None)
    gouging_machine = models.CharField(null=True, blank=True, max_length=220)
    profile_model = models.CharField(null=True, blank=True, max_length=220)
    #date = models.DateTimeField(auto_now_add=True)
    diamater = models.IntegerField(null=True, blank=True, default=None)
    thickness = models.FloatField(null=True, blank=True, default=None)
    hardness = models.FloatField(null=True, blank=True, default=None)
    flexibility = models.FloatField(null=True, blank=True, default=None)
    density = models.FloatField(null=True, blank=True, default=None)

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
    shaper = models.CharField(null=True,
                              blank=True,
                              max_length=220,
                              default=None)
    harvest_year = models.CharField(null=True,
                                    blank=True,
                                    max_length=220,
                                    default=None)
    temperature = models.FloatField(null=True, blank=True, default=None)
    humidity = models.FloatField(null=True, blank=True, default=None)
    CHOICES = [(i, i) for i in range(11)]
    evaluation = models.IntegerField(choices=CHOICES, blank=True, null=True)
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
    global_quality = models.IntegerField(choices=CHOICES,
                                         blank=True,
                                         null=True,
                                         default=None)

    class Meta:
        unique_together = ['reed_ID', 'reedauthor']

    def get_fields(self):
        return [(field.name, getattr(self, field.name))
                for field in Reedsdata._meta.fields]
