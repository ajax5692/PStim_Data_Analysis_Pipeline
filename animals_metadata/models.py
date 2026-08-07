from django.db import models
from django.utils import timezone


class Animal(models.Model):
    
    class SexChoices(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE  = 'F', 'Female'
        
    class OwnerChoices(models.TextChoices):
        AC = 'AC', 'Abhrajyoti'
        TB  = 'TB', 'Balázs'
    
    class GenotypeChoices(models.TextChoices):
        TC = 'Thy1-Cre', 'Thy1-Cre'
        TG = 'Thy1-gcamp6s', 'Thy1/gcamp6s (Tg)'
        
    animal_id = models.CharField(max_length=10,unique=True)
    owner = models.CharField(max_length=100,choices=OwnerChoices.choices, null=True, blank=True)
    sex = models.CharField(max_length=100,choices=SexChoices.choices)
    genotype = models.CharField(max_length=100,choices=GenotypeChoices.choices)
    cage_id = models.CharField(max_length=100)
    
    dob = models.DateField(verbose_name="Date of Birth")
    @property
    def age_in_days(self):
        if not self.dob:
            return "N/A"
        today = timezone.now().date()
        return (today - self.dob).days
    

    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animals"

    def __str__(self):
        return (
            f"{self.animal_id} - {self.owner} - {self.genotype} - {self.sex}"
            f" - {self.dob} - Age: {self.age_in_days} days"
        )
    
class VisionCheck(models.Model):

    class PassFailChoices(models.TextChoices):
        PASS = 'P', 'Pass'
        FAIL  = 'F', 'Fail' 

    class TestChoices(models.TextChoices):
        SWEEP = 'SweepTest', 'Vision Sweep Test'
        QOMR = 'qOMR', 'qOMR'
        
    animal_id = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE
    )
    
    vision_test_type = models.CharField(max_length=10,choices=TestChoices.choices)
    vision_test_result = models.CharField(max_length=10,choices=PassFailChoices.choices)
    data_path = models.CharField(blank=True, null=True)

    class Meta:
        verbose_name = "Vision Check"
        verbose_name_plural = "Vision Check"

    def __str__(self):
        a = self.animal_id
        return f"{a.animal_id} - {a.owner} - {a.genotype} - {a.sex}"
    
class ViralInjection(models.Model):
    
    animal_id = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE
    )
    
    class VirusChoices(models.TextChoices):
        AAV322 = 'AAV322', 'AAV322'
        AAV418  = 'AAV418', 'AAV418'
        
    class VirusConstructChoices(models.TextChoices):
        VIRUS_1 = 'AAV9-hSyn-DIO-jGCaMP8s-P2A-ChrimsonR-ST', 'AAV9-hSyn-DIO-jGCaMP8s-P2A-ChrimsonR-ST'
    
    class InjectionSiteChoices(models.TextChoices):
        V1 = 'V1', 'V1'
    
    virus_name = models.CharField(max_length=100,choices=VirusChoices.choices)
    virus_construct = models.CharField(max_length=100,choices=VirusConstructChoices.choices)
    injection_date = models.DateField()
    injection_site = models.CharField(max_length=100,choices=InjectionSiteChoices.choices)
    volume_ul = models.FloatField(verbose_name="Volume (nL)")
    notes = models.TextField(blank=True, null=True)
    expression_pattern = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Viral Injections"
        verbose_name_plural = "Viral Injections"
        
    def __str__(self):
        a = self.animal_id
        return (
            f"{a.animal_id} - ({a.owner}) - {self.virus_name} - {self.virus_construct}"
            f"{self.injection_date} - ({self.injection_site}) - {self.volume_ul} - {self.notes}"
        )