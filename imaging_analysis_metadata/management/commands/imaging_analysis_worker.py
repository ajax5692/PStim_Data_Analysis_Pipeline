import time

from django.core.management.base import BaseCommand

from imaging_analysis_metadata.services import process_next_analysis


class Command(BaseCommand):
    help = "Run the imaging analysis worker."

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                "=====================================================\n"
                "  Imaging Analysis Worker Started (Polling for jobs)\n"
                "====================================================="
            )
        )

        while True:
            try:
                analysis_run = process_next_analysis(logger_func=self.stdout.write)

                if analysis_run is None:
                    time.sleep(5)
                    continue

                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n✓ Successfully completed AnalysisRun #{analysis_run.pk}\n"
                    )
                )

            except KeyboardInterrupt:
                self.stdout.write(
                    self.style.WARNING(
                        "\nImaging analysis worker stopped by user."
                    )
                )
                break

            except Exception as exc:
                self.stderr.write(
                    self.style.ERROR(
                        f"\n✗ Analysis job failed: {exc}\n"
                    )
                )
