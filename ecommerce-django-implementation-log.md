# Ecommerce Django Microservice Implementation Log

Ngay 2026-06-11, project Django microservice da duoc scaffold theo phan tich DDD trong `ecommerce-ddd-analysis.md`.

## 1. Kien truc tong quan

Project duoc thiet ke theo monorepo nhung moi bounded context la mot Django service rieng:

- Moi service co `manage.py`, `config/settings.py`, `config/urls.py`, `config/wsgi.py`, `config/asgi.py`.
- Moi service co app domain rieng va migration rieng.
- Moi service chay container rieng.
- Moi service dung PostgreSQL database rieng.
- Khong co foreign key cross-service. Cac tham chieu lien service dung UUID snapshot nhu `customer_id`, `product_id`, `order_id`, `payment_id`.
- Giao tiep service-to-service qua REST bang `ecommerce_common.clients.ServiceClient`.
- Authentication dung JWT. `identity-service` phat hanh token, cac service con lai verify token offline bang shared `JWT_SIGNING_KEY`.

Thu muc chung:

```text
services/shared/ecommerce_common/
```

Package nay chi chua cac thanh phan ha tang dung chung:

- Base Django settings.
- JWT authentication cho service.
- Base UUID/timestamp model.
- REST service client.
- Common permissions.
- Health check view.

## 2. Services da tao

| Service | Port host | Database | Context |
| --- | ---: | --- | --- |
| identity-service | 8001 | identity_db | Identity & Access |
| customer-service | 8002 | customer_db | Customer |
| catalog-service | 8003 | catalog_db | Catalog |
| inventory-service | 8004 | inventory_db | Inventory |
| pricing-service | 8005 | pricing_db | Pricing & Promotion |
| cart-service | 8006 | cart_db | Cart |
| order-service | 8007 | order_db | Order |
| payment-service | 8008 | payment_db | Payment |
| shipping-service | 8009 | shipping_db | Shipping |
| search-service | 8010 | search_db | Search |
| recommendation-service | 8011 | recommendation_db | Recommendation |
| review-service | 8012 | review_db | Review & Rating |
| notification-service | 8013 | notification_db | Notification |
| return-refund-service | 8014 | return_refund_db | Return & Refund |
| analytics-service | 8015 | analytics_db | Analytics & Reporting |
| admin-backoffice-service | 8016 | admin_backoffice_db | Admin Backoffice & Audit |
| frontend | 3000 | none | React SPA |

Moi service co endpoint health check:

```text
GET /health/
```

## 3. Authentication va JWT

`identity-service` co custom user model:

- `id`: UUID primary key.
- `email`: unique login field.
- `full_name`.
- `phone`.
- `role`: `admin`, `staff`, `customer`.
- `is_active`, `is_staff`, `is_superuser`.

Auth endpoints:

```text
POST /api/v1/auth/register/
POST /api/v1/auth/login/
POST /api/v1/auth/refresh/
GET  /api/v1/auth/me/
PATCH /api/v1/auth/me/
```

JWT access token co them claims:

```json
{
  "user_id": "...",
  "email": "user@example.com",
  "role": "customer",
  "full_name": "Customer Name"
}
```

Moi service con lai dung `ServiceJWTAuthentication` de verify bearer token bang `JWT_SIGNING_KEY`, khong query database cua identity service.

## 4. Thiet ke database theo context

Tat ca service dung PostgreSQL va da co migration `0001_initial.py`.

Schema chinh:

- Identity: `users`.
- Customer: `customer_profiles`, `customer_addresses`, `wishlist_items`.
- Catalog: `categories`, `products`, `product_variants`.
- Inventory: `warehouses`, `stock_items`, `stock_reservations`.
- Pricing: `price_books`, `product_prices`, `promotion_campaigns`, `coupons`.
- Cart: `carts`, `cart_items`.
- Order: `orders`, `order_lines`, `order_status_history`.
- Payment: `payments`, `payment_transactions`, `refunds`.
- Shipping: `carriers`, `shipments`, `delivery_events`.
- Search: `search_product_documents`.
- Recommendation: `product_interactions`, `recommendations`.
- Review: `product_reviews`.
- Notification: `notification_templates`, `notifications`.
- Return/Refund: `return_requests`, `return_items`, `refund_requests`.
- Analytics: `analytics_events`, `daily_sales_metrics`.
- Admin Backoffice: `backoffice_work_items`, `audit_logs`.

Nhung rule quan trong da dua vao schema/model:

- UUID primary key cho aggregate.
- Unique constraint cho idempotency key o Order, Payment, Refund, Return.
- Unique SKU o Catalog.
- Unique stock theo warehouse + SKU.
- Check constraint dam bao reserved stock khong vuot on-hand stock.
- Check constraint rating trong khoang 1..5.
- Index cho cac truy van chinh nhu customer/status, SKU, order_id, idempotency_key.

## 5. API va flow chinh

### Catalog

```text
/api/v1/categories/
/api/v1/products/
/api/v1/variants/
```

Product ho tro `product_type`: `book`, `electronics`, `fashion`, va `attributes` JSON de mo rong theo domain.

### Inventory

```text
/api/v1/warehouses/
/api/v1/stock-items/
/api/v1/reservations/
POST /api/v1/stock/reserve/
```

Reserve stock dung transaction va `select_for_update()` de tranh overselling.

### Pricing

```text
/api/v1/price-books/
/api/v1/prices/
/api/v1/promotions/
/api/v1/coupons/
POST /api/v1/quote/
```

Quote endpoint tinh subtotal, discount, total va tra snapshot gia cho checkout.

### Cart Checkout

```text
POST /api/v1/carts/{cart_id}/checkout/
```

Checkout hien tai goi REST theo thu tu:

1. `pricing-service` de quote gia.
2. `order-service` de tao order snapshot.
3. `inventory-service` de reserve stock cho tung SKU.
4. Cap nhat cart sang `checked_out`.

### Order

```text
/api/v1/orders/
POST /api/v1/orders/{id}/mark-paid/
POST /api/v1/orders/{id}/confirm/
POST /api/v1/orders/{id}/cancel/
POST /api/v1/orders/{id}/ship/
POST /api/v1/orders/{id}/complete/
```

Order co state transition trong aggregate method `transition_to()`.

### Payment

```text
/api/v1/payments/
/api/v1/refunds/
POST /api/v1/payments/{id}/mark-succeeded/
POST /api/v1/payments/{id}/mark-failed/
```

Payment dung idempotency key va co transaction log theo provider transaction id.

### Shipping

```text
/api/v1/carriers/
/api/v1/shipments/
POST /api/v1/shipments/{id}/update-status/
```

Shipping luu shipment snapshot va delivery event rieng.

## 6. Frontend

Frontend duoc them tai:

```text
frontend/
```

Stack:

- React 18.
- TypeScript.
- Vite.
- lucide-react cho icon trong controls.
- Nginx de serve static build trong container.

Man hinh chinh da duoc nang cap thanh ecommerce web day du hon, khong phai landing page. UI hien co:

- Login/register voi `identity-service`.
- Storefront: catalog, search, filter theo product type, gia, ton kho, add to cart, wishlist.
- Customer account: sync customer profile, luu address, wishlist, recommendations, notifications.
- Cart va checkout: cap nhat so luong, quote cart qua pricing service, checkout qua cart/order/inventory flow.
- Orders: xem order lines, mock payment, review san pham, tao return request.
- Shipping workflow cho admin/staff: tao carrier va shipment.
- Backoffice: tao category, product, stock, price book, price, notification, analytics event, work item.
- Role-aware controls: cac tac vu van hanh yeu cau `admin` hoac `staff`.

Frontend API base URL duoc cau hinh qua build args/env:

```text
VITE_IDENTITY_API_URL=http://localhost:8001
VITE_CUSTOMER_API_URL=http://localhost:8002
VITE_CATALOG_API_URL=http://localhost:8003
VITE_INVENTORY_API_URL=http://localhost:8004
VITE_PRICING_API_URL=http://localhost:8005
VITE_CART_API_URL=http://localhost:8006
VITE_ORDER_API_URL=http://localhost:8007
VITE_PAYMENT_API_URL=http://localhost:8008
VITE_SHIPPING_API_URL=http://localhost:8009
VITE_SEARCH_API_URL=http://localhost:8010
VITE_RECOMMENDATION_API_URL=http://localhost:8011
VITE_REVIEW_API_URL=http://localhost:8012
VITE_NOTIFICATION_API_URL=http://localhost:8013
VITE_RETURN_REFUND_API_URL=http://localhost:8014
VITE_ANALYTICS_API_URL=http://localhost:8015
VITE_BACKOFFICE_API_URL=http://localhost:8016
```

De browser goi API khac port, backend da them:

```text
django-cors-headers
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## 7. Containerization

File da tao:

```text
docker/django-service.Dockerfile
docker/frontend.Dockerfile
docker/entrypoint.sh
docker-compose.yml
.dockerignore
.env.example
requirements.txt
frontend/
```

Dockerfile dung build arg `SERVICE_DIR` de build tung service:

```text
ARG SERVICE_DIR
COPY services/shared /app/shared
COPY ${SERVICE_DIR} /app
```

Entrypoint tu dong chay:

```text
python manage.py migrate --noinput
```

Sau do start Gunicorn:

```text
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60
```

Chay toan he thong:

```bash
docker compose up --build
```

Chay rieng frontend da build:

```bash
docker compose up -d --no-deps frontend
```

Scale rieng mot service:

```bash
docker compose up --scale catalog-service=3
```

Luu y: neu scale service co expose port truc tiep ra host, can bo mapping port co dinh hoac dat reverse proxy/load balancer phia truoc.

## 8. Ket qua kiem tra

Da chay:

```text
docker compose config --quiet
```

Ket qua: compose config hop le.

Canh bao Docker hien tai:

```text
WARNING: Error loading config file: open C:\Users\sivizstepp\.docker\config.json: Access is denied.
```

Canh bao nay den tu quyen doc Docker config tren may host, khong phai loi `docker-compose.yml`.

Da kiem tra moi service co migration `0001_initial.py`.

Da build frontend:

```text
docker compose build frontend
```

Ket qua moi nhat: `tsc -b && vite build` thanh cong trong Docker sau khi nang cap thanh ecommerce web day du hon.

Da start frontend:

```text
docker compose up -d --no-deps frontend
```

Frontend health check:

```text
GET http://localhost:3000/health -> ok
```

Frontend URL:

```text
http://localhost:3000
```

Khong chay duoc Django `manage.py check` tren host vi:

```text
python.exe failed to run: A specified logon session does not exist.
py: command not found
```

Can chay lai check ben trong container sau khi Docker build thanh cong:

```bash
docker compose run --rm identity-service python manage.py check
docker compose run --rm catalog-service python manage.py check
docker compose run --rm order-service python manage.py check
```

## 9. Viec nen lam tiep truoc production

- Them API Gateway hoac reverse proxy thay vi expose tat ca service ra host.
- Them frontend route guard chi tiet theo role.
- Them runtime config injection cho frontend neu can deploy cung mot image tren nhieu moi truong.
- Tach secret that su qua secret manager, khong dung default trong compose.
- Them service-to-service authentication rieng, khong chi forward customer JWT.
- Them OpenAPI schema cho tung service.
- Them test suite cho aggregate rule, serializer va checkout flow.
- Them async message broker cho event-driven flow: outbox pattern, retry, dead-letter queue.
- Hoan thien Saga/Process Manager cho checkout compensation khi order tao thanh cong nhung reserve stock that bai.
- Them observability: structured logging, trace id, metrics, health/readiness checks.
- Them CI pipeline chay lint, test, migration check va docker build.
