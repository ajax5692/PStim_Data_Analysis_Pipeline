import time
from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from imaging_analysis_metadata.services import process_next_analysis


class Command(BaseCommand):
    help = "Run the imaging analysis background worker."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--once",
            action="store_true",
            help="Process all currently pending analysis jobs and then exit immediately.",
        )
        parser.add_argument(
            "--poll-interval",
            type=int,
            default=5,
            help="Seconds to sleep between queue polling checks (default: 5).",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        run_once: bool = options.get("once", False)
        poll_interval: int = max(1, options.get("poll_interval", 5))

        mode_text = "Single-pass execution (--once)" if run_once else f"Continuous polling (every {poll_interval}s)"
        self.stdout.write(
            self.style.SUCCESS(
                "=====================================================\n"
                f"  Imaging Analysis Worker Started [{mode_text}]\n"
                "====================================================="
            )
        )

        while True:
            try:
                analysis_run = process_next_analysis(logger_func=self.stdout.write)

                if analysis_run is None:
                    if run_once:
                        self.stdout.write(
                            self.style.SUCCESS("No pending imaging analysis jobs. Exiting (--once).")
                        )
                        break
                    time.sleep(poll_interval)
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
                if run_once:
                    break
