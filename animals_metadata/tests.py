from django.test import TestCase
from django.utils import timezone

from virus_metadata.models import Virus
from .models import Animal, TrackChanges, ViralInjection, VisionCheck


class AnimalsMetadataTrackChangesTest(TestCase):
    def setUp(self):
        self.virus1 = Virus.objects.create(
            virus_id="AAV322",
            viral_construct="AAV9-hSyn-DIO-jGCaMP8s",
            titre="1.5x10^13",
            location_in_fridge="Box 1",
            virus_owner="AC",
        )
        self.virus2 = Virus.objects.create(
            virus_id="AAV418",
            viral_construct="AAV9-hSyn-DIO-ChrimsonR",
            titre="2.0x10^13",
            location_in_fridge="Box 2",
            virus_owner="TB",
        )
        self.animal = Animal.objects.create(
            animal_id="ANM01",
            sex="M",
            genotype="Thy1-Cre",
            dob=timezone.now().date(),
        )

    def test_viral_injection_with_virus_foreign_key(self):
        # Create ViralInjection
        inj = ViralInjection.objects.create(
            animal_id=self.animal,
            virus_id=self.virus1,
            volume_ul=100.0,
            site="V1",
            depth=300.0,
            virus_id_2=self.virus2,
            volume_nl_2=50.0,
            site_2="V1",
            depth_2=350.0,
            injection_date=timezone.now().date(),
        )
        self.assertEqual(inj.virus_id.virus_id, "AAV322")
        self.assertEqual(inj.virus_id_2.virus_id, "AAV418")
        self.assertEqual(TrackChanges.objects.filter(animal_id="ANM01", category=TrackChanges.CategoryChoices.VIRAL_INJECTION).count(), 1)

        # Update
        inj.depth = 320.0
        inj.save()
        self.assertEqual(TrackChanges.objects.filter(animal_id="ANM01", category=TrackChanges.CategoryChoices.VIRAL_INJECTION).count(), 2)

        # Delete
        inj.delete()
        self.assertEqual(TrackChanges.objects.filter(animal_id="ANM01", category=TrackChanges.CategoryChoices.VIRAL_INJECTION).count(), 3)

