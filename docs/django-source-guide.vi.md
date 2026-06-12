# Huong dan doc ma nguon Django ecommerce

Tai lieu nay giai thich backend Django trong repo theo cach de doc cho nguoi moi hoc code. Muc tieu la giup ban biet:

- He thong dang dung cong nghe nao.
- Moi thu muc/file Django co vai tro gi.
- Mot request di qua Django nhu the nao.
- Cac service giao tiep voi nhau ra sao.
- Luong mua hang, thanh toan, giao hang van hanh nhu the nao.

## 1. Tong quan he thong

Repo nay la mot ecommerce microservice monorepo. Nghia la tat ca ma nguon nam chung trong mot repo, nhung backend duoc tach thanh nhieu Django project nho.

Moi service nam trong `services/<ten_service>/` va co:

- `manage.py`: file chay lenh Django, vi du `python manage.py migrate`.
- `config/settings.py`: cau hinh Django cua service do.
- `config/urls.py`: noi khai bao URL goc cua service.
- App domain rieng, vi du `catalog`, `orders`, `payments`.
- Database PostgreSQL rieng khi chay bang Docker Compose.

Thu muc dung chung la:

```text
services/shared/ecommerce_common/
```

Package nay chua cac thanh phan ha tang dung lai o nhieu service:

- Cau hinh Django chung.
- Authentication bang JWT.
- Permission dung chung.
- Base model co UUID va timestamp.
- HTTP client de service nay goi service khac.
- Health check endpoint.

## 2. Cong nghe duoc su dung

| Nhom | Cong nghe | Vai tro |
| --- | --- | --- |
| Backend | Python 3.12 | Ngon ngu chay cac Django service |
| Web framework | Django 5 | Framework backend chinh |
| API | Django REST Framework | Tao REST API, serializer, viewset |
| Authentication | djangorestframework-simplejwt, PyJWT | Dang nhap va xac thuc JWT |
| Database | PostgreSQL 16 | Luu du lieu rieng cho tung service |
| HTTP noi bo | requests | Service-to-service REST calls |
| Container | Docker, Docker Compose | Chay nhieu service va database cung luc |
| App server | Gunicorn | Chay Django trong container |
| Frontend | React 18, Vite, TypeScript | Giao dien web goi cac API |
| Icons/UI | lucide-react | Icon trong frontend |

## 3. Danh sach service

| Service | Port local | App Django | Database | Chuc nang |
| --- | ---: | --- | --- | --- |
| identity-service | 8001 | `accounts` | `identity_db` | Dang ky, dang nhap, JWT, user |
| customer-service | 8002 | `customers` | `customer_db` | Ho so khach hang, dia chi, wishlist |
| catalog-service | 8003 | `catalog` | `catalog_db` | Danh muc, san pham, bien the san pham |
| inventory-service | 8004 | `inventory` | `inventory_db` | Kho, ton kho, giu hang |
| pricing-service | 8005 | `pricing` | `pricing_db` | Bang gia, gia SKU, coupon, quote |
| cart-service | 8006 | `carts` | `cart_db` | Gio hang va checkout |
| order-service | 8007 | `orders` | `order_db` | Don hang, dong hang, lich su trang thai |
| payment-service | 8008 | `payments` | `payment_db` | Thanh toan, giao dich, refund |
| shipping-service | 8009 | `shipping` | `shipping_db` | Don van chuyen, su kien giao hang |
| search-service | 8010 | `search` | `search_db` | Tai lieu tim kiem san pham |
| recommendation-service | 8011 | `recommendations` | `recommendation_db` | Hanh vi va goi y san pham |
| review-service | 8012 | `reviews` | `review_db` | Danh gia san pham |
| notification-service | 8013 | `notifications` | `notification_db` | Mau thong bao va thong bao |
| return-refund-service | 8014 | `returns` | `return_refund_db` | Yeu cau tra hang va hoan tien |
| analytics-service | 8015 | `analytics` | `analytics_db` | Event va metric doanh thu |
| admin-backoffice-service | 8016 | `backoffice` | `admin_backoffice_db` | Cong viec admin va audit log |
| frontend | 3000 | React app | Khong co | Giao dien web |

Tat ca backend service co endpoint:

```text
GET /health/
```

Endpoint nay tra ve service name va trang thai `ok`.

## 4. Cach Django xu ly mot request

Vi du frontend goi:

```text
GET http://localhost:8003/api/v1/products/
```

Luong xu ly nhu sau:

```text
Browser/Frontend
  -> catalog-service container
  -> config/urls.py
  -> catalog/urls.py
  -> ProductViewSet.list()
  -> Product.objects...
  -> ProductSerializer
  -> JSON response
```

Giai thich tung buoc:

1. Frontend goi API bang `fetch()` trong `frontend/src/api.ts`.
2. Django nhan URL trong `config/urls.py`.
3. `config/urls.py` include app URL, vi du `include("catalog.urls")`.
4. `catalog/urls.py` dung `DefaultRouter` de tao REST endpoint tu `ProductViewSet`.
5. `ProductViewSet` doc database qua Django ORM.
6. `ProductSerializer` bien object Python/Django model thanh JSON.
7. Django REST Framework tra JSON ve frontend.

## 5. Vai tro cac file Django quan trong

Trong moi app, cac file lap lai theo pattern sau:

```text
models.py       -> Dinh nghia bang database.
serializers.py  -> Doi model/input thanh JSON va nguoc lai.
views.py        -> Chua logic xu ly API.
urls.py         -> Noi URL voi view/viewset.
apps.py         -> Khai bao app Django.
migrations/     -> Lich su tao/sua bang database.
```

Trong moi service:

```text
config/settings.py -> Goi cau hinh chung.
config/urls.py     -> Khai bao endpoint goc nhu /health/ va /api/v1/.
config/wsgi.py     -> Entry point cho Gunicorn.
config/asgi.py     -> Entry point ASGI neu can async/websocket sau nay.
```

## 6. Cau hinh chung

Tat ca service goi ham `configure()` trong:

```text
services/shared/ecommerce_common/settings.py
```

Ham nay gan cac cau hinh Django vao `globals()` cua file `config/settings.py`, gom:

- `INSTALLED_APPS`
- `MIDDLEWARE`
- `REST_FRAMEWORK`
- `DATABASES`
- `CORS_ALLOWED_ORIGINS`
- `SERVICE_URLS`
- `JWT_SIGNING_KEY`
- `JWT_ALGORITHM`

`identity-service` la service dac biet:

- Co Django admin.
- Co auth/session cua Django.
- Co model `accounts.User`.
- Dung `rest_framework_simplejwt.authentication.JWTAuthentication`.
- Phat hanh access token va refresh token.

Nhung service con lai:

- Khong luu user local.
- Doc JWT tu header `Authorization: Bearer <token>`.
- Verify token offline bang `ServiceJWTAuthentication`.
- Lay `user_id`, `email`, `role` tu claims trong token.

## 7. Authentication va permission

### Dang ky

Endpoint:

```text
POST /api/v1/auth/register/
```

File lien quan:

```text
services/identity_service/accounts/views.py
services/identity_service/accounts/serializers.py
services/identity_service/accounts/models.py
services/identity_service/accounts/managers.py
```

Luong xu ly:

1. `RegisterView` nhan request.
2. `RegisterSerializer` validate email, full name, password.
3. `UserManager.create_user()` hash password bang `set_password()`.
4. User duoc luu vao bang `users`.

### Dang nhap

Endpoint:

```text
POST /api/v1/auth/login/
```

Luong xu ly:

1. `LoginView` dung `LoginSerializer`.
2. Serializer goi `authenticate()` de kiem tra email/password.
3. SimpleJWT tao token.
4. Code them claims `email`, `role`, `full_name` vao token.
5. Frontend luu token va gui token nay o cac request tiep theo.

### Cac service khac xac thuc

File:

```text
services/shared/ecommerce_common/authentication.py
```

Luong xu ly:

1. Doc header `Authorization`.
2. Kiem tra co dang `Bearer <token>` khong.
3. Decode JWT bang `JWT_SIGNING_KEY`.
4. Tao object `Principal`.
5. Gan object nay vao `request.user`.

Vi vay trong view co the viet:

```python
user = self.request.user
user.id
user.email
user.role
```

Permission dung chung nam trong:

```text
services/shared/ecommerce_common/permissions.py
```

- `IsAdminOrStaff`: chi cho role `admin` hoac `staff`.
- `IsAdmin`: chi cho role `admin`.

## 8. Database va cach lien ket giua service

He thong nay khong tao foreign key giua cac database khac service.

Vi du:

- `orders.customer_id` chi la UUID, khong phai foreign key sang `customer_db`.
- `cart_items.product_id` chi la UUID, khong phai foreign key sang `catalog_db`.
- `payments.order_id` chi la UUID, khong phai foreign key sang `order_db`.

Ly do:

- Moi service tu quan ly database cua minh.
- Service khac chi luu ID hoac snapshot can thiet.
- Giam phu thuoc truc tiep giua database.

Pattern nay rat pho bien trong microservice.

## 9. Cac model quan trong

### Identity

File:

```text
services/identity_service/accounts/models.py
```

Bang `users` luu:

- `id`: UUID.
- `email`: dung de dang nhap.
- `full_name`, `phone`.
- `role`: `admin`, `staff`, `customer`.
- `is_active`, `is_staff`, `is_superuser`.

### Catalog

File:

```text
services/catalog_service/catalog/models.py
```

Bang chinh:

- `categories`: danh muc san pham.
- `products`: san pham goc, co `sku`, `slug`, `status`, `attributes`, `image_urls`.
- `product_variants`: bien the theo SKU rieng.

### Inventory

File:

```text
services/inventory_service/inventory/models.py
```

Bang chinh:

- `warehouses`: kho hang.
- `stock_items`: ton kho theo kho va SKU.
- `stock_reservations`: so luong da giu cho mot order.

`available_quantity` duoc tinh:

```text
quantity_on_hand - quantity_reserved
```

### Pricing

File:

```text
services/pricing_service/pricing/models.py
```

Bang chinh:

- `price_books`: bang gia va tien te.
- `product_prices`: gia cua SKU.
- `promotion_campaigns`: chien dich khuyen mai.
- `coupons`: ma coupon.

### Cart va Order

Cart:

```text
services/cart_service/carts/models.py
```

- `carts`: gio hang.
- `cart_items`: san pham trong gio.

Order:

```text
services/order_service/orders/models.py
```

- `orders`: don hang.
- `order_lines`: dong san pham trong don.
- `order_status_history`: lich su thay doi trang thai.

Trang thai order co thu tu:

```text
pending_payment -> paid -> confirmed -> packed -> shipped -> completed
```

Mot so nhanh khac:

```text
pending_payment -> cancelled
paid -> refunded
completed -> refunded
```

## 10. Luong checkout chinh

Endpoint:

```text
POST /api/v1/carts/{cart_id}/checkout/
```

File:

```text
services/cart_service/carts/views.py
```

Luong xu ly:

```text
Frontend
  -> cart-service checkout
  -> pricing-service quote
  -> order-service create order
  -> inventory-service reserve stock
  -> cart-service mark cart checked_out
  -> Frontend nhan order va quote
```

Chi tiet:

1. `CartViewSet.checkout()` lay cart theo `cart_id`.
2. Kiem tra cart con `active` khong.
3. Kiem tra cart co item khong.
4. Validate input bang `CheckoutSerializer`.
5. Tao list SKU/quantity tu `cart.items`.
6. Goi `pricing-service`:

```text
POST /api/v1/quote/
```

7. Pricing tra ve `subtotal`, `discount_total`, `total`, va gia tung item.
8. Goi `order-service`:

```text
POST /api/v1/orders/
```

9. Order service tao `Order`, `OrderLine`, va `OrderStatusHistory`.
10. Cart service goi `inventory-service` cho tung SKU:

```text
POST /api/v1/stock/reserve/
```

11. Inventory giu hang bang cach tang `quantity_reserved`.
12. Cart duoc cap nhat status thanh `checked_out`.

## 11. Idempotency key la gi?

Mot so request tao du lieu quan trong co field `idempotency_key`, vi du:

- Tao order.
- Tao payment.
- Tao refund.
- Reserve stock.
- Tao return request.

Idempotency giup tranh tao trung du lieu khi user bam lai, frontend retry, hoac network bi loi.

Vi du trong `OrderViewSet.create()`:

1. Neu request co `idempotency_key`.
2. Code tim order cu co key do.
3. Neu da co, tra ve order cu.
4. Neu chua co, tao order moi.
5. Neu database bao trung key do race condition, code doc lai order cu.

## 12. Luong giu hang trong kho

Endpoint:

```text
POST /api/v1/stock/reserve/
```

File:

```text
services/inventory_service/inventory/views.py
```

Logic quan trong:

- Dung `transaction.atomic()` de gom cac thay doi database thanh mot giao dich.
- Dung `select_for_update()` de khoa dong ton kho dang duoc xu ly.
- Kiem tra `available_quantity`.
- Neu du hang, tang `quantity_reserved`.
- Tao `StockReservation`.

Muc dich la tranh overselling, tuc la ban qua so luong ton kho that.

## 13. Luong thanh toan

Endpoint tao payment:

```text
POST /api/v1/payments/
```

Endpoint danh dau thanh cong:

```text
POST /api/v1/payments/{payment_id}/mark-succeeded/
```

File:

```text
services/payment_service/payments/views.py
```

Luong xu ly khi payment thanh cong:

1. Lay payment theo ID.
2. Validate `provider_transaction_id`.
3. Tao `PaymentTransaction` neu chua co.
4. Doi `payment.status` thanh `succeeded`.
5. Goi sang order-service:

```text
POST /api/v1/orders/{order_id}/mark-paid/
```

6. Order service doi trang thai order tu `pending_payment` sang `paid`.

## 14. Luong van chuyen

Endpoint:

```text
POST /api/v1/shipments/{shipment_id}/update-status/
```

File:

```text
services/shipping_service/shipping/views.py
```

Luong xu ly:

1. Cap nhat `shipment.status`.
2. Tao `DeliveryEvent` de luu lich su giao hang.
3. Neu shipment sang `in_transit`, goi order action `ship`.
4. Neu shipment sang `delivered`, goi order action `complete`.

## 15. Search va recommendation

Search service khong truy van truc tiep bang `products`.

No dung bang:

```text
search_product_documents
```

Bang nay la ban copy/snapshot phuc vu tim kiem, gom:

- `product_id`
- `sku`
- `name`
- `description`
- `brand`
- `price_amount`
- `available_quantity`
- `rating_average`
- `search_text`

Endpoint public:

```text
GET /api/v1/products/search/?q=...
```

Recommendation service co:

- `ProductInteraction`: luu hanh vi nhu viewed, added_to_cart, purchased.
- `Recommendation`: luu danh sach san pham duoc goi y cho customer.

Endpoint:

```text
GET /api/v1/recommendations/for-customer/{customer_id}/
```

## 16. Admin, analytics va audit

Admin backoffice:

- `BackofficeWorkItem`: viec can admin/staff xu ly.
- `AuditLog`: lich su ai lam gi, tren context nao, truoc/sau ra sao.

Analytics:

- `AnalyticsEvent`: event thap, vi du user click, order created.
- `DailySalesMetric`: so lieu tong hop theo ngay.

Hai service nay phuc vu van hanh noi bo va bao cao.

## 17. REST endpoint duoc tao nhu the nao?

Nhieu app dung `DefaultRouter` cua Django REST Framework.

Vi du:

```python
router = DefaultRouter()
router.register("products", ProductViewSet)
urlpatterns = router.urls
```

DRF tu tao cac endpoint:

```text
GET    /products/       -> list
POST   /products/       -> create
GET    /products/{id}/   -> retrieve
PUT    /products/{id}/   -> update
PATCH  /products/{id}/   -> partial_update
DELETE /products/{id}/   -> destroy
```

Neu view co `@action`, DRF tao endpoint tuy bien.

Vi du:

```python
@action(detail=True, methods=["post"], url_path="mark-paid")
def mark_paid(...)
```

Se thanh:

```text
POST /orders/{id}/mark-paid/
```

## 18. Frontend goi backend nhu the nao?

File:

```text
frontend/src/api.ts
```

File nay:

- Dinh nghia URL cua tung service.
- Gan token vao header `Authorization`.
- Doi response JSON thanh object TypeScript.
- Gom cac ham API de UI dung, vi du `login`, `listProducts`, `checkout`, `createPayment`.

Vi du checkout tren frontend goi:

```typescript
api.checkout(token, cartId, shippingAddress, couponCode)
```

Ben trong no goi:

```text
POST cart-service /api/v1/carts/{cartId}/checkout/
```

## 19. Cach chay he thong bang Docker

Tu root repo:

```bash
docker compose up --build
```

Docker Compose se:

1. Build frontend.
2. Build image Django dung chung.
3. Tao container cho tung service.
4. Tao PostgreSQL database cho tung service.
5. Chay `python manage.py migrate --noinput` qua `docker/entrypoint.sh`.
6. Chay Django bang Gunicorn.

Sau khi chay:

- Frontend: `http://localhost:3000`
- Identity API: `http://localhost:8001`
- Catalog API: `http://localhost:8003`
- Cart API: `http://localhost:8006`
- Order API: `http://localhost:8007`

## 20. Thu tu nen doc code cho nguoi moi

Nen doc theo thu tu nay:

1. `docker-compose.yml`: biet co bao nhieu service va port nao.
2. `requirements.txt`: biet backend dung thu vien nao.
3. `services/shared/ecommerce_common/settings.py`: biet cau hinh chung.
4. `services/shared/ecommerce_common/authentication.py`: hieu JWT.
5. `services/identity_service/accounts/models.py`: hieu user.
6. `services/identity_service/accounts/serializers.py`: hieu dang ky/dang nhap.
7. `services/catalog_service/catalog/models.py`: hieu san pham.
8. `services/cart_service/carts/views.py`: hieu checkout.
9. `services/order_service/orders/models.py`: hieu trang thai don hang.
10. `services/inventory_service/inventory/views.py`: hieu giu hang.
11. `services/payment_service/payments/views.py`: hieu payment cap nhat order.
12. `services/shipping_service/shipping/views.py`: hieu giao hang cap nhat order.
13. `frontend/src/api.ts`: hieu frontend goi backend nhu the nao.

## 21. Tu khoa can nam

| Tu khoa | Giai thich ngan |
| --- | --- |
| Model | Class Django dai dien cho bang database |
| Serializer | Lop chuyen model/input thanh JSON va validate data |
| View/ViewSet | Noi chua logic xu ly HTTP request |
| Router | Tu tao URL REST cho ViewSet |
| Migration | File ghi lai thay doi schema database |
| JWT | Token dang nhap gui kem moi request |
| Permission | Luat ai duoc goi endpoint nao |
| ORM | Cach Django truy van database bang Python object |
| Transaction | Gom nhieu thao tac database thanh mot khoi an toan |
| Idempotency | Goi lai request nhieu lan van khong tao trung ket qua |
| Snapshot | Luu ban copy du lieu can thiet tai thoi diem do |
| Microservice | Tach he thong thanh nhieu service nho, moi service tu quan ly du lieu |

## 22. Diem can luu y neu nang cap production

Code hien tai phu hop cho demo/scaffold microservice, nhung production nen bo sung:

- Message broker/event bus cho cac luong lien service thay vi chi goi REST dong bo.
- Distributed tracing/logging de debug request qua nhieu service.
- Retry co backoff va circuit breaker cho service-to-service call.
- Permission chi tiet hon cho tung action.
- Test tu dong cho checkout, payment, inventory reservation.
- Dong bo search document va recommendation bang event.
- Quan ly secret that su thay vi default env trong Docker Compose.
- Xu ly rollback/compensation khi checkout tao order thanh cong nhung reserve stock that bai.

