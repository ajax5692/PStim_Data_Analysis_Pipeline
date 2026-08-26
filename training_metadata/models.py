from django.db import models
from simple_history.models import HistoricalRecords


class TrainingSession(models.Model):
    animal = models.ForeignKey(
        "animals_metadata.Animal",
        on_delete=models.PROTECT,
        related_name="training_sessions",
    )

    training_date = models.DateField()

    bpod_file_path = models.CharField(
        max_length=500,
        help_text="Path to the source .mesc file.",
    )

    training_unit_range = models.CharField(
        max_length=200,
        help_text="Example: 10:21,25:55",
    )

    notes = models.TextField(
        blank=True,
        null=True,
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Training Session"
        verbose_name_plural = "Training Sessions"
        ordering = ["-training_date"]

    def __str__(self):
        return f"{self.animal.animal_id} - {self.training_date}"


class MouseBodyWeightRecord(models.Model):
    animal = models.ForeignKey(
        "animals_metadata.Animal",
        on_delete=models.PROTECT,
        related_name="body_weight_records",
        verbose_name="Mouse ID",
    )

    date = models.DateField(
        verbose_name="Date",
    )

    body_weight_g = models.FloatField(
        verbose_name="Body Weight in Grams",
    )

    percent_body_weight = models.FloatField(
        blank=True,
        null=True,
        verbose_name="% Body Weight Compared to Start",
    )

    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes",
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Mouse Body Weight Record"
        verbose_name_plural = "Mice Body Weight Records"
        ordering = ["-date", "animal"]

    def __str__(self):
        return f"{self.animal.animal_id} - {self.date} ({self.body_weight_g}g)"

    def calculate_percent_body_weight(self):
        if not self.animal_id or self.body_weight_g is None:
            return None
        first_record = (
            MouseBodyWeightRecord.objects.filter(animal=self.animal)
            .order_by("date", "id")
            .first()
        )
        if first_record and first_record.pk != self.pk:
            if self.date < first_record.date:
                start_wt = self.body_weight_g
            else:
                start_wt = first_record.body_weight_g
        else:
            start_wt = self.body_weight_g

        if start_wt and start_wt > 0:
            return round((self.body_weight_g / start_wt) * 100.0, 2)
        return 100.0

    @classmethod
    def recalculate_for_animal(cls, animal):
        if not animal:
            return
        records = list(cls.objects.filter(animal=animal).order_by("date", "id"))
        if not records:
            return
        start_wt = records[0].body_weight_g
        to_update = []
        for rec in records:
            if start_wt and start_wt > 0 and rec.body_weight_g is not None:
                new_pct = round((rec.body_weight_g / start_wt) * 100.0, 2)
            else:
                new_pct = 100.0
            if rec.percent_body_weight != new_pct:
                rec.percent_body_weight = new_pct
                to_update.append(rec)
        if to_update:
            cls.objects.bulk_update(to_update, ["percent_body_weight"])

    def save(self, *args, **kwargs):
        self.percent_body_weight = self.calculate_percent_body_weight()
        super().save(*args, **kwargs)
        MouseBodyWeightRecord.recalculate_for_animal(self.animal)

    def delete(self, *args, **kwargs):
        animal = self.animal
        super().delete(*args, **kwargs)
        MouseBodyWeightRecord.recalculate_for_animal(animal)


class TrackChanges(models.Model):

    class CategoryChoices(models.TextChoices):
        TRAINING_SESSION = "training_session", "Training Session"
        MOUSE_BODY_WEIGHT = "mouse_body_weight", "Mouse Body Weight Record"

    class ActionChoices(models.TextChoices):
        CREATED = "+", "Created"
        UPDATED = "~", "Updated"
        DELETED = "-", "Deleted"

    category = models.CharField(
        max_length=30,
        choices=CategoryChoices.choices,
    )

    animal_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    action = models.CharField(
        max_length=1,
        choices=ActionChoices.choices,
    )

    changed_at = models.DateTimeField()

    changed_by = models.CharField(
        max_length=150,
        blank=True,
        null=True,
    )

    changes = models.TextField(
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Track Change"
        verbose_name_plural = "Track Changes"
        ordering = ["-changed_at"]

    def __str__(self):
        return f"{self.get_category_display()} - {self.animal_id}"