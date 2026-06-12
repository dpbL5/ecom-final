# LSTM + RAG + Knowledge Graph Recommender

This project now has a next-buy recommender inside `recommendation-service`.

## Runtime Flow

1. Frontend records behavior into `ProductInteraction`:
   - `viewed`
   - `wishlisted`
   - `added_to_cart`
   - `purchased`
2. `UserBehaviorLSTMRecommender` reads each customer's ordered interaction sequence.
3. If TensorFlow is installed, the training command saves a Keras LSTM model.
4. If TensorFlow is not installed, the same recommender uses a deterministic sequence-transition fallback so the API still runs.
5. The next-buy endpoint blends:
   - LSTM or sequence fallback score
   - Neo4j knowledge graph recommendations
   - search-service product retrieval for product facts used as RAG context
6. The chatbot also receives the LSTM next-buy candidates in its RAG user context.

## API

```http
GET /api/v1/recommendations/next-buy/{customer_id}/?limit=10
Authorization: Bearer <token>
```

Optional query params:

- `limit`: max returned products, default `10`
- `exclude_purchased`: default `true`
- `persist`: when `true`, writes predictions into the existing `recommendations` table

Response shape:

```json
{
  "customer_id": "...",
  "source": "user-behavior LSTM/fallback + Neo4j knowledge graph + search-service RAG product retrieval",
  "model": {
    "model_source": "tensorflow_lstm",
    "sequence_length": 6,
    "trained_at": "..."
  },
  "recommendations": [
    {
      "product_id": "...",
      "sku": "SKU-001",
      "name": "Product name",
      "product_type": "electronics",
      "brand": "Brand",
      "score": 0.91,
      "source": "tensorflow_lstm + neo4j_kg",
      "reason": "..."
    }
  ]
}
```

## Training

Run after seeding or after collecting enough interactions:

```bash
docker compose exec recommendation-service python manage.py train_lstm_recommender --epochs 12 --sequence-length 6
```

To enable the real Keras LSTM path in a custom image or local virtualenv, install:

```bash
pip install -r requirements-ml.txt
```

Without TensorFlow installed, this command still writes:

```text
/app/recommendations/artifacts/user_behavior_lstm.json
```

With TensorFlow installed, it also writes:

```text
/app/recommendations/artifacts/user_behavior_lstm.keras
```

The service can predict without a saved artifact by building an in-memory fallback from current interactions, but the training command makes behavior reproducible.
