export type Role = "admin" | "staff" | "customer";

export interface ApiListResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface AuthUser {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  role: Role;
}

export interface AuthSession {
  access: string;
  refresh: string;
  user: AuthUser;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  parent?: string | null;
  is_active: boolean;
}

export interface Product {
  id: string;
  category: string;
  sku: string;
  name: string;
  slug: string;
  description: string;
  brand: string;
  product_type: "book" | "electronics" | "fashion";
  status: "draft" | "published" | "archived";
  attributes: Record<string, unknown>;
  image_urls: string[];
}

export interface SearchProductDocument {
  id: string;
  product_id: string;
  sku: string;
  name: string;
  description: string;
  product_type: Product["product_type"];
  category_id?: string | null;
  brand: string;
  status: Product["status"];
  price_amount?: string | null;
  currency: string;
  available_quantity: number;
  rating_average?: string | null;
  attributes: Record<string, unknown>;
  image_urls: string[];
  search_text: string;
}

export interface PriceBook {
  id: string;
  code: string;
  name: string;
  currency: string;
  is_active: boolean;
}

export interface ProductPrice {
  id: string;
  price_book: string;
  product_id: string;
  sku: string;
  amount: string;
  compare_at_amount?: string | null;
  is_active: boolean;
}

export interface QuoteLine {
  sku: string;
  quantity: number;
  unit_price: string;
  line_total: string;
  currency: string;
}

export interface Quote {
  currency: string;
  subtotal: string;
  discount_total: string;
  total: string;
  items: QuoteLine[];
}

export interface Cart {
  id: string;
  customer_id: string | null;
  session_key: string;
  status: "active" | "checked_out" | "abandoned";
  items: CartItem[];
}

export interface CartItem {
  id: string;
  cart: string;
  product_id: string;
  sku: string;
  product_name: string;
  quantity: number;
  unit_price_snapshot?: string | null;
  attributes_snapshot: Record<string, unknown>;
}

export interface OrderLine {
  id: string;
  product_id: string;
  sku: string;
  product_name: string;
  quantity: number;
  unit_price: string;
  line_total: string;
}

export interface Order {
  id: string;
  customer_id: string;
  status: string;
  currency: string;
  subtotal: string;
  discount_total: string;
  shipping_fee: string;
  grand_total: string;
  shipping_address: Record<string, unknown>;
  created_at: string;
  lines: OrderLine[];
}

export interface CustomerProfile {
  id: string;
  user_id: string;
  email: string;
  full_name: string;
  phone: string;
  status: string;
  preferences: Record<string, unknown>;
}

export interface Address {
  id: string;
  customer: string;
  label: string;
  recipient_name: string;
  phone: string;
  line1: string;
  line2: string;
  city: string;
  state: string;
  country: string;
  postal_code: string;
  is_default: boolean;
}

export interface WishlistItem {
  id: string;
  customer: string;
  product_id: string;
  sku: string;
  name_snapshot: string;
}

export interface Warehouse {
  id: string;
  code: string;
  name: string;
  city: string;
  country: string;
  is_active: boolean;
}

export interface StockItem {
  id: string;
  warehouse: string;
  product_id: string;
  sku: string;
  quantity_on_hand: number;
  quantity_reserved: number;
  available_quantity: number;
}

export interface Payment {
  id: string;
  order_id: string;
  customer_id: string;
  amount: string;
  currency: string;
  provider: string;
  status: string;
  idempotency_key: string;
}

export interface Carrier {
  id: string;
  code: string;
  name: string;
  tracking_url_template: string;
  is_active: boolean;
}

export interface Shipment {
  id: string;
  order_id: string;
  carrier: string;
  tracking_number: string;
  status: string;
  ship_to: Record<string, unknown>;
  package_items: unknown[];
}

export interface ProductReview {
  id: string;
  product_id: string;
  customer_id: string;
  order_id: string;
  rating: number;
  title: string;
  body: string;
  status: string;
  created_at?: string;
  updated_at?: string;
}


export interface Recommendation {
  id: string;
  customer_id: string;
  product_id: string;
  sku: string;
  score: string;
  reason: string;
}

export interface AIProductSuggestion {
  product_id: string;
  sku: string;
  name: string;
  product_type: string;
  brand: string;
  reason: string;
  score?: number;
  source?: string;
}

export interface AIChatResponse {
  answer: string;
  source: string;
  intent: string;
  suggestions: AIProductSuggestion[];
}

export interface NextBuyRecommendation {
  product_id: string;
  sku: string;
  name: string;
  product_type: string;
  brand: string;
  score: number;
  source: string;
  reason: string;
}

export interface NextBuyRecommendationResponse {
  customer_id: string;
  source: string;
  model: Record<string, unknown>;
  recommendations: NextBuyRecommendation[];
}

export interface NotificationMessage {
  id: string;
  recipient_user_id?: string | null;
  recipient: string;
  channel: string;
  template_code: string;
  subject: string;
  body: string;
  payload: Record<string, unknown>;
  status: string;
}

export interface ReturnRequest {
  id: string;
  order_id: string;
  customer_id: string;
  reason: string;
  status: string;
}

export interface AnalyticsEvent {
  id: string;
  event_name: string;
  aggregate_type: string;
  aggregate_id?: string | null;
  customer_id?: string | null;
  occurred_at: string;
  payload: Record<string, unknown>;
}

export interface BackofficeWorkItem {
  id: string;
  context: string;
  aggregate_type: string;
  aggregate_id?: string | null;
  title: string;
  status: string;
  priority: number;
}
