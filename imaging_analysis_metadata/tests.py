from django.test import TestCase
from django.utils import timezone

from animals_metadata.models import Animal
from imaging_metadata.models import ImagingSession
from .models import AnalysisRun, TrackChanges


class AnalysisRunTrackChangesTest(TestCase):
    def setUp(self):
        self.animal = Animal.objects.create(
            animal_id="ANL01",
            sex="F",
            genotype="Thy1-Cre",
            dob=timezone.now().date(),
        )
        self.session = ImagingSession.objects.create(
            animal=self.animal,
            acquisition_date=timezone.now().date(),
            imaging_region="V1",
            mesc_file_path="/data/file.mesc",
            measurement_unit_ranges="1:10",
        )

    def test_track_changes_lifecycle(self):
        # Create
        run = AnalysisRun.objects.create(
            imaging_session=self.session,
            frame_rate=30.0,
        )
        self.assertEqual(TrackChanges.objects.filter(animal_id="ANL01").count(), 1)
        create_record = TrackChanges.objects.filter(animal_id="ANL01").first()
        self.assertEqual(create_record.action, "+")
        self.assertEqual(create_record.category, TrackChanges.CategoryChoices.ANALYSIS_RUN)
        self.assertEqual(create_record.changes, "Initial Entry")

        # Update
        run.notes = "Updated pipeline notes"
        run.save()
        self.assertEqual(TrackChanges.objects.filter(animal_id="ANL01").count(), 2)
        update_record = TrackChanges.objects.filter(animal_id="ANL01").first()
        self.assertEqual(update_record.action, "~")
        self.assertIn("notes", update_record.changes)

        # Delete
        run.delete()
        self.assertEqual(TrackChanges.objects.filter(animal_id="ANL01").count(), 3)
        delete_record = TrackChanges.objects.filter(animal_id="ANL01").first()
        self.assertEqual(delete_record.action, "-")
        self.assertEqual(delete_record.changes, "Deleted Record")

