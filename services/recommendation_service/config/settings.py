from pathlib import Path
import os

from ecommerce_common.settings import configure


BASE_DIR = Path(__file__).resolve().parent.parent
configure(globals(), service_name="recommendation", base_dir=BASE_DIR, local_apps=["recommendations"])

NEO4J = {
    "URI": os.getenv("NEO4J_URI", "bolt://neo4j:7687"),
    "USER": os.getenv("NEO4J_USER", "neo4j"),
    "PASSWORD": os.getenv("NEO4J_PASSWORD", "ecommerce-graph"),
    "DATABASE": os.getenv("NEO4J_DATABASE", "neo4j"),
    "ENABLED": os.getenv("NEO4J_ENABLED", "true").lower() in {"1", "true", "yes", "on"},
}

GEMMA = {
    "API_KEY": os.getenv("GEMMA_API_KEY", ""),
    "MODEL": os.getenv("GEMMA_MODEL", "gemma-4-26b-a4b-it"),
    "BASE_URL": os.getenv("GEMMA_BASE_URL", "https://generativelanguage.googleapis.com/v1beta"),
    "TIMEOUT": int(os.getenv("GEMMA_TIMEOUT", "45")),
}

LSTM_RECOMMENDER = {
    "SEQUENCE_LENGTH": int(os.getenv("LSTM_SEQUENCE_LENGTH", "6")),
    "ARTIFACT_DIR": os.getenv("LSTM_ARTIFACT_DIR", str(BASE_DIR / "recommendations" / "artifacts")),
}
