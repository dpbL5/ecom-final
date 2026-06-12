import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from recommendations.graph import Neo4jRecommender, Neo4jUnavailable


class Command(BaseCommand):
    help = "Seed Neo4j recommendation graph from a JSON file."

    def add_arguments(self, parser):
        parser.add_argument("--file", help="Path to JSON graph seed data.")

    def handle(self, *args, **options):
        seed_path = Path(options["file"]) if options.get("file") else Path(__file__).resolve().parents[2] / "fixtures" / "neo4j_recommender_seed.json"
        if not seed_path.exists():
            raise CommandError(f"Seed file not found: {seed_path}")

        with seed_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        try:
            summary = Neo4jRecommender().seed(payload)
        except Neo4jUnavailable as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(self.style.SUCCESS(f"Neo4j graph seeded: {summary}"))
