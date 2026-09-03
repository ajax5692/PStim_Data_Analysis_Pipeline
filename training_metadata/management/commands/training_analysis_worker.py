import time

from django.core.management.base import BaseCommand

from training_metadata.services import process_next_training_analysis


class Command(BaseCommand):
    help = "Run the background training analysis worker for behavior session licking data."

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                "=====================================================\n"
                "  Training Analysis Worker Started (Polling for jobs)\n"
                "====================================================="
            )
        )

        while True:
            try:
                training_session = process_next_training_analysis()

                if training_session is None:
                    time.sleep(5)
                    continue

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Processed TrainingSession #{training_session.pk} for "
                        f"Animal {training_session.animal.animal_id} on {training_session.training_date}"
                    )
                )

            except KeyboardInterrupt:
                self.stdout.write(
                    self.style.WARNING(
                        "Training analysis worker stopped."
                    )
                )
                break

            except Exception as exc:
                self.stderr.write(
                    self.style.ERROR(
                        f"Training analysis job failed: {exc}"
                    )
                )

