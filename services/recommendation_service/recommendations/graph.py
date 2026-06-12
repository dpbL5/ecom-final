from contextlib import contextmanager

from django.conf import settings

try:
    from neo4j import GraphDatabase
except ImportError:  # pragma: no cover - dependency is available in Docker image after requirements install.
    GraphDatabase = None


EVENT_RELATIONSHIPS = {
    "viewed": "VIEWED",
    "added_to_cart": "ADDED_TO_CART",
    "purchased": "PURCHASED",
    "wishlisted": "WISHLISTED",
}


class Neo4jUnavailable(RuntimeError):
    pass


class Neo4jRecommender:
    def __init__(self):
        config = getattr(settings, "NEO4J", {})
        self.enabled = config.get("ENABLED", False)
        self.database = config.get("DATABASE") or "neo4j"
        if not self.enabled or GraphDatabase is None:
            self.driver = None
            return
        self.driver = GraphDatabase.driver(
            config.get("URI"),
            auth=(config.get("USER"), config.get("PASSWORD")),
        )

    @contextmanager
    def session(self):
        if self.driver is None:
            raise Neo4jUnavailable("Neo4j driver is disabled or not installed.")
        with self.driver.session(database=self.database) as session:
            yield session

    def verify(self):
        if self.driver is None:
            raise Neo4jUnavailable("Neo4j driver is disabled or not installed.")
        self.driver.verify_connectivity()

    def ensure_schema(self):
        with self.session() as session:
            session.run("CREATE CONSTRAINT customer_id_unique IF NOT EXISTS FOR (c:Customer) REQUIRE c.customer_id IS UNIQUE")
            session.run("CREATE CONSTRAINT product_sku_unique IF NOT EXISTS FOR (p:Product) REQUIRE p.sku IS UNIQUE")

    def seed(self, payload):
        self.ensure_schema()
        users = payload.get("users", [])
        products = payload.get("products", [])
        similarities = payload.get("similarities", [])
        interactions = payload.get("interactions", [])

        with self.session() as session:
            for user in users:
                session.run(
                    """
                    MERGE (c:Customer {customer_id: $customer_id})
                    SET c.email = $email,
                        c.full_name = $full_name,
                        c.segment = $segment
                    """,
                    customer_id=str(user["customer_id"]),
                    email=user.get("email", ""),
                    full_name=user.get("full_name", ""),
                    segment=user.get("segment", ""),
                )

            for product in products:
                session.run(
                    """
                    MERGE (p:Product {sku: $sku})
                    SET p.product_id = $product_id,
                        p.name = $name,
                        p.product_type = $product_type,
                        p.brand = $brand,
                        p.price = $price,
                        p.search_text = $search_text
                    """,
                    product_id=str(product.get("product_id") or product["sku"]),
                    sku=product["sku"],
                    name=product.get("name", ""),
                    product_type=product.get("product_type", ""),
                    brand=product.get("brand", ""),
                    price=product.get("price", 0),
                    search_text=product.get("search_text", ""),
                )

            for item in similarities:
                session.run(
                    """
                    MATCH (source:Product {sku: $from_sku})
                    MATCH (target:Product {sku: $to_sku})
                    MERGE (source)-[r:SIMILAR]->(target)
                    SET r.score = $score,
                        r.reason = $reason
                    """,
                    from_sku=item["from_sku"],
                    to_sku=item["to_sku"],
                    score=float(item.get("score", 0.5)),
                    reason=item.get("reason", "Related product in recommendation graph."),
                )

            for item in interactions:
                event_type = item.get("event_type", "viewed")
                relationship = EVENT_RELATIONSHIPS.get(event_type)
                if relationship is None:
                    continue
                session.run(
                    f"""
                    MATCH (c:Customer {{customer_id: $customer_id}})
                    MATCH (p:Product {{sku: $sku}})
                    MERGE (c)-[r:{relationship}]->(p)
                    SET r.weight = $weight,
                        r.event_type = $event_type,
                        r.timestamp = $timestamp
                    """,
                    customer_id=str(item["customer_id"]),
                    sku=item["sku"],
                    weight=float(item.get("weight", 1)),
                    event_type=event_type,
                    timestamp=item.get("timestamp", ""),
                )

        return {
            "users": len(users),
            "products": len(products),
            "similarities": len(similarities),
            "interactions": len(interactions),
        }

    def recommend_for_customer(self, customer_id, limit=10):
        with self.session() as session:
            result = session.run(
                """
                MATCH (c:Customer {customer_id: $customer_id})-[i:VIEWED|ADDED_TO_CART|PURCHASED|WISHLISTED]->(p:Product)
                MATCH (p)-[s:SIMILAR]->(rec:Product)
                WHERE NOT (c)-[:VIEWED|ADDED_TO_CART|PURCHASED|WISHLISTED]->(rec)
                WITH rec,
                     sum(coalesce(i.weight, 1.0) * coalesce(s.score, 0.5)) AS score,
                     collect(DISTINCT p.name) AS based_on,
                     collect(DISTINCT s.reason) AS graph_reasons
                RETURN rec.product_id AS product_id,
                       rec.sku AS sku,
                       rec.name AS name,
                       rec.product_type AS product_type,
                       rec.brand AS brand,
                       score,
                       based_on,
                       graph_reasons
                ORDER BY score DESC, name ASC
                LIMIT $limit
                """,
                customer_id=str(customer_id),
                limit=int(limit),
            )
            return [dict(record) for record in result]

    def related_by_sku(self, skus, limit=10):
        with self.session() as session:
            result = session.run(
                """
                MATCH (p:Product)-[s:SIMILAR]->(rec:Product)
                WHERE p.sku IN $skus
                RETURN rec.product_id AS product_id,
                       rec.sku AS sku,
                       rec.name AS name,
                       rec.product_type AS product_type,
                       rec.brand AS brand,
                       max(s.score) AS score,
                       collect(DISTINCT p.name) AS based_on,
                       collect(DISTINCT s.reason) AS graph_reasons
                ORDER BY score DESC, name ASC
                LIMIT $limit
                """,
                skus=list(skus),
                limit=int(limit),
            )
            return [dict(record) for record in result]
