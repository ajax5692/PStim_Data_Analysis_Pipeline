import time

from django.core.management.base import BaseCommand

from imaging_analysis_metadata.services import process_next_analysis


class Command(BaseCommand):
    help = "Run the imaging analysis worker."

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                "Imaging analysis worker started."
            )
        )

        while True:
            try:
                analysis_run = process_next_analysis()

                if analysis_run is None:
                    time.sleep(5)
                    continue

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Processed AnalysisRun #{analysis_run.pk}"
                    )
                )

            except KeyboardInterrupt:
                self.stdout.write(
                    self.style.WARNING(
                        "Imaging analysis worker stopped."
                    )
                )
                break

            except Exception as exc:
                self.stderr.write(
                    self.style.ERROR(
                        f"Analysis job failed: {exc}"
                    )
                )