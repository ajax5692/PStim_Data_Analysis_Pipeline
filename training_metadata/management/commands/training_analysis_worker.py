import time
from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from training_metadata.services import process_next_training_analysis


class Command(BaseCommand):
    help = "Run the background training analysis worker for behavior session licking data."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--once",
            action="store_true",
            help="Process all currently pending training sessions and then exit immediately.",
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
                f"  Training Analysis Worker Started [{mode_text}]\n"
                "====================================================="
            )
        )

        while True:
            try:
                training_session = process_next_training_analysis()

                if training_session is None:
                    if run_once:
                        self.stdout.write(
                            self.style.SUCCESS("No pending training sessions. Exiting (--once).")
                        )
                        break
                    time.sleep(poll_interval)
                    continue

                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n✓ Processed TrainingSession #{training_session.pk} for "
                        f"Animal {training_session.animal.animal_id} on {training_session.training_date}\n"
                    )
                )

            except KeyboardInterrupt:
                self.stdout.write(
                    self.style.WARNING(
                        "\nTraining analysis worker stopped by user."
                    )
                )
                break

            except Exception as exc:
                self.stderr.write(
                    self.style.ERROR(
                        f"\n✗ Training analysis job failed: {exc}\n"
                    )
                )
                if run_once:
                    break
