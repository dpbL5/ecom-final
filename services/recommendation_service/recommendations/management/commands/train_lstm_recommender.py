from django.core.management.base import BaseCommand, CommandError

from recommendations.sequence_model import UserBehaviorLSTMRecommender


class Command(BaseCommand):
    help = "Train the user-behavior LSTM recommender or save a sequence fallback artifact."

    def add_arguments(self, parser):
        parser.add_argument("--epochs", type=int, default=12, help="Training epochs when TensorFlow is installed.")
        parser.add_argument("--batch-size", type=int, default=16, help="Training batch size when TensorFlow is installed.")
        parser.add_argument("--sequence-length", type=int, default=6, help="Number of recent events used as model input.")
        parser.add_argument("--min-events", type=int, default=2, help="Minimum events required per customer sequence.")

    def handle(self, *args, **options):
        recommender = UserBehaviorLSTMRecommender(sequence_length=options["sequence_length"])
        try:
            artifact = recommender.train(
                epochs=options["epochs"],
                batch_size=options["batch_size"],
                min_events=options["min_events"],
            )
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.SUCCESS(
                "LSTM recommender artifact ready: "
                f"source={artifact.get('model_source')}, "
                f"products={artifact.get('product_count')}, "
                f"customers={artifact.get('customer_sequences')}, "
                f"samples={artifact.get('training_samples', 0)}"
            )
        )
