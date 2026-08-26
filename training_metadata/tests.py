from django.test import TestCase
from django.utils import timezone

from animals_metadata.models import Animal
from .models import TrackChanges, TrainingSession


class TrainingSessionTrackChangesTest(TestCase):
    def setUp(self):
        self.animal = Animal.objects.create(
            animal_id="TRN01",
            sex="M",
            genotype="Thy1-gcamp6s",
            dob=timezone.now().date(),
        )

    def test_track_changes_lifecycle(self):
        # Create
        session = TrainingSession.objects.create(
            animal=self.animal,
            training_date=timezone.now().date(),
            bpod_file_path="/data/bpod.mat",
            training_unit_range="1:10",
        )
        self.assertEqual(TrackChanges.objects.filter(animal_id="TRN01").count(), 1)
        create_record = TrackChanges.objects.filter(animal_id="TRN01").first()
        self.assertEqual(create_record.action, "+")
        self.assertEqual(create_record.category, TrackChanges.CategoryChoices.TRAINING_SESSION)
        self.assertEqual(create_record.changes, "Initial Entry")

        # Update
        session.notes = "Updated training notes"
        session.save()
        self.assertEqual(TrackChanges.objects.filter(animal_id="TRN01").count(), 2)
        update_record = TrackChanges.objects.filter(animal_id="TRN01").first()
        self.assertEqual(update_record.action, "~")
        self.assertIn("notes", update_record.changes)

        # Delete
        session.delete()
        self.assertEqual(TrackChanges.objects.filter(animal_id="TRN01").count(), 3)
        delete_record = TrackChanges.objects.filter(animal_id="TRN01").first()
        self.assertEqual(delete_record.action, "-")
        self.assertEqual(delete_record.changes, "Deleted Record")

