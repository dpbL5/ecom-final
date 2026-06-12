import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from uuid import UUID

from django.conf import settings

from .models import ProductInteraction, Recommendation

try:
    import tensorflow as tf
except ImportError:  # pragma: no cover - the default image keeps ML dependencies optional.
    tf = None


EVENT_WEIGHTS = {
    ProductInteraction.EventType.VIEWED: 0.35,
    ProductInteraction.EventType.WISHLISTED: 0.65,
    ProductInteraction.EventType.ADDED_TO_CART: 0.9,
    ProductInteraction.EventType.PURCHASED: 1.0,
}

PURCHASE_INTENT_BOOSTS = {
    ProductInteraction.EventType.VIEWED: 0.05,
    ProductInteraction.EventType.WISHLISTED: 0.22,
    ProductInteraction.EventType.ADDED_TO_CART: 0.45,
}


@dataclass(frozen=True)
class SequencePrediction:
    product_id: str
    sku: str
    score: float
    source: str
    reason: str

    def as_dict(self):
        return {
            "product_id": self.product_id,
            "sku": self.sku,
            "score": round(float(self.score), 6),
            "source": self.source,
            "reason": self.reason,
        }


class UserBehaviorLSTMRecommender:
    """Next-product predictor for the recommendation service.

    TensorFlow is intentionally optional. When it is available, `train()` writes
    a Keras LSTM model plus JSON metadata. When it is not available, the same
    interface writes a deterministic sequence-transition artifact so the service
    remains runnable in the lightweight Django container.
    """

    def __init__(self, sequence_length=None, artifact_dir=None):
        self.sequence_length = int(sequence_length or getattr(settings, "LSTM_RECOMMENDER", {}).get("SEQUENCE_LENGTH", 6))
        configured_dir = getattr(settings, "LSTM_RECOMMENDER", {}).get("ARTIFACT_DIR")
        self.artifact_dir = Path(artifact_dir or configured_dir or Path(settings.BASE_DIR) / "recommendations" / "artifacts")
        self.metadata_path = self.artifact_dir / "user_behavior_lstm.json"
        self.keras_model_path = self.artifact_dir / "user_behavior_lstm.keras"

    def train(self, *, epochs=12, batch_size=16, min_events=2):
        histories = self._customer_histories(min_events=min_events)
        if not histories:
            raise ValueError("No customer interaction sequences are available for training.")

        artifact = self._build_sequence_artifact(histories)
        artifact["tensorflow_available"] = tf is not None
        artifact["keras_model_path"] = str(self.keras_model_path)

        if tf is None:
            artifact["model_source"] = "sequence_fallback"
            artifact["training_note"] = "TensorFlow is not installed; saved transition-based fallback artifact."
            self._write_artifact(artifact)
            return artifact

        samples, labels, sample_weights, vocab_size = self._build_lstm_samples(histories, artifact["product_to_index"])
        if len(samples) < 2 or vocab_size < 2:
            artifact["model_source"] = "sequence_fallback"
            artifact["training_note"] = "Not enough sequence samples for LSTM; saved transition-based fallback artifact."
            self._write_artifact(artifact)
            return artifact

        model = self._build_keras_model(vocab_size)
        x_train = tf.keras.preprocessing.sequence.pad_sequences(
            samples,
            maxlen=self.sequence_length,
            padding="pre",
            truncating="pre",
            value=0,
        )
        y_train = tf.convert_to_tensor(labels)
        weights = tf.convert_to_tensor(sample_weights)
        model.fit(
            x_train,
            y_train,
            sample_weight=weights,
            epochs=int(epochs),
            batch_size=int(batch_size),
            verbose=0,
        )
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        model.save(self.keras_model_path)

        artifact["model_source"] = "tensorflow_lstm"
        artifact["training_note"] = "Keras LSTM trained successfully."
        artifact["training_samples"] = len(samples)
        artifact["epochs"] = int(epochs)
        artifact["batch_size"] = int(batch_size)
        self._write_artifact(artifact)
        return artifact

    def recommend_for_customer(self, customer_id, *, limit=10, exclude_purchased=True):
        history = list(
            ProductInteraction.objects.filter(customer_id=customer_id).order_by("created_at", "id")
        )
        if not history:
            return []

        artifact = self._load_or_build_artifact()
        fallback_scores = self._score_with_sequence_fallback(history, artifact)
        model_scores = self._score_with_lstm(history, artifact)

        scores = dict(fallback_scores)
        if model_scores:
            fallback_max = max(fallback_scores.values(), default=1.0) or 1.0
            for sku, score in model_scores.items():
                scores[sku] = (0.7 * score) + (0.3 * (fallback_scores.get(sku, 0.0) / fallback_max))

        if exclude_purchased:
            purchased = {item.sku for item in history if item.event_type == ProductInteraction.EventType.PURCHASED}
            for sku in purchased:
                scores.pop(sku, None)

        product_ids = artifact.get("product_ids", {})
        source = artifact.get("model_source", "sequence_fallback")
        sorted_items = sorted(scores.items(), key=lambda item: (-item[1], item[0]))

        predictions = []
        for sku, score in sorted_items:
            if score <= 0:
                continue
            product_id = product_ids.get(sku)
            if not product_id:
                continue
            predictions.append(
                SequencePrediction(
                    product_id=product_id,
                    sku=sku,
                    score=float(score),
                    source=source,
                    reason=self._prediction_reason(sku, history, source),
                ).as_dict()
            )
            if len(predictions) >= int(limit):
                break
        return predictions

    def persist_recommendations(self, customer_id, predictions):
        saved = 0
        for item in predictions:
            product_id = item.get("product_id")
            try:
                UUID(str(product_id))
            except (TypeError, ValueError):
                continue

            try:
                score = Decimal(str(round(float(item.get("score", 0)), 4)))
            except (InvalidOperation, TypeError, ValueError):
                score = Decimal("0")

            Recommendation.objects.update_or_create(
                customer_id=customer_id,
                product_id=product_id,
                defaults={
                    "sku": item.get("sku", ""),
                    "score": score,
                    "reason": item.get("reason", "Predicted next purchase from user behavior sequence.")[:255],
                },
            )
            saved += 1
        return saved

    def metadata(self):
        if not self.metadata_path.exists():
            return {
                "model_source": "untrained",
                "sequence_length": self.sequence_length,
                "tensorflow_available": tf is not None,
                "artifact_path": str(self.metadata_path),
                "keras_model_path": str(self.keras_model_path),
            }
        artifact = self._read_artifact()
        return {
            "model_source": artifact.get("model_source", "sequence_fallback"),
            "sequence_length": artifact.get("sequence_length", self.sequence_length),
            "tensorflow_available": artifact.get("tensorflow_available", tf is not None),
            "trained_at": artifact.get("trained_at"),
            "training_samples": artifact.get("training_samples", 0),
            "training_note": artifact.get("training_note", ""),
            "artifact_path": str(self.metadata_path),
            "keras_model_path": artifact.get("keras_model_path", str(self.keras_model_path)),
        }

    def _customer_histories(self, *, min_events):
        histories = defaultdict(list)
        queryset = ProductInteraction.objects.all().order_by("customer_id", "created_at", "id")
        for item in queryset:
            histories[str(item.customer_id)].append(item)
        return {customer_id: items for customer_id, items in histories.items() if len(items) >= int(min_events)}

    def _build_sequence_artifact(self, histories):
        product_ids = {}
        product_counter = Counter()
        transition_scores = defaultdict(Counter)

        for events in histories.values():
            for item in events:
                product_ids[item.sku] = str(item.product_id)
                product_counter[item.sku] += EVENT_WEIGHTS.get(item.event_type, 0.3)

            for previous, current in zip(events, events[1:]):
                if previous.sku == current.sku and current.event_type != ProductInteraction.EventType.PURCHASED:
                    continue
                transition_weight = EVENT_WEIGHTS.get(previous.event_type, 0.3) * EVENT_WEIGHTS.get(current.event_type, 0.3)
                transition_scores[previous.sku][current.sku] += transition_weight

        skus = sorted(product_ids)
        product_to_index = {sku: index + 1 for index, sku in enumerate(skus)}
        index_to_product = {str(index): sku for sku, index in product_to_index.items()}
        normalized_transitions = {
            source: self._normalize_counter(targets)
            for source, targets in transition_scores.items()
        }
        popularity = self._normalize_counter(product_counter)

        return {
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "sequence_length": self.sequence_length,
            "product_ids": product_ids,
            "product_to_index": product_to_index,
            "index_to_product": index_to_product,
            "transition_scores": normalized_transitions,
            "global_popularity": popularity,
            "customer_sequences": len(histories),
            "product_count": len(product_to_index),
        }

    def _build_lstm_samples(self, histories, product_to_index):
        samples = []
        labels = []
        sample_weights = []
        for events in histories.values():
            sequence = [product_to_index[item.sku] for item in events if item.sku in product_to_index]
            if len(sequence) < 2:
                continue
            for index in range(1, len(sequence)):
                samples.append(sequence[max(0, index - self.sequence_length) : index])
                labels.append(sequence[index])
                sample_weights.append(EVENT_WEIGHTS.get(events[index].event_type, 0.3))
        return samples, labels, sample_weights, len(product_to_index)

    def _build_keras_model(self, vocab_size):
        embedding_dim = min(48, max(8, int(math.sqrt(vocab_size + 1) * 4)))
        model = tf.keras.Sequential(
            [
                tf.keras.layers.Embedding(vocab_size + 1, embedding_dim, mask_zero=True),
                tf.keras.layers.LSTM(64),
                tf.keras.layers.Dropout(0.15),
                tf.keras.layers.Dense(vocab_size + 1, activation="softmax"),
            ]
        )
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.003),
            loss="sparse_categorical_crossentropy",
            metrics=["sparse_categorical_accuracy"],
        )
        return model

    def _score_with_lstm(self, history, artifact):
        if tf is None or artifact.get("model_source") != "tensorflow_lstm" or not self.keras_model_path.exists():
            return {}

        product_to_index = artifact.get("product_to_index", {})
        index_to_product = artifact.get("index_to_product", {})
        sequence = [product_to_index[item.sku] for item in history[-self.sequence_length :] if item.sku in product_to_index]
        if not sequence:
            return {}

        model = tf.keras.models.load_model(self.keras_model_path)
        x_input = tf.keras.preprocessing.sequence.pad_sequences(
            [sequence],
            maxlen=int(artifact.get("sequence_length", self.sequence_length)),
            padding="pre",
            truncating="pre",
            value=0,
        )
        probabilities = model.predict(x_input, verbose=0)[0]
        scores = {}
        for index, probability in enumerate(probabilities):
            if index == 0:
                continue
            sku = index_to_product.get(str(index))
            if sku:
                scores[sku] = float(probability)
        return scores

    def _score_with_sequence_fallback(self, history, artifact):
        transitions = artifact.get("transition_scores", {})
        popularity = artifact.get("global_popularity", {})
        product_ids = artifact.get("product_ids", {})
        scores = defaultdict(float)

        recent = history[-self.sequence_length :]
        for recency_index, event in enumerate(reversed(recent)):
            recency_weight = 1.0 / (recency_index + 1)
            event_weight = EVENT_WEIGHTS.get(event.event_type, 0.3)
            for target_sku, transition_score in transitions.get(event.sku, {}).items():
                scores[target_sku] += float(transition_score) * event_weight * recency_weight

            boost = PURCHASE_INTENT_BOOSTS.get(event.event_type, 0.0)
            if boost:
                scores[event.sku] += boost * recency_weight

        for sku, score in popularity.items():
            if sku in product_ids:
                scores[sku] += float(score) * 0.08

        return dict(scores)

    def _load_or_build_artifact(self):
        if self.metadata_path.exists():
            return self._read_artifact()
        histories = self._customer_histories(min_events=1)
        if not histories:
            return {
                "model_source": "untrained",
                "sequence_length": self.sequence_length,
                "product_ids": {},
                "transition_scores": {},
                "global_popularity": {},
            }
        artifact = self._build_sequence_artifact(histories)
        artifact["model_source"] = "sequence_fallback"
        artifact["tensorflow_available"] = tf is not None
        artifact["training_note"] = "Built in-memory fallback from current interactions; run train_lstm_recommender to persist it."
        return artifact

    def _prediction_reason(self, sku, history, source):
        recent = ", ".join(f"{item.event_type}:{item.sku}" for item in history[-3:])
        if source == "tensorflow_lstm":
            return f"LSTM sequence model predicts SKU {sku} as a likely next purchase from recent behavior: {recent}."
        return f"Sequence fallback predicts SKU {sku} from recent behavior transitions: {recent}."

    def _normalize_counter(self, counter):
        total = sum(float(value) for value in counter.values()) or 1.0
        return {key: round(float(value) / total, 8) for key, value in counter.items()}

    def _read_artifact(self):
        with self.metadata_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _write_artifact(self, artifact):
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        with self.metadata_path.open("w", encoding="utf-8") as handle:
            json.dump(artifact, handle, ensure_ascii=False, indent=2)
