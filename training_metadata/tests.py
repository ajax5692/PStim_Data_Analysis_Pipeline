from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from animals_metadata.models import Animal
from .models import MouseBodyWeightRecord, TrackChanges, TrainingSession


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

    def test_mouse_body_weight_lifecycle_and_auto_calculation(self):
        base_date = timezone.now().date()

        # Day 1: Start weight = 25.0g (100.0%)
        rec1 = MouseBodyWeightRecord.objects.create(
            animal=self.animal,
            date=base_date,
            body_weight_g=25.0,
            notes="Baseline weight",
        )
        self.assertEqual(rec1.percent_body_weight, 100.0)
        self.assertEqual(
            TrackChanges.objects.filter(
                animal_id="TRN01",
                category=TrackChanges.CategoryChoices.MOUSE_BODY_WEIGHT,
            ).count(),
            1,
        )

        # Day 2: Entered weight = 24.0g (96.0%)
        rec2 = MouseBodyWeightRecord.objects.create(
            animal=self.animal,
            date=base_date + timedelta(days=1),
            body_weight_g=24.0,
            notes="Day 2 training",
        )
        self.assertEqual(rec2.percent_body_weight, 96.0)

        # Day 3: Entered weight = 22.5g (90.0%)
        rec3 = MouseBodyWeightRecord.objects.create(
            animal=self.animal,
            date=base_date + timedelta(days=2),
            body_weight_g=22.5,
            notes="Day 3 training",
        )
        self.assertEqual(rec3.percent_body_weight, 90.0)

        # Update rec2 notes and weight
        rec2.notes = "Day 2 notes updated"
        rec2.save()
        self.assertIn(
            "notes",
            TrackChanges.objects.filter(
                animal_id="TRN01",
                category=TrackChanges.CategoryChoices.MOUSE_BODY_WEIGHT,
            ).first().changes,
        )

        # Delete rec3
        rec3.delete()
        delete_track = TrackChanges.objects.filter(
            animal_id="TRN01",
            category=TrackChanges.CategoryChoices.MOUSE_BODY_WEIGHT,
            action="-",
        ).first()
        self.assertIsNotNone(delete_track)


