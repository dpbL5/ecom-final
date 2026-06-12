import unicodedata

from django.conf import settings
from rest_framework import permissions, status, views, viewsets
from rest_framework.response import Response

from ecommerce_common.clients import ServiceClient, ServiceClientError, bearer_token_from_request
from ecommerce_common.permissions import IsAdminOrStaff

from .gemma import GemmaUnavailable, generate_product_advice, is_gemma_configured
from .graph import Neo4jRecommender, Neo4jUnavailable
from .models import ProductInteraction, Recommendation
from .serializers import AIChatRequestSerializer, ProductInteractionSerializer, RecommendationSerializer
from .sequence_model import UserBehaviorLSTMRecommender


def normalize_text(value):
    normalized = unicodedata.normalize("NFD", value.lower())
    without_marks = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    return without_marks.replace("đ", "d")


def classify_intent(message):
    normalized = normalize_text(message)
    if any(keyword in normalized for keyword in ("book", "sach", "isbn", "author", "tac gia")):
        return "book"
    if any(keyword in normalized for keyword in ("phone", "laptop", "mobile", "dien tu", "electronics", "gaming", "may tinh")):
        return "electronics"
    if any(keyword in normalized for keyword in ("fashion", "ao", "quan", "giay", "size", "color", "mau")):
        return "fashion"
    return ""


def build_reason(product, intent):
    product_type = product.get("product_type", "")
    brand = product.get("brand", "")
    type_labels = {
        "book": "sách",
        "electronics": "điện tử",
        "fashion": "thời trang",
        "home": "gia dụng",
    }
    if intent and product_type == intent:
        return f"Phù hợp với nhóm {type_labels.get(intent, intent)} mà khách đang tìm."
    if brand:
        return f"Sản phẩm liên quan trong catalog từ thương hiệu {brand}."
    return "Sản phẩm liên quan được lấy từ chỉ mục tìm kiếm."


def graph_reason(item):
    based_on = ", ".join(item.get("based_on") or [])
    reasons = "; ".join(reason for reason in (item.get("graph_reasons") or []) if reason)
    if based_on and reasons:
        return f"Gợi ý từ Neo4j dựa trên {based_on}: {reasons}"
    if based_on:
        return f"Gợi ý từ Neo4j dựa trên các sản phẩm khách đã tương tác: {based_on}."
    return "Gợi ý từ độ tương đồng sản phẩm trên Neo4j."


def graph_item_to_suggestion(item):
    return {
        "product_id": item.get("product_id") or item.get("sku"),
        "sku": item.get("sku", ""),
        "name": item.get("name", ""),
        "product_type": item.get("product_type", ""),
        "brand": item.get("brand", ""),
        "reason": graph_reason(item),
        "score": float(item.get("score") or 0),
    }


def parse_positive_int(value, default=10, maximum=50):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, min(parsed, maximum))


def query_search_products(token, params):
    documents = ServiceClient(settings.SERVICE_URLS["search"]).request(
        "GET",
        "/api/v1/products/search/",
        token=token,
        params=params,
    )
    if isinstance(documents, dict):
        documents = documents.get("results", [])
    return documents if isinstance(documents, list) else []


def build_product_lookup(skus, token):
    clean_skus = [sku for sku in dict.fromkeys(skus) if sku]
    if not clean_skus:
        return {}
    try:
        documents = query_search_products(token, {"sku": ",".join(clean_skus)})
    except Exception:
        return {}
    return {item.get("sku"): item for item in documents if item.get("sku")}


def prediction_item_to_suggestion(item, product_lookup=None):
    product_lookup = product_lookup or {}
    document = product_lookup.get(item.get("sku")) or {}
    return {
        "product_id": str(document.get("product_id") or item.get("product_id") or item.get("sku")),
        "sku": item.get("sku", ""),
        "name": document.get("name") or item.get("name", "") or item.get("sku", ""),
        "product_type": document.get("product_type") or item.get("product_type", ""),
        "brand": document.get("brand") or item.get("brand", ""),
        "reason": item.get("reason", "Predicted as a likely next purchase from recent behavior."),
        "score": float(item.get("score") or 0),
        "source": item.get("source", "lstm"),
    }


def normalize_scores(items):
    max_score = max((float(item.get("score") or 0) for item in items), default=0)
    if max_score <= 0:
        return [(item, 0.0) for item in items]
    return [(item, float(item.get("score") or 0) / max_score) for item in items]


def merge_next_buy_candidates(lstm_items, graph_items, product_lookup):
    merged = {}

    def add_item(item, normalized_score, source, reason):
        sku = item.get("sku")
        if not sku:
            return
        document = product_lookup.get(sku) or {}
        entry = merged.setdefault(
            sku,
            {
                "product_id": str(document.get("product_id") or item.get("product_id") or sku),
                "sku": sku,
                "name": document.get("name") or item.get("name", "") or sku,
                "product_type": document.get("product_type") or item.get("product_type", ""),
                "brand": document.get("brand") or item.get("brand", ""),
                "score": 0.0,
                "sources": [],
                "reasons": [],
            },
        )
        entry["score"] += normalized_score
        if source not in entry["sources"]:
            entry["sources"].append(source)
        if reason and reason not in entry["reasons"]:
            entry["reasons"].append(reason)

    for item, score in normalize_scores(lstm_items):
        add_item(item, score * 0.65, item.get("source", "lstm"), item.get("reason", "LSTM next-buy prediction."))

    for item, score in normalize_scores(graph_items):
        add_item(item, score * 0.35, "neo4j_kg", graph_reason(item))

    recommendations = []
    for item in merged.values():
        recommendations.append(
            {
                "product_id": item["product_id"],
                "sku": item["sku"],
                "name": item["name"],
                "product_type": item["product_type"],
                "brand": item["brand"],
                "score": round(item["score"], 6),
                "source": " + ".join(item["sources"]),
                "reason": " ".join(item["reasons"])[:500],
            }
        )
    return sorted(recommendations, key=lambda item: (-item["score"], item["name"], item["sku"]))


def build_next_buy_recommendations(customer_id, token, *, limit=10, exclude_purchased=True, persist=False):
    recommender = UserBehaviorLSTMRecommender()
    model_limit = max(limit * 2, 10)
    lstm_items = recommender.recommend_for_customer(
        customer_id,
        limit=model_limit,
        exclude_purchased=exclude_purchased,
    )

    try:
        graph_items = Neo4jRecommender().recommend_for_customer(customer_id, limit=model_limit)
    except Exception:
        graph_items = []

    skus = [item.get("sku") for item in lstm_items] + [item.get("sku") for item in graph_items]
    product_lookup = build_product_lookup(skus, token)
    recommendations = merge_next_buy_candidates(lstm_items, graph_items, product_lookup)[:limit]

    saved_count = recommender.persist_recommendations(customer_id, recommendations) if persist else 0
    model = recommender.metadata()
    if model.get("model_source") == "untrained" and lstm_items:
        model["model_source"] = lstm_items[0].get("source", "sequence_fallback")
        model["training_note"] = "Using in-memory sequence fallback from current interactions; run train_lstm_recommender to persist it."
    model["saved_recommendations"] = saved_count
    return recommendations, model


def build_rag_user_context(customer_id, token):
    if not customer_id:
        return ""

    context_parts = []
    if token:
        try:
            profile = ServiceClient(settings.SERVICE_URLS["customer"]).request(
                "GET",
                f"/api/v1/customers/{customer_id}/",
                token=token,
            )
            preferences = profile.get("preferences") or {}
            context_parts.append(
                "Customer profile: "
                f"name={profile.get('full_name', '')}, "
                f"email={profile.get('email', '')}, "
                f"preferences={preferences}"
            )
        except Exception:
            pass

    try:
        interactions = ProductInteraction.objects.filter(customer_id=customer_id).order_by("-created_at")[:12]
        if interactions:
            history = ", ".join(f"{item.event_type}:{item.sku}" for item in interactions)
            context_parts.append(f"Recent behavior from recommendation service: {history}")
    except Exception:
        pass

    try:
        sequence_items = UserBehaviorLSTMRecommender().recommend_for_customer(customer_id, limit=5)
        if sequence_items:
            product_lookup = build_product_lookup([item.get("sku") for item in sequence_items], token)
            sequence_context = ", ".join(
                f"{(product_lookup.get(item.get('sku')) or {}).get('name') or item.get('sku')} score={round(float(item.get('score') or 0), 2)}"
                for item in sequence_items
            )
            context_parts.append(f"LSTM next-buy candidates: {sequence_context}")
    except Exception:
        pass

    try:
        graph_items = Neo4jRecommender().recommend_for_customer(customer_id, limit=5)
        if graph_items:
            graph_context = ", ".join(f"{item.get('name')} score={round(float(item.get('score') or 0), 2)}" for item in graph_items)
            context_parts.append(f"Neo4j personalized graph candidates: {graph_context}")
    except Exception:
        pass

    return "\n".join(context_parts)


class ProductInteractionViewSet(viewsets.ModelViewSet):
    queryset = ProductInteraction.objects.all().order_by("-created_at")
    serializer_class = ProductInteractionSerializer


class RecommendationViewSet(viewsets.ModelViewSet):
    queryset = Recommendation.objects.all().order_by("-score")
    serializer_class = RecommendationSerializer


class RecommendationForCustomerView(views.APIView):
    def get(self, request, customer_id):
        queryset = Recommendation.objects.filter(customer_id=customer_id).order_by("-score")[:50]
        return Response(RecommendationSerializer(queryset, many=True).data)


class GraphSeedView(views.APIView):
    permission_classes = [IsAdminOrStaff]

    def post(self, request):
        try:
            summary = Neo4jRecommender().seed(request.data)
        except Neo4jUnavailable as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as exc:
            return Response({"detail": f"Neo4j seed failed: {exc}"}, status=status.HTTP_502_BAD_GATEWAY)
        return Response(
            {
                "detail": "Neo4j recommendation graph seeded.",
                "summary": summary,
            },
            status=status.HTTP_201_CREATED,
        )


class GraphRecommendationView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, customer_id):
        limit = request.query_params.get("limit", 10)
        try:
            recommendations = Neo4jRecommender().recommend_for_customer(customer_id, limit=limit)
        except Neo4jUnavailable as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as exc:
            return Response({"detail": f"Neo4j recommendation query failed: {exc}"}, status=status.HTTP_502_BAD_GATEWAY)
        return Response(
            {
                "customer_id": str(customer_id),
                "source": "neo4j graph: customer behavior -> product similarity",
                "recommendations": [graph_item_to_suggestion(item) for item in recommendations],
            }
        )


class NextBuyRecommendationView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, customer_id):
        limit = parse_positive_int(request.query_params.get("limit"), default=10, maximum=50)
        persist = str(request.query_params.get("persist", "false")).lower() in {"1", "true", "yes", "on"}
        exclude_purchased = str(request.query_params.get("exclude_purchased", "true")).lower() in {"1", "true", "yes", "on"}
        token = bearer_token_from_request(request)

        recommendations, model = build_next_buy_recommendations(
            customer_id,
            token,
            limit=limit,
            exclude_purchased=exclude_purchased,
            persist=persist,
        )
        return Response(
            {
                "customer_id": str(customer_id),
                "source": "user-behavior LSTM/fallback + Neo4j knowledge graph + search-service RAG product retrieval",
                "model": model,
                "recommendations": recommendations,
            }
        )


class AIChatbotView(views.APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = AIChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data["message"]
        intent = classify_intent(message)
        token = bearer_token_from_request(request)

        try:
            documents = ServiceClient(settings.SERVICE_URLS["search"]).request(
                "GET",
                "/api/v1/products/search/",
                token=token,
                params={"q": message},
            )
        except ServiceClientError as exc:
            return Response(
                {
                    "answer": "AI advisor could not retrieve product documents from Search service.",
                    "source": str(exc),
                    "intent": intent,
                    "suggestions": [],
                },
                status=502,
            )

        if isinstance(documents, dict):
            documents = documents.get("results", [])

        filtered = [item for item in documents if not intent or item.get("product_type") == intent]
        if intent and not filtered:
            try:
                type_documents = ServiceClient(settings.SERVICE_URLS["search"]).request(
                    "GET",
                    "/api/v1/products/search/",
                    token=token,
                    params={"type": intent},
                )
                if isinstance(type_documents, dict):
                    type_documents = type_documents.get("results", [])
                if type_documents:
                    documents = type_documents
                    filtered = [item for item in documents if item.get("product_type") == intent]
            except ServiceClientError:
                pass

        selected = (filtered or documents)[:3]
        suggestions = [
            {
                "product_id": item["product_id"],
                "sku": item["sku"],
                "name": item["name"],
                "product_type": item.get("product_type", ""),
                "brand": item.get("brand", ""),
                "reason": build_reason(item, intent),
            }
            for item in selected
        ]

        customer_id = serializer.validated_data.get("customer_id")
        graph_suggestions = []
        try:
            if customer_id:
                graph_items = Neo4jRecommender().recommend_for_customer(customer_id, limit=3)
            else:
                graph_items = Neo4jRecommender().related_by_sku([item["sku"] for item in selected], limit=3)
            graph_suggestions = [graph_item_to_suggestion(item) for item in graph_items]
        except Exception:
            graph_suggestions = []

        sequence_suggestions = []
        try:
            if customer_id:
                sequence_items = UserBehaviorLSTMRecommender().recommend_for_customer(customer_id, limit=3)
                product_lookup = build_product_lookup([item.get("sku") for item in sequence_items], token)
                sequence_suggestions = [prediction_item_to_suggestion(item, product_lookup) for item in sequence_items]
        except Exception:
            sequence_suggestions = []

        seen_skus = {item["sku"] for item in suggestions}
        for item in graph_suggestions + sequence_suggestions:
            if intent and item.get("product_type") != intent:
                continue
            if item["sku"] and item["sku"] not in seen_skus:
                suggestions.append(item)
                seen_skus.add(item["sku"])
            if len(suggestions) >= 5:
                break

        source = "recommendation-service AI demo: query -> search-service retrieval -> heuristic ranking -> optional Neo4j graph similarity -> optional LSTM next-buy prediction"
        user_context = build_rag_user_context(customer_id, token)
        if suggestions and is_gemma_configured():
            try:
                answer = generate_product_advice(message, suggestions, user_context=user_context)
                source = f"{source} -> Gemma 4 Gemini API"
            except GemmaUnavailable:
                answer = ""
        else:
            answer = ""

        if not answer and suggestions:
            names = ", ".join(item["name"] for item in suggestions)
            answer = (
                f"Mình gợi ý {names}. "
                "Các gợi ý này được chọn từ tài liệu tìm kiếm, intent của câu hỏi và độ tương đồng trên Neo4j khi có dữ liệu."
            )
        elif not answer:
            answer = (
                "Mình chưa tìm thấy sản phẩm đủ gần với nhu cầu này. Bạn có thể nhập rõ hơn như laptop, sách, thời trang, SKU hoặc thương hiệu."
            )

        return Response(
            {
                "answer": answer,
                "source": source,
                "intent": intent,
                "suggestions": suggestions,
            }
        )
