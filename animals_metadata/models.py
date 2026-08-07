from django.db import models
from django.utils import timezone


class Animal(models.Model):
    
    class SexChoices(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE  = 'F', 'Female' 
    
    class GenotypeChoices(models.TextChoices):
        TC = 'Thy1-Cre', 'Thy1-Cre'
        TG = 'Thy1-gcamp6s', 'Thy1/gcamp6s (Tg)'
        
    animal_id = models.CharField(max_length=10,unique=True)
    genotype = models.CharField(max_length=100,choices=GenotypeChoices.choices)
    sex = models.CharField(max_length=100,choices=SexChoices.choices)
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
            f"{self.animal_id} - {self.genotype} - {self.sex} - {self.dob} "
            f"- Age: {self.age_in_days} days"
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
    

    class Meta:
        verbose_name = "Vision Check"
        verbose_name_plural = "Vision Check"

    def __str__(self):
        a = self.animal_id
        return f"{a.animal_id} - {a.genotype} - {a.sex}"