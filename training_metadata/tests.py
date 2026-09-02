import os
import tempfile
from datetime import timedelta
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from animals_metadata.models import Animal
from .models import BodyWeightEntry, MouseBodyWeight, TrackChanges, TrainingSession
from .services import (
    claim_next_pending_training_session,
    execute_training_analysis,
    process_next_training_analysis,
)


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
        self.assertIn("Initial Entry", create_record.changes)
        self.assertIn("bpod_file_path: '/data/bpod.mat'", create_record.changes)

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

        # Create Tracker
        tracker = MouseBodyWeight.objects.create(animal=self.animal)
        self.assertEqual(
            TrackChanges.objects.filter(
                animal_id="TRN01",
                category=TrackChanges.CategoryChoices.MOUSE_BODY_WEIGHT,
            ).count(),
            1,
        )

        # Day 1: Start weight = 25.0g (100.0%)
        entry1 = BodyWeightEntry.objects.create(
            tracker=tracker,
            date=base_date,
            body_weight_g=25.0,
            notes="Baseline weight",
        )
        self.assertEqual(entry1.percent_body_weight, 100.0)

        # Day 2: Entered weight = 24.0g (96.0%)
        entry2 = BodyWeightEntry.objects.create(
            tracker=tracker,
            date=base_date + timedelta(days=1),
            body_weight_g=24.0,
            notes="Day 2 training",
        )
        self.assertEqual(entry2.percent_body_weight, 96.0)

        # Day 3: Entered weight = 22.5g (90.0%)
        entry3 = BodyWeightEntry.objects.create(
            tracker=tracker,
            date=base_date + timedelta(days=2),
            body_weight_g=22.5,
            notes="Day 3 training",
        )
        self.assertEqual(entry3.percent_body_weight, 90.0)

        # Update entry2 notes and weight
        entry2.notes = "Day 2 notes updated"
        entry2.save()
        self.assertIn(
            "notes",
            TrackChanges.objects.filter(
                animal_id="TRN01",
                category=TrackChanges.CategoryChoices.MOUSE_BODY_WEIGHT,
            ).first().changes,
        )

        # Delete entry3
        entry3.delete()
        delete_track = TrackChanges.objects.filter(
            animal_id="TRN01",
            category=TrackChanges.CategoryChoices.MOUSE_BODY_WEIGHT,
            action="-",
        ).first()
        self.assertIsNotNone(delete_track)


class TrainingAnalysisServiceAndAdminTest(TestCase):
    def setUp(self):
        self.animal = Animal.objects.create(
            animal_id="m67",
            sex="M",
            genotype="Thy1-gcamp6s",
            dob=timezone.now().date(),
        )
        self.user = get_user_model().objects.create_superuser(
            username="admin_test",
            email="admin@example.com",
            password="testpassword123",
        )
        self.client = Client()
        self.client.force_login(self.user)

    def test_status_lifecycle_and_service_execution(self):
        test_mat_path = r"C:\Users\abhrajyoti.chakrabarti\Desktop\64gb_usb_dump\TrainingData\m67_new_VisGo_GoProb_Train_measure_20250926_132921.mat"

        session = TrainingSession.objects.create(
            animal=self.animal,
            training_date=timezone.now().date(),
            bpod_file_path=test_mat_path if os.path.exists(test_mat_path) else "dummy.mat",
            training_unit_range="10:21",
        )
        self.assertEqual(session.status, TrainingSession.StatusChoices.PENDING)

        # Test claiming
        claimed = claim_next_pending_training_session()
        self.assertIsNotNone(claimed)
        self.assertEqual(claimed.pk, session.pk)
        self.assertEqual(claimed.status, TrainingSession.StatusChoices.RUNNING)

        if os.path.exists(test_mat_path):
            with tempfile.TemporaryDirectory() as tmpdir:
                execute_training_analysis(claimed, output_dir=tmpdir)
                claimed.refresh_from_db()
                self.assertEqual(claimed.status, TrainingSession.StatusChoices.COMPLETED)
                self.assertTrue(bool(claimed.output_plot_path))
                self.assertTrue(bool(claimed.output_raster_path))
                self.assertTrue(bool(claimed.output_excel_path))
                self.assertIn("n_trials", claimed.metrics_json)
                self.assertEqual(claimed.metrics_json["n_trials"], 167)

    def test_admin_lick_traces_view(self):
        session = TrainingSession.objects.create(
            animal=self.animal,
            training_date=timezone.now().date(),
            bpod_file_path="/data/test.mat",
            training_unit_range="1:10",
        )
        url = reverse("admin:training_session_lick_traces", args=[session.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Animal {self.animal.animal_id}")
        self.assertContains(response, "Average Licking Trace")
