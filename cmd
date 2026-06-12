docker compose exec identity-service pip install requests
docker compose exec identity-service python /app/seed_data.py

docker compose exec recommendation-service python manage.py train_lstm_recommender --epochs 12 --sequence-length 6