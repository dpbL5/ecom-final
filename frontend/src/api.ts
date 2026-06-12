import type {
  Address,
  AIChatResponse,
  AnalyticsEvent,
  ApiListResponse,
  AuthSession,
  BackofficeWorkItem,
  Carrier,
  Cart,
  CartItem,
  Category,
  CustomerProfile,
  NextBuyRecommendationResponse,
  NotificationMessage,
  Order,
  Payment,
  PriceBook,
  Product,
  ProductPrice,
  ProductReview,
  Quote,
  Recommendation,
  ReturnRequest,
  SearchProductDocument,
  Shipment,
  StockItem,
  Warehouse,
  WishlistItem
} from "./types";

export type ServiceName =
  | "identity"
  | "customer"
  | "catalog"
  | "inventory"
  | "pricing"
  | "cart"
  | "order"
  | "payment"
  | "shipping"
  | "search"
  | "recommendation"
  | "review"
  | "notification"
  | "returnRefund"
  | "analytics"
  | "backoffice";

const defaultServiceUrls: Record<ServiceName, string> = {
  identity: "http://localhost:8001",
  customer: "http://localhost:8002",
  catalog: "http://localhost:8003",
  inventory: "http://localhost:8004",
  pricing: "http://localhost:8005",
  cart: "http://localhost:8006",
  order: "http://localhost:8007",
  payment: "http://localhost:8008",
  shipping: "http://localhost:8009",
  search: "http://localhost:8010",
  recommendation: "http://localhost:8011",
  review: "http://localhost:8012",
  notification: "http://localhost:8013",
  returnRefund: "http://localhost:8014",
  analytics: "http://localhost:8015",
  backoffice: "http://localhost:8016"
};

const env = import.meta.env;

export const serviceUrls: Record<ServiceName, string> = {
  identity: env.VITE_IDENTITY_API_URL || defaultServiceUrls.identity,
  customer: env.VITE_CUSTOMER_API_URL || defaultServiceUrls.customer,
  catalog: env.VITE_CATALOG_API_URL || defaultServiceUrls.catalog,
  inventory: env.VITE_INVENTORY_API_URL || defaultServiceUrls.inventory,
  pricing: env.VITE_PRICING_API_URL || defaultServiceUrls.pricing,
  cart: env.VITE_CART_API_URL || defaultServiceUrls.cart,
  order: env.VITE_ORDER_API_URL || defaultServiceUrls.order,
  payment: env.VITE_PAYMENT_API_URL || defaultServiceUrls.payment,
  shipping: env.VITE_SHIPPING_API_URL || defaultServiceUrls.shipping,
  search: env.VITE_SEARCH_API_URL || defaultServiceUrls.search,
  recommendation: env.VITE_RECOMMENDATION_API_URL || defaultServiceUrls.recommendation,
  review: env.VITE_REVIEW_API_URL || defaultServiceUrls.review,
  notification: env.VITE_NOTIFICATION_API_URL || defaultServiceUrls.notification,
  returnRefund: env.VITE_RETURN_REFUND_API_URL || defaultServiceUrls.returnRefund,
  analytics: env.VITE_ANALYTICS_API_URL || defaultServiceUrls.analytics,
  backoffice: env.VITE_BACKOFFICE_API_URL || defaultServiceUrls.backoffice
};

interface RequestOptions {
  token?: string;
  method?: string;
  body?: unknown;
  query?: Record<string, string | undefined>;
}

function buildQuery(query?: Record<string, string | undefined>) {
  if (!query) {
    return "";
  }
  const entries = Object.entries(query).filter((entry): entry is [string, string] => Boolean(entry[1]));
  if (!entries.length) {
    return "";
  }
  return `?${new URLSearchParams(entries)}`;
}

async function request<T>(service: ServiceName, path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = { Accept: "application/json" };
  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  if (options.token) {
    headers.Authorization = `Bearer ${options.token}`;
  }

  const response = await fetch(`${serviceUrls[service]}${path}${buildQuery(options.query)}`, {
    method: options.method || "GET",
    headers,
    body: options.body === undefined ? undefined : JSON.stringify(options.body)
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `${response.status} ${response.statusText}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

function list<T>(service: ServiceName, path: string, token?: string, query?: Record<string, string | undefined>) {
  return request<T[] | ApiListResponse<T>>(service, path, { token, query }).then((payload) =>
    Array.isArray(payload) ? payload : payload.results
  );
}

function post<T>(service: ServiceName, path: string, token: string | undefined, body: unknown) {
  return request<T>(service, path, { token, method: "POST", body });
}

function patch<T>(service: ServiceName, path: string, token: string | undefined, body: unknown) {
  return request<T>(service, path, { token, method: "PATCH", body });
}

function searchDocumentToProduct(document: SearchProductDocument): Product {
  return {
    id: document.product_id,
    category: document.category_id || "",
    sku: document.sku,
    name: document.name,
    slug: document.sku.toLowerCase(),
    description: document.description,
    brand: document.brand,
    product_type: document.product_type,
    status: document.status,
    attributes: document.attributes || {},
    image_urls: document.image_urls || []
  };
}

export const api = {
  urls: serviceUrls,

  login(email: string, password: string) {
    return post<AuthSession>("identity", "/api/v1/auth/login/", undefined, { email, password });
  },
  register(fullName: string, email: string, password: string) {
    return post("identity", "/api/v1/auth/register/", undefined, { full_name: fullName, email, password });
  },

  listCategories: (token?: string) => list<Category>("catalog", "/api/v1/categories/", token),
  createCategory: (token: string, body: Partial<Category>) => post<Category>("catalog", "/api/v1/categories/", token, body),
  listProducts: (token?: string) => list<Product>("catalog", "/api/v1/products/", token),
  createProduct: (token: string, body: Partial<Product>) => post<Product>("catalog", "/api/v1/products/", token, body),
  searchProducts: (query: string) =>
    list<SearchProductDocument>("search", "/api/v1/products/search/", undefined, { q: query })
      .then((documents) => documents.map(searchDocumentToProduct)),
  upsertSearchDocument: (token: string, body: unknown) => post("search", "/api/v1/documents/", token, body),

  listProfiles: (token: string) => list<CustomerProfile>("customer", "/api/v1/customers/", token),
  createProfile: (token: string, body: Partial<CustomerProfile>) => post<CustomerProfile>("customer", "/api/v1/customers/", token, body),
  updateProfile: (token: string, id: string, body: Partial<CustomerProfile>) =>
    patch<CustomerProfile>("customer", `/api/v1/customers/${id}/`, token, body),
  listAddresses: (token: string) => list<Address>("customer", "/api/v1/addresses/", token),
  createAddress: (token: string, body: Partial<Address>) => post<Address>("customer", "/api/v1/addresses/", token, body),
  listWishlist: (token: string) => list<WishlistItem>("customer", "/api/v1/wishlist/", token),
  addWishlist: (token: string, body: Partial<WishlistItem>) => post<WishlistItem>("customer", "/api/v1/wishlist/", token, body),

  listWarehouses: (token: string) => list<Warehouse>("inventory", "/api/v1/warehouses/", token),
  createWarehouse: (token: string, body: Partial<Warehouse>) => post<Warehouse>("inventory", "/api/v1/warehouses/", token, body),
  listStockItems: (token: string) => list<StockItem>("inventory", "/api/v1/stock-items/", token),
  createStockItem: (token: string, body: Partial<StockItem>) => post<StockItem>("inventory", "/api/v1/stock-items/", token, body),

  listPriceBooks: (token: string) => list<PriceBook>("pricing", "/api/v1/price-books/", token),
  createPriceBook: (token: string, body: Partial<PriceBook>) => post<PriceBook>("pricing", "/api/v1/price-books/", token, body),
  listPrices: (token: string) => list<ProductPrice>("pricing", "/api/v1/prices/", token),
  createPrice: (token: string, body: Partial<ProductPrice>) => post<ProductPrice>("pricing", "/api/v1/prices/", token, body),
  quote: (token: string, items: { sku: string; quantity: number }[], couponCode = "") =>
    post<Quote>("pricing", "/api/v1/quote/", token, { items, coupon_code: couponCode }),

  listCarts: (token: string) => list<Cart>("cart", "/api/v1/carts/", token),
  createCart: (token: string, customerId: string) => post<Cart>("cart", "/api/v1/carts/", token, { customer_id: customerId }),
  addCartItem: (token: string, item: Omit<CartItem, "id">) => post<CartItem>("cart", "/api/v1/cart-items/", token, item),
  updateCartItem: (token: string, itemId: string, body: Partial<CartItem>) =>
    patch<CartItem>("cart", `/api/v1/cart-items/${itemId}/`, token, body),
  checkout: (token: string, cartId: string, shippingAddress: Record<string, string>, couponCode = "") =>
    post<{ order: Order; quote: Quote }>("cart", `/api/v1/carts/${cartId}/checkout/`, token, {
      shipping_address: shippingAddress,
      coupon_code: couponCode,
      idempotency_key: crypto.randomUUID()
    }),

  listOrders: (token: string) => list<Order>("order", "/api/v1/orders/", token),
  transitionOrder: (token: string, orderId: string, action: "confirm" | "cancel" | "ship" | "complete") =>
    post<Order>("order", `/api/v1/orders/${orderId}/${action}/`, token, { note: `Frontend ${action}` }),

  listPayments: (token: string) => list<Payment>("payment", "/api/v1/payments/", token),
  createPayment: (token: string, order: Order) =>
    post<Payment>("payment", "/api/v1/payments/", token, {
      order_id: order.id,
      customer_id: order.customer_id,
      amount: order.grand_total,
      currency: order.currency,
      provider: "mock",
      idempotency_key: `payment:${order.id}`
    }),
  markPaymentSucceeded: (token: string, paymentId: string) =>
    post<Payment>("payment", `/api/v1/payments/${paymentId}/mark-succeeded/`, token, {
      provider_transaction_id: `mock:${paymentId}:${Date.now()}`,
      payload: { source: "frontend" }
    }),

  listCarriers: (token: string) => list<Carrier>("shipping", "/api/v1/carriers/", token),
  createCarrier: (token: string, body: Partial<Carrier>) => post<Carrier>("shipping", "/api/v1/carriers/", token, body),
  listShipments: (token: string) => list<Shipment>("shipping", "/api/v1/shipments/", token),
  createShipment: (token: string, body: Partial<Shipment>) => post<Shipment>("shipping", "/api/v1/shipments/", token, body),
  updateShipmentStatus: (token: string, shipmentId: string, status: string) =>
    post<Shipment>("shipping", `/api/v1/shipments/${shipmentId}/update-status/`, token, { status, description: "Updated from frontend" }),

  listReviews: (token: string) => list<ProductReview>("review", "/api/v1/reviews/", token),
  createReview: (token: string, body: Partial<ProductReview>) => post<ProductReview>("review", "/api/v1/reviews/", token, body),
  approveReview: (token: string, reviewId: string) => post<ProductReview>("review", `/api/v1/reviews/${reviewId}/approve/`, token, {}),

  listRecommendations: (token: string, customerId: string) =>
    request<Recommendation[]>("recommendation", `/api/v1/recommendations/for-customer/${customerId}/`, { token }),
  nextBuyRecommendations: (token: string, customerId: string, persist = false) =>
    request<NextBuyRecommendationResponse>("recommendation", `/api/v1/recommendations/next-buy/${customerId}/`, {
      token,
      query: { persist: persist ? "true" : undefined }
    }),
  trackInteraction: (token: string, body: unknown) => post("recommendation", "/api/v1/interactions/", token, body),
  askAIAdvisor: (token: string | undefined, message: string, customerId?: string) =>
    post<AIChatResponse>("recommendation", "/api/v1/ai/chatbot/", token, { message, customer_id: customerId }),

  listNotifications: (token: string) => list<NotificationMessage>("notification", "/api/v1/notifications/", token),
  createNotification: (token: string, body: Partial<NotificationMessage>) =>
    post<NotificationMessage>("notification", "/api/v1/notifications/", token, body),
  sendNotification: (token: string, id: string) => post<NotificationMessage>("notification", `/api/v1/notifications/${id}/send/`, token, {}),

  listReturns: (token: string) => list<ReturnRequest>("returnRefund", "/api/v1/returns/", token),
  createReturn: (token: string, order: Order, reason: string) =>
    post<ReturnRequest>("returnRefund", "/api/v1/returns/", token, {
      order_id: order.id,
      customer_id: order.customer_id,
      reason,
      idempotency_key: `return:${order.id}:${Date.now()}`,
      items: order.lines.map((line) => ({
        order_line_id: line.id,
        product_id: line.product_id,
        sku: line.sku,
        quantity: line.quantity,
        reason
      }))
    }),

  listAnalyticsEvents: (token: string) => list<AnalyticsEvent>("analytics", "/api/v1/events/", token),
  createAnalyticsEvent: (token: string, body: Partial<AnalyticsEvent>) => post<AnalyticsEvent>("analytics", "/api/v1/events/", token, body),
  listWorkItems: (token: string) => list<BackofficeWorkItem>("backoffice", "/api/v1/work-items/", token),
  createWorkItem: (token: string, body: Partial<BackofficeWorkItem>) => post<BackofficeWorkItem>("backoffice", "/api/v1/work-items/", token, body)
};
