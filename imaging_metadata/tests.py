from django.test import TestCase
from django.utils import timezone

from animals_metadata.models import Animal
from .models import ImagingSession, TrackChanges


class ImagingSessionTrackChangesTest(TestCase):
    def setUp(self):
        self.animal = Animal.objects.create(
            animal_id="IMG01",
            sex="M",
            genotype="Thy1-Cre",
            dob=timezone.now().date(),
        )

    def test_track_changes_lifecycle(self):
        # Create
        session = ImagingSession.objects.create(
            animal=self.animal,
            acquisition_date=timezone.now().date(),
            imaging_region="V1",
            mesc_file_path="/data/file.mesc",
            measurement_unit_ranges="1:10",
        )
        self.assertEqual(TrackChanges.objects.filter(animal_id="IMG01").count(), 1)
        create_record = TrackChanges.objects.filter(animal_id="IMG01").first()
        self.assertEqual(create_record.action, "+")
        self.assertEqual(create_record.category, TrackChanges.CategoryChoices.IMAGING_SESSION)
        self.assertEqual(create_record.changes, "Initial Entry")

        # Update
        session.imaging_region = "V2"
        session.save()
        self.assertEqual(TrackChanges.objects.filter(animal_id="IMG01").count(), 2)
        update_record = TrackChanges.objects.filter(animal_id="IMG01").first()
        self.assertEqual(update_record.action, "~")
        self.assertIn("imaging_region", update_record.changes)

        # Delete
        session.delete()
        self.assertEqual(TrackChanges.objects.filter(animal_id="IMG01").count(), 3)
        delete_record = TrackChanges.objects.filter(animal_id="IMG01").first()
        self.assertEqual(delete_record.action, "-")
        self.assertEqual(delete_record.changes, "Deleted Record")

