import json
import random
import re
import subprocess
import sys
import unicodedata
from decimal import Decimal
from urllib.parse import quote_plus


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


PASSWORD = "password123"
RANDOM = random.Random(20260612)


def run_django_code(service, python_code):
    print(f"--- Running seed script in {service} ---")
    proc = subprocess.run(
        ["docker", "compose", "exec", "-T", service, "python", "manage.py", "shell"],
        input=python_code,
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    if proc.returncode != 0:
        print(f"Error seeding {service} (Return Code {proc.returncode}):")
        print(proc.stderr)
        return ""

    print(proc.stdout)
    if proc.stderr:
        print("Warnings/Errors in stderr:")
        print(proc.stderr)
    return proc.stdout


def marker_json(output, marker):
    match = re.search(rf"{marker}_START\r?\n(.*?)\r?\n{marker}_END", output, re.DOTALL)
    if not match:
        return {}
    return json.loads(match.group(1).strip())


def slugify(value):
    value = unicodedata.normalize("NFD", value.lower())
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")
    value = value.replace("đ", "d")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def image_url(query, sku):
    # Unsplash Source returns a product-relevant photo by query instead of random placeholder noise.
    return f"https://source.unsplash.com/600x600/?{quote_plus(query)}&sig={quote_plus(sku)}"


def build_users():
    users = [
        {
            "email": "admin@example.com",
            "password": PASSWORD,
            "full_name": "Admin User",
            "role": "admin",
            "is_staff": True,
            "is_superuser": True,
        },
        {
            "email": "staff@example.com",
            "password": PASSWORD,
            "full_name": "Staff User",
            "role": "staff",
            "is_staff": True,
            "is_superuser": False,
        },
    ]
    segments = ["tech_lover", "book_reader", "fashion_buyer", "home_cook", "value_hunter"]
    for index in range(1, 51):
        email = "customer@example.com" if index == 1 else f"customer{index:02d}@example.com"
        users.append(
            {
                "email": email,
                "password": PASSWORD,
                "full_name": f"Demo Customer {index:02d}",
                "role": "customer",
                "is_staff": False,
                "is_superuser": False,
                "segment": segments[(index - 1) % len(segments)],
            }
        )
    return users


def product(sku, name, category_slug, product_type, brand, price, query, description, attributes):
    return {
        "sku": sku,
        "name": name,
        "slug": slugify(f"{name}-{sku}"),
        "category_slug": category_slug,
        "description": description,
        "brand": brand,
        "product_type": product_type,
        "status": "published",
        "price": price,
        "compare_at": int(price * 1.12),
        "quantity": RANDOM.randint(35, 240),
        "rating": round(RANDOM.uniform(4.2, 4.95), 2),
        "attributes": attributes,
        "image_urls": [image_url(query, sku)],
        "search_text": f"{name} {brand} {product_type} {query} {description}",
    }


def build_products():
    products = [
        product("IPHONE15PM", "iPhone 15 Pro Max 256GB Chính Hãng", "dien-thoai-phu-kien", "electronics", "Apple", 29990000, "iphone 15 pro max smartphone", "Điện thoại titanium, chip A17 Pro, camera zoom 5x.", {"color": "Natural Titanium", "storage": "256GB", "warranty_months": 12}),
        product("TSHIRT-SHOPEE-ORG", "Áo thun Polo Shopee Orange Premium", "thoi-trang", "fashion", "Shopee OS", 199000, "orange polo shirt fashion", "Áo polo cotton màu cam, co giãn và thoáng mát.", {"color": "Orange", "size": "L", "material": "Cotton"}),
        product("DDD-BOOK-EVANS", "Sách Domain-Driven Design - Eric Evans", "sach-do-choi", "book", "Addison-Wesley", 850000, "domain driven design book", "Sách kinh điển về DDD và thiết kế phần mềm phức tạp.", {"author": "Eric Evans", "language": "English", "pages": 560}),
        product("LOCK-AIRFRYER", "Nồi Chiên Không Dầu Lock&Lock Eco Fryer 5.2L", "dien-gia-dung", "electronics", "Lock&Lock", 2490000, "air fryer kitchen appliance", "Nồi chiên không dầu 5.2L, chống dính, giảm dầu mỡ.", {"capacity_liters": 5.2, "power_watts": 1800, "color": "Black"}),
    ]

    phones = [
        ("SAMSUNG-S24U", "Samsung Galaxy S24 Ultra 512GB", "Samsung", 27990000, "samsung galaxy s24 ultra smartphone"),
        ("XIAOMI-14T", "Xiaomi 14T Pro 5G 256GB", "Xiaomi", 15990000, "xiaomi smartphone"),
        ("OPPO-RENO12", "OPPO Reno12 5G 256GB", "OPPO", 10990000, "oppo smartphone"),
        ("VIVO-V30", "Vivo V30 5G 256GB", "Vivo", 9990000, "vivo smartphone"),
        ("IPAD-AIR-M2", "iPad Air M2 11 inch WiFi", "Apple", 16990000, "ipad air tablet"),
        ("AIRPODS-PRO2", "AirPods Pro 2 USB-C", "Apple", 5990000, "airpods pro earbuds"),
        ("ANKER-POWERCORE", "Pin Sạc Dự Phòng Anker PowerCore 20000mAh", "Anker", 990000, "anker power bank"),
        ("BASEUS-CABLE", "Cáp Sạc Nhanh Baseus Type-C 100W", "Baseus", 190000, "usb c charging cable"),
        ("LOGI-MXMASTER", "Chuột Logitech MX Master 3S", "Logitech", 2390000, "logitech mouse"),
        ("KEYCHRON-K2", "Bàn Phím Cơ Keychron K2 Wireless", "Keychron", 2190000, "mechanical keyboard"),
        ("SONY-WH1000XM5", "Tai Nghe Sony WH-1000XM5 Chống Ồn", "Sony", 7990000, "sony headphones"),
        ("JBL-FLIP6", "Loa Bluetooth JBL Flip 6", "JBL", 2690000, "jbl bluetooth speaker"),
        ("GARMIN-VENU3", "Đồng Hồ Garmin Venu 3", "Garmin", 9990000, "garmin smartwatch"),
        ("CANON-R50", "Máy Ảnh Canon EOS R50 Kit", "Canon", 18990000, "canon mirrorless camera"),
        ("DJI-MINI4", "Flycam DJI Mini 4 Pro", "DJI", 22990000, "dji drone"),
        ("ASUS-ROG-ALLY", "Máy Chơi Game ASUS ROG Ally Z1 Extreme", "ASUS", 15990000, "handheld gaming console"),
    ]
    for sku, name, brand, price, query in phones:
        products.append(product(sku, name, "dien-thoai-phu-kien", "electronics", brand, price, query, f"{name} chính hãng, hiệu năng cao, phù hợp nhu cầu công nghệ.", {"warranty_months": 12}))

    laptops = [
        ("MACBOOK-AIR-M3", "MacBook Air M3 13 inch 16GB 512GB", "Apple", 32990000, "macbook air laptop"),
        ("DELL-XPS13", "Dell XPS 13 Plus OLED", "Dell", 34990000, "dell xps laptop"),
        ("ASUS-ZENBOOK14", "ASUS Zenbook 14 OLED", "ASUS", 24990000, "asus zenbook laptop"),
        ("LENOVO-LOQ15", "Lenovo LOQ 15 Gaming RTX 4060", "Lenovo", 23990000, "gaming laptop"),
        ("HP-PAVILION", "HP Pavilion 15 Core i5", "HP", 15990000, "hp laptop"),
        ("ACER-NITRO5", "Acer Nitro 5 Gaming RTX 4050", "Acer", 20990000, "acer gaming laptop"),
        ("MSI-MODERN14", "MSI Modern 14 Business Laptop", "MSI", 13990000, "business laptop"),
        ("LG-GRAM16", "LG Gram 16 Siêu Nhẹ", "LG", 29990000, "lg gram laptop"),
        ("SAMSUNG-TAB-S9", "Samsung Galaxy Tab S9 FE", "Samsung", 10990000, "samsung tablet"),
        ("WACOM-ONE", "Bảng Vẽ Wacom One Medium", "Wacom", 2990000, "wacom drawing tablet"),
    ]
    for sku, name, brand, price, query in laptops:
        products.append(product(sku, name, "dien-thoai-phu-kien", "electronics", brand, price, query, f"{name} phù hợp học tập, làm việc và giải trí.", {"warranty_months": 12, "usage": "work"}))

    appliances = [
        ("DYSON-V12", "Máy Hút Bụi Dyson V12 Detect Slim", "Dyson", 16990000, "dyson vacuum cleaner"),
        ("PHILIPS-AIRFRYER", "Nồi Chiên Không Dầu Philips HD9252", "Philips", 3290000, "philips air fryer"),
        ("PANASONIC-RICE", "Nồi Cơm Điện Panasonic 1.8L", "Panasonic", 1890000, "rice cooker"),
        ("TOSHIBA-FRIDGE", "Tủ Lạnh Toshiba Inverter 233L", "Toshiba", 6790000, "refrigerator"),
        ("LG-WASHER", "Máy Giặt LG Inverter 9kg", "LG", 8490000, "washing machine"),
        ("SAMSUNG-TV55", "Smart TV Samsung 55 inch 4K", "Samsung", 11990000, "samsung smart tv"),
        ("XIAOMI-VACUUM", "Robot Hút Bụi Xiaomi Vacuum S10", "Xiaomi", 5990000, "robot vacuum"),
        ("SUNHOUSE-BLENDER", "Máy Xay Sinh Tố Sunhouse 1.5L", "Sunhouse", 690000, "blender"),
        ("LOCK-KETTLE", "Ấm Đun Siêu Tốc Lock&Lock 1.7L", "Lock&Lock", 590000, "electric kettle"),
        ("SHARP-MICROWAVE", "Lò Vi Sóng Sharp 23L", "Sharp", 1990000, "microwave oven"),
        ("TEFAL-IRON", "Bàn Ủi Hơi Nước Tefal", "Tefal", 1190000, "steam iron"),
        ("DAIKIN-AC", "Máy Lạnh Daikin Inverter 1HP", "Daikin", 9290000, "air conditioner"),
        ("KANGAROO-WATER", "Máy Lọc Nước Kangaroo RO", "Kangaroo", 4990000, "water purifier"),
        ("ELECTROLUX-DRYER", "Máy Sấy Electrolux 8kg", "Electrolux", 9990000, "clothes dryer"),
        ("LOCK-PANSET", "Bộ Nồi Chảo Chống Dính Lock&Lock", "Lock&Lock", 1290000, "nonstick cookware set"),
        ("ECO-DISHWASHER", "Máy Rửa Chén Electrolux 8 Bộ", "Electrolux", 8990000, "dishwasher kitchen appliance"),
        ("MIDEA-FAN", "Quạt Điều Hòa Midea AC120", "Midea", 3190000, "air cooler fan"),
        ("PHILIPS-COFFEE", "Máy Pha Cà Phê Philips 2200 Series", "Philips", 10990000, "espresso coffee machine"),
        ("CUCKOO-RICE", "Nồi Cơm Áp Suất Cuckoo 1.8L", "Cuckoo", 4990000, "pressure rice cooker"),
        ("BLUEAIR-PURIFIER", "Máy Lọc Không Khí Blueair 3210", "Blueair", 3990000, "air purifier"),
    ]
    for sku, name, brand, price, query in appliances:
        products.append(product(sku, name, "dien-gia-dung", "electronics", brand, price, query, f"{name} chính hãng, tiết kiệm điện, phù hợp gia đình.", {"warranty_months": 12, "home_appliance": True}))

    fashion_items = [
        ("NIKE-AIRMAX", "Giày Nike Air Max Nam Nữ", "Nike", 2890000, "nike air max shoes"),
        ("ADIDAS-SAMBA", "Giày Adidas Samba OG", "Adidas", 2590000, "adidas samba shoes"),
        ("UNIQLO-TEE", "Áo Thun Uniqlo U Cotton", "Uniqlo", 390000, "plain cotton t shirt"),
        ("ZARA-DRESS", "Đầm Zara Midi Dáng A", "Zara", 1290000, "midi dress"),
        ("LEVIS-501", "Quần Jeans Levi's 501 Original", "Levi's", 1890000, "levis jeans"),
        ("MLB-CAP", "Nón MLB New York Yankees", "MLB", 890000, "baseball cap"),
        ("CHARLES-BAG", "Túi Charles & Keith Crossbody", "Charles & Keith", 1590000, "crossbody bag"),
        ("CASIO-A168", "Đồng Hồ Casio A168 Vintage", "Casio", 790000, "casio watch"),
        ("PUMA-HOODIE", "Áo Hoodie Puma Essentials", "Puma", 990000, "hoodie fashion"),
        ("CONVERSE-CLASSIC", "Giày Converse Chuck Taylor Classic", "Converse", 1390000, "converse sneakers"),
        ("HNM-SHIRT", "Áo Sơ Mi H&M Oxford", "H&M", 590000, "oxford shirt"),
        ("MANGO-BLAZER", "Áo Blazer Mango Công Sở", "Mango", 1690000, "women blazer"),
        ("FILA-SKIRT", "Chân Váy Tennis Fila", "Fila", 790000, "tennis skirt"),
        ("CROCS-CLOG", "Dép Crocs Classic Clog", "Crocs", 1190000, "crocs clogs"),
        ("RAYBAN-WAYFARER", "Kính Ray-Ban Wayfarer", "Ray-Ban", 3290000, "rayban sunglasses"),
        ("MUJI-TOTE", "Túi Tote Canvas Muji", "Muji", 390000, "canvas tote bag"),
        ("GU-SHORTS", "Quần Short GU Linen", "GU", 490000, "linen shorts"),
        ("DECATHLON-JACKET", "Áo Khoác Chạy Bộ Decathlon", "Decathlon", 690000, "running jacket"),
        ("SKECHERS-WALK", "Giày Skechers Go Walk", "Skechers", 1690000, "walking shoes"),
        ("PEDRO-WALLET", "Ví Da Pedro Nam", "Pedro", 990000, "leather wallet"),
        ("COTTONON-JOGGER", "Quần Jogger Cotton On", "Cotton On", 590000, "jogger pants"),
        ("ELISE-BLOUSE", "Áo Blouse Elise Nữ", "Elise", 790000, "women blouse"),
        ("ANPHUOC-POLO", "Áo Polo An Phước Nam", "An Phước", 890000, "men polo shirt"),
        ("JUNO-HEELS", "Giày Cao Gót Juno", "Juno", 690000, "women high heels"),
        ("OWEN-TROUSER", "Quần Tây Owen Slim Fit", "Owen", 990000, "men trousers"),
    ]
    for sku, name, brand, price, query in fashion_items:
        products.append(product(sku, name, "thoi-trang", "fashion", brand, price, query, f"{name} chất lượng tốt, dễ phối đồ, phù hợp sử dụng hằng ngày.", {"size": "M", "material": "Premium fabric"}))

    books = [
        ("CLEAN-CODE-BOOK", "Sách Clean Code - Robert C. Martin", "Prentice Hall", 620000, "clean code book"),
        ("REFACTORING-FOWLER", "Sách Refactoring - Martin Fowler", "Addison-Wesley", 720000, "refactoring book"),
        ("SYSTEM-DESIGN", "Sách System Design Interview", "ByteByteGo", 650000, "system design book"),
        ("K8S-ACTION", "Sách Kubernetes in Action", "Manning", 780000, "kubernetes book"),
        ("PYTHON-CRASH", "Sách Python Crash Course", "No Starch Press", 580000, "python programming book"),
        ("DEEP-LEARNING", "Sách Deep Learning with Python", "Manning", 690000, "deep learning book"),
        ("AI-MODERN", "Sách Artificial Intelligence A Modern Approach", "Pearson", 990000, "artificial intelligence book"),
        ("DESIGN-PATTERNS", "Sách Design Patterns GoF", "Addison-Wesley", 730000, "design patterns book"),
        ("MICROSERVICES-NEWMAN", "Sách Building Microservices - Sam Newman", "O'Reilly", 820000, "microservices book"),
        ("DEVOPS-HANDBOOK", "Sách The DevOps Handbook", "IT Revolution", 640000, "devops handbook"),
        ("ATOMIC-HABITS", "Sách Atomic Habits", "Penguin", 220000, "atomic habits book"),
        ("THINKING-FAST", "Sách Thinking, Fast and Slow", "FSG", 260000, "psychology book"),
        ("RICH-DAD", "Sách Rich Dad Poor Dad", "Plata", 180000, "finance book"),
        ("START-WHY", "Sách Start With Why", "Portfolio", 210000, "business book"),
        ("LEAN-STARTUP", "Sách The Lean Startup", "Crown", 240000, "startup book"),
        ("ZERO-ONE", "Sách Zero to One", "Crown Business", 230000, "startup business book"),
        ("NHA-GIA-KIM", "Sách Nhà Giả Kim", "NXB Văn Học", 99000, "novel book"),
        ("DAC-NHAN-TAM", "Sách Đắc Nhân Tâm", "NXB Tổng Hợp", 86000, "self help book"),
        ("TOI-TAI-GIOI", "Sách Tôi Tài Giỏi Bạn Cũng Thế", "NXB Trẻ", 125000, "study skills book"),
        ("MUON-KIEP", "Sách Muôn Kiếp Nhân Sinh", "First News", 168000, "vietnamese book"),
        ("BLUE-OCEAN", "Sách Blue Ocean Strategy", "Harvard", 290000, "strategy book"),
        ("GOOD-GREAT", "Sách Good to Great", "HarperBusiness", 260000, "business management book"),
        ("PRAGMATIC-PROG", "Sách The Pragmatic Programmer", "Addison-Wesley", 680000, "programming book"),
        ("DATABASE-DESIGN", "Sách Database Design for Mere Mortals", "Addison-Wesley", 610000, "database design book"),
        ("SOFTWARE-ARCH", "Sách Software Architecture in Practice", "SEI", 760000, "software architecture book"),
    ]
    for sku, name, brand, price, query in books:
        products.append(product(sku, name, "sach-do-choi", "book", brand, price, query, f"{name} phù hợp đọc, học tập và phát triển kỹ năng.", {"language": "Vietnamese/English", "format": "paperback"}))

    if len(products) != 100:
        raise RuntimeError(f"Expected 100 products, got {len(products)}")
    return products


def build_graph_payload(users, customer_profiles, products, product_ids):
    customers = [u for u in users if u["role"] == "customer"]
    graph_users = [
        {
            "customer_id": customer_profiles[user["email"]]["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "segment": user.get("segment", ""),
        }
        for user in customers
        if user["email"] in customer_profiles
    ]
    graph_products = [
        {
            "product_id": product_ids[item["sku"]]["product_id"],
            "sku": item["sku"],
            "name": item["name"],
            "product_type": item["product_type"],
            "brand": item["brand"],
            "price": item["price"],
            "search_text": item["search_text"],
        }
        for item in products
    ]

    event_types = ["viewed", "added_to_cart", "purchased", "wishlisted"]
    interactions = []
    for index, user in enumerate(graph_users):
        preferred_type = ["electronics", "book", "fashion", "electronics", "fashion"][index % 5]
        candidates = [p for p in products if p["product_type"] == preferred_type]
        for offset in range(5):
            item = candidates[(index * 3 + offset) % len(candidates)]
            interactions.append(
                {
                    "customer_id": user["customer_id"],
                    "sku": item["sku"],
                    "event_type": event_types[offset % len(event_types)],
                    "weight": [1.0, 1.6, 2.4, 1.3][offset % 4],
                    "timestamp": f"2026-06-12T{8 + (offset % 10):02d}:00:00+07:00",
                }
            )

    similarities = []
    seen_similarity_pairs = set()
    for index, item in enumerate(products):
        same_type = [p for p in products if p["product_type"] == item["product_type"] and p["sku"] != item["sku"]]
        same_brand = [p for p in products if p["brand"] == item["brand"] and p["sku"] != item["sku"]]
        targets = []
        if same_brand:
            targets.extend(same_brand[:1])
        targets.extend(same_type[index % len(same_type):(index % len(same_type)) + 3])
        for target in targets:
            if item["sku"] == target["sku"]:
                continue
            pair = (item["sku"], target["sku"])
            if pair in seen_similarity_pairs:
                continue
            seen_similarity_pairs.add(pair)
            similarities.append(
                {
                    "from_sku": item["sku"],
                    "to_sku": target["sku"],
                    "score": round(0.55 + (0.4 if item["brand"] == target["brand"] else 0.0) + RANDOM.random() * 0.15, 2),
                    "reason": f"Cùng nhóm {item['product_type']} và phù hợp hành vi mua sắm tương tự",
                }
            )
            if len(similarities) >= 200:
                break
        if len(similarities) >= 200:
            break

    return {
        "users": graph_users,
        "products": graph_products,
        "interactions": interactions,
        "similarities": similarities[:200],
    }


def py_json(value):
    return json.dumps(value, ensure_ascii=False)


def main():
    users = build_users()
    products = build_products()

    identity_code = f"""
import json
from accounts.models import User

users = json.loads(r'''{py_json(users)}''')
created_users = {{}}
for item in users:
    user = User.objects.filter(email=item["email"]).first()
    if not user:
        if item.get("is_superuser"):
            user = User.objects.create_superuser(email=item["email"], password=item["password"], full_name=item["full_name"])
            user.role = item["role"]
            user.save(update_fields=["role"])
        else:
            user = User.objects.create_user(
                email=item["email"],
                password=item["password"],
                full_name=item["full_name"],
                role=item["role"],
                is_staff=item.get("is_staff", False),
            )
        print(f"Created user: {{item['email']}}")
    created_users[item["email"]] = str(user.id)

print("USER_IDS_START")
print(json.dumps(created_users, ensure_ascii=False))
print("USER_IDS_END")
"""
    user_ids = marker_json(run_django_code("identity-service", identity_code), "USER_IDS")

    customer_users = [u for u in users if u["role"] == "customer"]
    customer_code = f"""
import json
from customers.models import CustomerProfile, Address

users = json.loads(r'''{py_json(customer_users)}''')
user_ids = json.loads(r'''{py_json(user_ids)}''')
profiles = {{}}
for index, item in enumerate(users, start=1):
    profile, created = CustomerProfile.objects.update_or_create(
        user_id=user_ids[item["email"]],
        defaults={{
            "email": item["email"],
            "full_name": item["full_name"],
            "phone": f"09{{index:08d}}",
            "status": "active",
            "preferences": {{
                "segment": item.get("segment", ""),
                "category_preference": ["electronics", "book", "fashion", "home"][index % 4],
                "budget": ["low", "medium", "premium"][index % 3],
            }},
        }},
    )
    Address.objects.update_or_create(
        customer=profile,
        is_default=True,
        defaults={{
            "label": "Nhà riêng",
            "recipient_name": item["full_name"],
            "phone": f"09{{index:08d}}",
            "line1": f"{{index}} Đường Nguyễn Trãi",
            "city": ["Hồ Chí Minh", "Hà Nội", "Đà Nẵng", "Cần Thơ"][index % 4],
            "country": "VN",
        }},
    )
    profiles[item["email"]] = {{"id": str(profile.id), "user_id": str(profile.user_id), "preferences": profile.preferences}}

print("CUSTOMER_PROFILES_START")
print(json.dumps(profiles, ensure_ascii=False))
print("CUSTOMER_PROFILES_END")
"""
    customer_profiles = marker_json(run_django_code("customer-service", customer_code), "CUSTOMER_PROFILES")

    categories_data = [
        {"name": "Điện thoại & Phụ kiện", "slug": "dien-thoai-phu-kien"},
        {"name": "Thời trang", "slug": "thoi-trang"},
        {"name": "Sách & Đồ chơi", "slug": "sach-do-choi"},
        {"name": "Điện gia dụng", "slug": "dien-gia-dung"},
    ]
    catalog_code = f"""
import json
from catalog.models import Category, Product, ProductVariant

categories_data = json.loads(r'''{py_json(categories_data)}''')
products_data = json.loads(r'''{py_json(products)}''')
cats = {{}}
for item in categories_data:
    category, _ = Category.objects.update_or_create(
        slug=item["slug"],
        defaults={{"name": item["name"], "is_active": True}},
    )
    cats[item["slug"]] = category

product_ids = {{}}
for item in products_data:
    product, _ = Product.objects.update_or_create(
        sku=item["sku"],
        defaults={{
            "name": item["name"],
            "slug": item["slug"],
            "category": cats[item["category_slug"]],
            "description": item["description"],
            "brand": item["brand"],
            "product_type": item["product_type"],
            "status": item["status"],
            "attributes": item["attributes"],
            "image_urls": item["image_urls"],
        }},
    )
    ProductVariant.objects.update_or_create(
        sku=item["sku"],
        defaults={{"product": product, "name": item["name"], "attributes": item["attributes"], "is_active": True}},
    )
    product_ids[item["sku"]] = {{"product_id": str(product.id), "category_id": str(product.category_id)}}

print("PRODUCTS_START")
print(json.dumps(product_ids, ensure_ascii=False))
print("PRODUCTS_END")
"""
    product_ids = marker_json(run_django_code("catalog-service", catalog_code), "PRODUCTS")

    pricing_code = f"""
import json
from decimal import Decimal
from django.utils import timezone
from pricing.models import PriceBook, ProductPrice, PromotionCampaign, Coupon

products_data = json.loads(r'''{py_json(products)}''')
product_ids = json.loads(r'''{py_json(product_ids)}''')
price_book, _ = PriceBook.objects.update_or_create(
    code="DEFAULT_PB",
    defaults={{"name": "Bảng giá mặc định", "currency": "VND", "is_active": True}},
)
for item in products_data:
    ProductPrice.objects.update_or_create(
        price_book=price_book,
        sku=item["sku"],
        defaults={{
            "product_id": product_ids[item["sku"]]["product_id"],
            "amount": Decimal(str(item["price"])),
            "compare_at_amount": Decimal(str(item["compare_at"])),
            "starts_at": timezone.now(),
            "is_active": True,
        }},
    )
campaign, _ = PromotionCampaign.objects.update_or_create(
    code="FREESHIPXTRA",
    defaults={{"name": "Freeship Xtra Toàn Quốc", "discount_percent": Decimal("10.00"), "is_active": True, "starts_at": timezone.now()}},
)
Coupon.objects.update_or_create(code="SHOPEE10", defaults={{"campaign": campaign, "max_redemptions": 1000, "is_active": True}})
print("PRICING_SEEDED")
"""
    run_django_code("pricing-service", pricing_code)

    inventory_code = f"""
import json
from inventory.models import Warehouse, StockItem

products_data = json.loads(r'''{py_json(products)}''')
product_ids = json.loads(r'''{py_json(product_ids)}''')
warehouse, _ = Warehouse.objects.update_or_create(
    code="HN_MAIN",
    defaults={{"name": "Kho chính Hà Nội", "city": "Hà Nội", "country": "VN", "is_active": True}},
)
for item in products_data:
    StockItem.objects.update_or_create(
        warehouse=warehouse,
        sku=item["sku"],
        defaults={{
            "product_id": product_ids[item["sku"]]["product_id"],
            "quantity_on_hand": item["quantity"],
            "quantity_reserved": 0,
        }},
    )
print("INVENTORY_SEEDED")
"""
    run_django_code("inventory-service", inventory_code)

    search_code = f"""
import json
from decimal import Decimal
from search.models import SearchProductDocument

products_data = json.loads(r'''{py_json(products)}''')
product_ids = json.loads(r'''{py_json(product_ids)}''')
for item in products_data:
    SearchProductDocument.objects.update_or_create(
        product_id=product_ids[item["sku"]]["product_id"],
        defaults={{
            "sku": item["sku"],
            "name": item["name"],
            "description": item["description"],
            "product_type": item["product_type"],
            "category_id": product_ids[item["sku"]]["category_id"],
            "brand": item["brand"],
            "status": item["status"],
            "price_amount": Decimal(str(item["price"])),
            "currency": "VND",
            "available_quantity": item["quantity"],
            "rating_average": Decimal(str(item["rating"])),
            "attributes": item["attributes"],
            "image_urls": item["image_urls"],
            "search_text": item["search_text"],
        }},
    )
print("SEARCH_SEEDED")
"""
    run_django_code("search-service", search_code)

    graph_payload = build_graph_payload(users, customer_profiles, products, product_ids)
    recommendation_code = f"""
import json
from decimal import Decimal
from recommendations.models import ProductInteraction, Recommendation
from recommendations.graph import Neo4jRecommender

payload = json.loads(r'''{py_json(graph_payload)}''')
products_by_sku = {{item["sku"]: item for item in payload["products"]}}

for item in payload["interactions"]:
    product = products_by_sku[item["sku"]]
    ProductInteraction.objects.get_or_create(
        customer_id=item["customer_id"],
        product_id=product["product_id"],
        sku=item["sku"],
        event_type=item["event_type"],
        defaults={{"metadata": {{"seeded": True, "weight": item["weight"]}}}},
    )

for user in payload["users"]:
    ranked = [edge for edge in payload["similarities"] if edge["from_sku"] in {{i["sku"] for i in payload["interactions"] if i["customer_id"] == user["customer_id"]}}]
    for index, edge in enumerate(ranked[:8], start=1):
        product = products_by_sku[edge["to_sku"]]
        Recommendation.objects.update_or_create(
            customer_id=user["customer_id"],
            product_id=product["product_id"],
            defaults={{"sku": product["sku"], "score": Decimal(str(max(0.1, 1 - index * 0.07))), "reason": edge["reason"]}},
        )

recommender = Neo4jRecommender()
with recommender.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
summary = recommender.seed(payload)
print("NEO4J_GRAPH_START")
print(json.dumps(summary, ensure_ascii=False))
print("NEO4J_GRAPH_END")
print("RECOMMENDATION_SEEDED")
"""
    graph_summary = marker_json(run_django_code("recommendation-service", recommendation_code), "NEO4J_GRAPH")

    print("=== SEEDING COMPLETED SUCCESSFULLY ===")
    print(f"Users: {len(users)} total, {len(customer_users)} customers")
    print(f"Products: {len(products)}")
    print(f"Neo4j summary: {graph_summary}")


if __name__ == "__main__":
    main()
