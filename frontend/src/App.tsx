import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link, Navigate, Route, Routes, useLocation, useNavigate, useParams } from "react-router-dom";
import {
  ArrowRight,
  BarChart3,
  Bell,
  Boxes,
  CheckCircle2,
  CreditCard,
  Heart,
  Home,
  LogIn,
  LogOut,
  Minus,
  Package,
  PackageCheck,
  Plus,
  RefreshCcw,
  RotateCcw,
  Search,
  Settings,
  ShieldCheck,
  ShoppingBag,
  ShoppingCart,
  Star,
  Truck,
  UserRound,
  Warehouse
} from "lucide-react";

import { api, serviceUrls } from "./api";
import AIChatbot from "./components/AIChatbot";
import { useAuth } from "./contexts/AuthContext";
import type {
  Address,
  AnalyticsEvent,
  AuthSession,
  BackofficeWorkItem,
  Carrier,
  Cart,
  CartItem,
  Category,
  CustomerProfile,
  NextBuyRecommendation,
  NextBuyRecommendationResponse,
  NotificationMessage,
  Order,
  Payment,
  PriceBook,
  Product,
  ProductPrice,
  ProductReview,
  Recommendation,
  ReturnRequest,
  Shipment,
  StockItem,
  Warehouse as WarehouseModel,
  WishlistItem
} from "./types";

type RoleRoute = "admin" | "staff" | "customer";
type ProductEventType = "viewed" | "added_to_cart" | "purchased" | "wishlisted";

interface AppData {
  categories: Category[];
  products: Product[];
  priceBooks: PriceBook[];
  prices: ProductPrice[];
  stockItems: StockItem[];
  carts: Cart[];
  profiles: CustomerProfile[];
  addresses: Address[];
  wishlist: WishlistItem[];
  recommendations: Recommendation[];
  nextBuyRecommendations: NextBuyRecommendation[];
  orders: Order[];
  payments: Payment[];
  shipments: Shipment[];
  warehouses: WarehouseModel[];
  carriers: Carrier[];
  reviews: ProductReview[];
  notifications: NotificationMessage[];
  returns: ReturnRequest[];
  analyticsEvents: AnalyticsEvent[];
  workItems: BackofficeWorkItem[];
}

const emptyData: AppData = {
  categories: [],
  products: [],
  priceBooks: [],
  prices: [],
  stockItems: [],
  carts: [],
  profiles: [],
  addresses: [],
  wishlist: [],
  recommendations: [],
  nextBuyRecommendations: [],
  orders: [],
  payments: [],
  shipments: [],
  warehouses: [],
  carriers: [],
  reviews: [],
  notifications: [],
  returns: [],
  analyticsEvents: [],
  workItems: []
};

function money(value?: string | number | null, currency = "VND") {
  const numberValue = Number(value || 0);
  return new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency,
    maximumFractionDigits: currency === "VND" ? 0 : 2
  }).format(numberValue);
}

function compactError(error: unknown) {
  if (!(error instanceof Error)) return "Request failed.";
  try {
    const parsed = JSON.parse(error.message);
    if (parsed.detail) return parsed.detail;
    return Object.entries(parsed)
      .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(", ") : String(value)}`)
      .join(" | ");
  } catch {
    return error.message;
  }
}

function routeForRole(role?: string): string {
  if (role === "admin") return "/admin";
  if (role === "staff") return "/staff";
  return "/customer";
}

function productInitials(product: Product) {
  return product.name
    .split(" ")
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}

export default function App() {
  const { session, token, login, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [data, setData] = useState<AppData>(emptyData);
  const [loading, setLoading] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");

  const activeCart = useMemo(() => data.carts.find((cart) => cart.status === "active") || null, [data.carts]);
  const cartCount = activeCart?.items.reduce((total, item) => total + item.quantity, 0) || 0;
  const currentProfile = data.profiles.find((profile) => profile.user_id === session?.user.id);

  const priceBySku = useMemo(() => {
    const map = new Map<string, ProductPrice>();
    data.prices.forEach((price) => {
      if (price.is_active) map.set(price.sku, price);
    });
    return map;
  }, [data.prices]);

  const stockBySku = useMemo(() => {
    const map = new Map<string, number>();
    data.stockItems.forEach((stock) => {
      map.set(stock.sku, (map.get(stock.sku) || 0) + Number(stock.available_quantity ?? stock.quantity_on_hand ?? 0));
    });
    return map;
  }, [data.stockItems]);

  const currencyMap = useMemo(() => {
    const map = new Map<string, string>();
    data.priceBooks.forEach((book) => {
      map.set(book.id, book.currency);
    });
    return map;
  }, [data.priceBooks]);

  async function run<T>(operation: () => Promise<T>, success?: string) {
    setLoading(true);
    setError("");
    setNotice("");
    try {
      const result = await operation();
      if (success) setNotice(success);
      return result;
    } catch (err) {
      setError(compactError(err));
      return null;
    } finally {
      window.setTimeout(() => {
        setNotice("");
        setError("");
      }, 5000);
      setLoading(false);
    }
  }

  async function refreshData(nextToken = token, nextSession = session) {
    const [categories, products] = await Promise.all([
      api.listCategories(nextToken || undefined).catch(() => []),
      api.listProducts(nextToken || undefined).catch(() => [])
    ]);

    const nextData: AppData = { ...emptyData, categories, products };
    if (!nextToken || !nextSession) {
      setData(nextData);
      return;
    }

    const [
      profiles,
      prices,
      stockItems,
      carts,
      orders,
      wishlist,
      addresses,
      payments,
      shipments,
      reviews,
      notifications,
      returns,
      warehouses,
      priceBooks,
      carriers,
      analyticsEvents,
      workItems
    ] = await Promise.all([
      api.listProfiles(nextToken).catch(() => []),
      api.listPrices(nextToken).catch(() => []),
      api.listStockItems(nextToken).catch(() => []),
      api.listCarts(nextToken).catch(() => []),
      api.listOrders(nextToken).catch(() => []),
      api.listWishlist(nextToken).catch(() => []),
      api.listAddresses(nextToken).catch(() => []),
      api.listPayments(nextToken).catch(() => []),
      api.listShipments(nextToken).catch(() => []),
      api.listReviews(nextToken).catch(() => []),
      api.listNotifications(nextToken).catch(() => []),
      api.listReturns(nextToken).catch(() => []),
      api.listWarehouses(nextToken).catch(() => []),
      api.listPriceBooks(nextToken).catch(() => []),
      api.listCarriers(nextToken).catch(() => []),
      api.listAnalyticsEvents(nextToken).catch(() => []),
      api.listWorkItems(nextToken).catch(() => [])
    ]);

    const profile = profiles.find((item) => item.user_id === nextSession.user.id);
    let recommendations: Recommendation[] = [];
    let nextBuyResponse: NextBuyRecommendationResponse | null = null;
    if (profile) {
      [recommendations, nextBuyResponse] = await Promise.all([
        api.listRecommendations(nextToken, profile.id).catch(() => []),
        api.nextBuyRecommendations(nextToken, profile.id).catch(() => null)
      ]);
    }

    setData({
      categories,
      products,
      priceBooks,
      prices,
      stockItems,
      carts,
      profiles,
      addresses,
      wishlist,
      recommendations,
      nextBuyRecommendations: nextBuyResponse?.recommendations || [],
      orders,
      payments,
      shipments,
      warehouses,
      carriers,
      reviews,
      notifications,
      returns,
      analyticsEvents,
      workItems
    });
  }

  useEffect(() => {
    void refreshData();
  }, [token]);

  function handleLogout() {
    logout();
    setData((current) => ({ ...emptyData, categories: current.categories, products: current.products }));
    setNotice("Signed out.");
    navigate("/");
  }

  async function handleLogin(nextSession: AuthSession) {
    login(nextSession);
    await refreshData(nextSession.access, nextSession);
    navigate("/");
  }

  async function ensureProfile() {
    if (!session || !token) throw new Error("Sign in first.");
    if (currentProfile) return currentProfile;
    const created = await api.createProfile(token, {
      user_id: session.user.id,
      email: session.user.email,
      full_name: session.user.full_name,
      phone: session.user.phone || "",
      preferences: {}
    });
    setData((current) => ({ ...current, profiles: [created, ...current.profiles] }));
    return created;
  }

  async function ensureCart() {
    if (!session || !token) throw new Error("Sign in first.");
    if (activeCart) return activeCart;
    const created = await api.createCart(token, session.user.id);
    setData((current) => ({ ...current, carts: [created, ...current.carts] }));
    return created;
  }

  async function trackProductEvent(productId: string, sku: string, eventType: ProductEventType, metadata: Record<string, unknown> = {}) {
    if (!session || !token) return;
    try {
      const profile = await ensureProfile();
      await api.trackInteraction(token, {
        customer_id: profile.id,
        product_id: productId,
        sku,
        event_type: eventType,
        metadata: { source: "frontend", ...metadata }
      });
    } catch {
      // Behavior tracking must not block the shopping flow.
    }
  }

  async function addToCart(product: Product, quantity = 1) {
    if (!session || !token) {
      navigate("/login");
      return;
    }
    await run(async () => {
      const cart = await ensureCart();
      const existing = cart.items.find((item) => item.sku === product.sku);
      const productPrice = priceBySku.get(product.sku);
      if (existing) {
        await api.updateCartItem(token, existing.id, { quantity: existing.quantity + quantity });
      } else {
        await api.addCartItem(token, {
          cart: cart.id,
          product_id: product.id,
          sku: product.sku,
          product_name: product.name,
          quantity,
          unit_price_snapshot: productPrice?.amount || "0.00",
          attributes_snapshot: product.attributes || {}
        });
      }
      await trackProductEvent(product.id, product.sku, "added_to_cart", { quantity });
      await refreshData();
    }, "Giỏ hàng đã được cập nhật.");
  }

  async function addToWishlist(product: Product) {
    if (!session || !token) {
      navigate("/login");
      return;
    }
    await run(async () => {
      const profile = await ensureProfile();
      await api.addWishlist(token, {
        customer: profile.id,
        product_id: product.id,
        sku: product.sku,
        name_snapshot: product.name
      });
      await trackProductEvent(product.id, product.sku, "wishlisted");
      await refreshData();
    }, "Đã thêm vào yêu thích.");
  }

  return (
    <div className="shop-shell role-shell">
      <AppHeader
        session={session}
        activePath={location.pathname}
        cartCount={cartCount}
        onRefresh={() => void run(() => refreshData(), "Refreshed.")}
        onLogout={handleLogout}
      />

      <main className="role-main">
        {(notice || error) && <div className={error ? "feedback error" : "feedback"}>{error || notice}</div>}

        <Routes>
          <Route path="/" element={
            <HomePage
              data={data}
              priceBySku={priceBySku}
              currencyMap={currencyMap}
              stockBySku={stockBySku}
              addToCart={addToCart}
              addToWishlist={addToWishlist}
            />
          } />
          
          <Route path="/login" element={
            session ? <Navigate to="/" replace /> : <LoginPage loading={loading} run={run} onLogin={handleLogin} />
          } />

          <Route path="/register" element={
            session ? <Navigate to="/" replace /> : <RegisterPage loading={loading} run={run} />
          } />

          <Route path="/product/:id" element={
            <ProductDetailPage
              data={data}
              priceBySku={priceBySku}
              currencyMap={currencyMap}
              stockBySku={stockBySku}
              token={token}
              session={session}
              currentProfile={currentProfile}
              run={run}
              refreshData={refreshData}
              ensureCart={ensureCart}
              addToCart={addToCart}
            />
          } />

          <Route path="/search" element={
            <SearchResultsPage
              data={data}
              priceBySku={priceBySku}
              currencyMap={currencyMap}
              stockBySku={stockBySku}
              addToCart={addToCart}
              addToWishlist={addToWishlist}
            />
          } />

          <Route path="/customer" element={
            <RoleGate session={session} allowed={["customer", "staff", "admin"]}>
              <CustomerPage
                data={data}
                activeCart={activeCart}
                cartCount={cartCount}
                currentProfile={currentProfile}
                priceBySku={priceBySku}
                stockBySku={stockBySku}
                token={token}
                session={session}
                run={run}
                refreshData={refreshData}
                ensureProfile={ensureProfile}
                addToCart={addToCart}
                addToWishlist={addToWishlist}
              />
            </RoleGate>
          } />

          <Route path="/staff" element={
            <RoleGate session={session} allowed={["staff", "admin"]}>
              <StaffPage data={data} token={token} run={run} refreshData={refreshData} />
            </RoleGate>
          } />

          <Route path="/admin" element={
            <RoleGate session={session} allowed={["admin"]}>
              <AdminPage data={data} token={token} run={run} refreshData={refreshData} />
            </RoleGate>
          } />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      <AIChatbot />
    </div>
  );
}

function AppHeader({
  session,
  activePath,
  cartCount,
  onRefresh,
  onLogout
}: {
  session: AuthSession | null;
  activePath: string;
  cartCount: number;
  onRefresh: () => void;
  onLogout: () => void;
}) {
  const [searchVal, setSearchVal] = useState("");
  const navigate = useNavigate();
  const rolePortal =
    session?.user.role === "admin"
      ? { href: "/admin", label: "Trang admin" }
      : session?.user.role === "staff"
        ? { href: "/staff", label: "Trang staff" }
        : null;

  function handleSearch(e: FormEvent) {
    e.preventDefault();
    if (searchVal.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchVal.trim())}`);
    }
  }

  return (
    <header className="site-header role-header">
      {/* Top utility bar inside Shopee header */}
      <div className="header-top-bar">
        <div className="header-top-left">
          <span>Kênh Người Bán</span>
          <span>Tải ứng dụng</span>
          <span>Kết nối</span>
        </div>
        <div className="header-top-right">
          <span className="top-link-hide-mobile">Thông báo</span>
          <span className="top-link-hide-mobile">Hỗ trợ</span>
          {session ? (
            <div className="header-user-info">
              <span className="role-chip">{session.user.role}</span>
              {rolePortal && (
                <Link className="role-portal-link" to={rolePortal.href}>
                  <ShieldCheck size={14} />
                  <span>{rolePortal.label}</span>
                </Link>
              )}
              <strong>{session.user.full_name || session.user.email}</strong>
              <button className="header-logout-btn" onClick={onLogout}>Đăng xuất</button>
            </div>
          ) : (
            <div className="header-auth-links">
              <Link to="/register">Đăng ký</Link>
              <span className="divider">|</span>
              <Link to="/login">Đăng nhập</Link>
            </div>
          )}
        </div>
      </div>

      {/* Main search and logo bar */}
      <div className="header-main-bar">
        <Link className="brand" to="/">
          <div className="brand-mark">S</div>
          <div>
            <strong>Shopee OS</strong>
            <span>Microservice Mall</span>
          </div>
        </Link>

        <form onSubmit={handleSearch} className="search-box">
          <input
            value={searchVal}
            onChange={(e) => setSearchVal(e.target.value)}
            placeholder="Tìm sản phẩm, thương hiệu hoặc SKU..."
          />
          <button type="submit"><Search size={18} /></button>
        </form>

        <div className="header-actions-right">
          <button className="header-refresh-btn" onClick={onRefresh} title="Refresh">
            <RefreshCcw size={18} />
          </button>
          {session && (
            <Link to="/customer" className="cart-pill">
              <ShoppingCart size={17} />
              <span>Giỏ hàng ({cartCount})</span>
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}

function RoleGate({ session, allowed, children }: { session: AuthSession | null; allowed: string[]; children: JSX.Element }) {
  if (!session) return <Navigate to="/login" replace />;
  if (!allowed.includes(session.user.role)) {
    return (
      <section className="empty-state">
        <ShieldCheck size={28} />
        <strong>Không có quyền truy cập</strong>
        <span>Vai trò của bạn là {session.user.role}. Hãy sử dụng đúng tài khoản cho chức năng này.</span>
        <Link className="primary-button" to="/" style={{ textDecoration: "none", marginTop: "12px" }}>Về trang chủ</Link>
      </section>
    );
  }
  return children;
}

/* ========================================================
   PAGE 1: SHOPEE STOREFRONT HOME PAGE (GUESTS & USERS)
   ======================================================== */

function HomePage({
  data,
  priceBySku,
  currencyMap,
  stockBySku,
  addToCart,
  addToWishlist
}: {
  data: AppData;
  priceBySku: Map<string, ProductPrice>;
  currencyMap: Map<string, string>;
  stockBySku: Map<string, number>;
  addToCart: (product: Product) => Promise<void>;
  addToWishlist: (product: Product) => Promise<void>;
}) {
  return (
    <section className="home-page-shell">
      {/* Banners and Carousel Row */}
      <section className="hero-band home-hero">
        <div>
          <span className="eyebrow">Shopee OS Platform</span>
          <h1>Siêu Hội Mua Sắm E-Commerce Microservices</h1>
          <p>
            Trải nghiệm cổng mua sắm trực tuyến thiết kế theo Domain-Driven Design (DDD). Giao diện Shopee được kết nối trực tiếp đến 16 dịch vụ độc lập thông qua API Gateway.
          </p>
        </div>
        <aside className="home-highlight-card">
          <span>Khuyến Mãi Hot</span>
          <strong><CheckCircle2 size={16} /> Freeship Xtra</strong>
          <strong><CheckCircle2 size={16} /> Hoàn Xu 10%</strong>
          <strong><CheckCircle2 size={16} /> AI Chat Tư Vấn 24/7</strong>
          <small>Hệ thống tự động đồng bộ kho, giá và vận chuyển theo thời gian thực.</small>
        </aside>
      </section>

      {/* Categories Banner */}
      <section className="panel" style={{ padding: "16px" }}>
        <h2 style={{ fontSize: "0.95rem", textTransform: "uppercase", color: "#757575", border: "none", padding: "0" }}>Danh Mục Nổi Bật</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(120px, 1fr))", gap: "12px", textAlign: "center", marginTop: "12px" }}>
          {data.categories.map((cat) => (
            <div key={cat.id} style={{ background: "white", padding: "12px", border: "1px solid rgba(0,0,0,0.05)", borderRadius: "4px", cursor: "pointer" }}>
              <div style={{ width: "40px", height: "40px", background: "#ffeae6", borderRadius: "50%", margin: "0 auto 8px auto", display: "grid", placeItems: "center", color: "#ee4d2d" }}>
                <ShoppingBag size={20} />
              </div>
              <strong style={{ fontSize: "0.8rem", color: "#333", display: "block" }}>{cat.name}</strong>
            </div>
          ))}
        </div>
      </section>

      {/* Products list section */}
      <section>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#222222" }}>Gợi Ý Hôm Nay</h2>
        </div>
        
        <div className="product-grid">
          {data.products.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              price={priceBySku.get(product.sku)}
              currency={currencyMap.get(priceBySku.get(product.sku)?.price_book || "") || "VND"}
              stock={stockBySku.get(product.sku) || 0}
              onAdd={() => addToCart(product)}
              onWishlist={() => addToWishlist(product)}
            />
          ))}
          {!data.products.length && (
            <EmptyState icon={<Package size={26} />} title="Không có sản phẩm nào" text="Hệ thống catalog đang trống." />
          )}
        </div>
      </section>
    </section>
  );
}

/* ========================================================
   PAGE 2: DEDICATED LOGIN PAGE
   ======================================================== */

function LoginPage({
  loading,
  run,
  onLogin
}: {
  loading: boolean;
  run: <T>(operation: () => Promise<T>, success?: string) => Promise<T | null>;
  onLogin: (session: AuthSession) => Promise<void>;
}) {
  const [email, setEmail] = useState("customer@example.com");
  const [password, setPassword] = useState("password123");
  const navigate = useNavigate();

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextSession = await run(() => api.login(email, password), "Đăng nhập thành công.");
    if (nextSession) await onLogin(nextSession);
  }

  async function demoLogin(roleEmail: string) {
    const nextSession = await run(() => api.login(roleEmail, "password123"), "Đăng nhập Demo thành công.");
    if (nextSession) await onLogin(nextSession);
  }

  return (
    <section style={{ display: "grid", gridTemplateColumns: "minmax(0, 1fr) 420px", gap: "36px", alignItems: "center", padding: "40px 0" }}>
      <div style={{ paddingRight: "24px" }}>
        <h1 style={{ color: "#ee4d2d", fontSize: "3rem", fontWeight: 800 }}>Shopee OS</h1>
        <p style={{ fontSize: "1.3rem", color: "#555", marginTop: "12px", lineHeight: 1.5 }}>
          Nền tảng thương mại điện tử microservices hàng đầu, tích hợp công nghệ AI gợi ý và chat tư vấn tự động.
        </p>
        <img
          src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='300' viewBox='0 0 400 300'%3E%3Crect width='400' height='300' fill='%23f5f5f5'/%3E%3Cg fill='%23ee4d2d' opacity='.15'%3E%3Ccircle cx='200' cy='150' r='100'/%3E%3C/g%3E%3C/svg%3E"
          alt="Banner"
          style={{ width: "100%", maxWidth: "400px", marginTop: "24px" }}
        />
      </div>

      <div className="panel" style={{ padding: "30px" }}>
        <h2 style={{ fontSize: "1.3rem", fontWeight: 700, border: "none", padding: "0", marginBottom: "20px" }}>Đăng Nhập</h2>
        <form className="login-card" onSubmit={submit}>
          <label className="field">
            <span>Email</span>
            <input value={email} type="email" onChange={(event) => setEmail(event.target.value)} required />
          </label>
          <label className="field">
            <span>Mật khẩu</span>
            <input value={password} type="password" onChange={(event) => setPassword(event.target.value)} required />
          </label>
          <button className="primary-button" disabled={loading} type="submit" style={{ width: "100%", minHeight: "44px" }}>
            ĐĂNG NHẬP
          </button>
          
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginTop: "10px" }}>
            <span style={{ color: "#0056b3", cursor: "pointer" }}>Quên mật khẩu?</span>
            <Link to="/register" style={{ color: "#ee4d2d", textDecoration: "none", fontWeight: 700 }}>Đăng ký tài khoản</Link>
          </div>

          <div style={{ borderTop: "1px solid #f1f1f1", marginTop: "20px", paddingTop: "20px" }}>
            <span style={{ display: "block", fontSize: "0.75rem", color: "#757575", textAlign: "center", marginBottom: "12px" }}>
              ĐĂNG NHẬP NHANH VỚI TÀI KHOẢN DEMO
            </span>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "8px" }}>
              <button type="button" className="secondary-button" style={{ fontSize: "0.75rem" }} onClick={() => demoLogin("customer@example.com")}>Customer</button>
              <button type="button" className="secondary-button" style={{ fontSize: "0.75rem" }} onClick={() => demoLogin("staff@example.com")}>Staff</button>
              <button type="button" className="secondary-button" style={{ fontSize: "0.75rem" }} onClick={() => demoLogin("admin@example.com")}>Admin</button>
            </div>
          </div>
        </form>
      </div>
    </section>
  );
}

/* ========================================================
   PAGE 3: DEDICATED REGISTER PAGE
   ======================================================== */

function RegisterPage({
  loading,
  run
}: {
  loading: boolean;
  run: <T>(operation: () => Promise<T>, success?: string) => Promise<T | null>;
}) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const navigate = useNavigate();

  async function handleRegister(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const success = await run(() => api.register(fullName, email, password), "Tạo tài khoản thành công! Hãy đăng nhập.");
    if (success !== null) {
      navigate("/login");
    }
  }

  return (
    <section style={{ display: "grid", gridTemplateColumns: "minmax(0, 1fr) 420px", gap: "36px", alignItems: "center", padding: "40px 0" }}>
      <div style={{ paddingRight: "24px" }}>
        <h1 style={{ color: "#ee4d2d", fontSize: "3rem", fontWeight: 800 }}>Shopee OS</h1>
        <p style={{ fontSize: "1.3rem", color: "#555", marginTop: "12px", lineHeight: 1.5 }}>
          Đăng ký tài khoản ngay hôm nay để nhận voucher giảm giá và kết nối với chatbot AI tư vấn.
        </p>
      </div>

      <div className="panel" style={{ padding: "30px" }}>
        <h2 style={{ fontSize: "1.3rem", fontWeight: 700, border: "none", padding: "0", marginBottom: "20px" }}>Đăng Ký</h2>
        <form className="login-card" onSubmit={handleRegister}>
          <label className="field">
            <span>Họ và Tên</span>
            <input value={fullName} onChange={(event) => setFullName(event.target.value)} placeholder="Nguyễn Văn A" required />
          </label>
          <label className="field">
            <span>Email</span>
            <input value={email} type="email" onChange={(event) => setEmail(event.target.value)} placeholder="email@example.com" required />
          </label>
          <label className="field">
            <span>Mật khẩu</span>
            <input value={password} type="password" onChange={(event) => setPassword(event.target.value)} placeholder="Tối thiểu 8 ký tự" required />
          </label>
          <button className="primary-button" disabled={loading} type="submit" style={{ width: "100%", minHeight: "44px", marginTop: "10px" }}>
            ĐĂNG KÝ
          </button>
          
          <div style={{ textAlign: "center", fontSize: "0.85rem", marginTop: "16px" }}>
            <span>Bạn đã có tài khoản? </span>
            <Link to="/login" style={{ color: "#ee4d2d", textDecoration: "none", fontWeight: 700 }}>Đăng nhập</Link>
          </div>
        </form>
      </div>
    </section>
  );
}

/* ========================================================
   PAGE 4: PRODUCT DETAIL PAGE (SPECIFICATIONS & REVIEWS)
   ======================================================== */

function ProductDetailPage({
  data,
  priceBySku,
  currencyMap,
  stockBySku,
  token,
  session,
  currentProfile,
  run,
  refreshData,
  ensureCart,
  addToCart
}: {
  data: AppData;
  priceBySku: Map<string, ProductPrice>;
  currencyMap: Map<string, string>;
  stockBySku: Map<string, number>;
  token: string;
  session: AuthSession | null;
  currentProfile?: CustomerProfile;
  run: <T>(operation: () => Promise<T>, success?: string) => Promise<T | null>;
  refreshData: () => Promise<void>;
  ensureCart: () => Promise<Cart>;
  addToCart: (product: Product, quantity: number) => Promise<void>;
}) {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const product = useMemo(() => data.products.find((p) => p.id === id) || null, [data.products, id]);
  const price = useMemo(() => (product ? priceBySku.get(product.sku) : null), [product, priceBySku]);
  const stock = useMemo(() => (product ? stockBySku.get(product.sku) || 0 : 0), [product, stockBySku]);
  const currency = useMemo(() => (price ? currencyMap.get(price.price_book) || "VND" : "VND"), [price, currencyMap]);

  const productReviews = useMemo(() => data.reviews.filter((r) => r.product_id === id && r.status === "approved"), [data.reviews, id]);

  const [qty, setQty] = useState(1);
  const [reviewRating, setReviewRating] = useState(5);
  const [reviewTitle, setReviewTitle] = useState("");
  const [reviewComment, setReviewComment] = useState("");

  useEffect(() => {
    if (!token || !currentProfile || !product) return;
    void api.trackInteraction(token, {
      customer_id: currentProfile.id,
      product_id: product.id,
      sku: product.sku,
      event_type: "viewed",
      metadata: { source: "frontend", page: "product_detail" }
    }).catch(() => undefined);
  }, [token, currentProfile?.id, product?.id]);

  if (!product) {
    return (
      <section className="empty-state">
        <Package size={32} />
        <strong>Không tìm thấy sản phẩm</strong>
        <span>Sản phẩm này không tồn tại hoặc đã bị xóa.</span>
        <Link className="primary-button" to="/" style={{ textDecoration: "none", marginTop: "12px" }}>Quay về trang chủ</Link>
      </section>
    );
  }

  async function handleBuyNow() {
    if (!session || !token) {
      navigate("/login");
      return;
    }
    await addToCart(product!, qty);
    navigate("/customer");
  }

  async function submitReview(e: FormEvent) {
    e.preventDefault();
    if (!session || !token) {
      navigate("/login");
      return;
    }
    await run(async () => {
      await api.createReview(token, {
        product_id: product!.id,
        order_id: crypto.randomUUID(),
        rating: reviewRating,
        title: reviewTitle,
        body: reviewComment
      });
      setReviewTitle("");
      setReviewComment("");
      await refreshData();
    }, "Cảm ơn bạn đã gửi đánh giá! Review của bạn đang chờ phê duyệt.");
  }


  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* Breadcrumbs */}
      <div style={{ fontSize: "0.85rem", color: "#757575" }}>
        <Link to="/" style={{ color: "#0056b3", textDecoration: "none" }}>Trang chủ</Link>
        <span> &gt; </span>
        <span style={{ textTransform: "capitalize" }}>{product.product_type}</span>
        <span> &gt; </span>
        <strong>{product.name}</strong>
      </div>

      {/* Main product detail container */}
      <section className="panel" style={{ display: "grid", gridTemplateColumns: "400px minmax(0, 1fr)", gap: "30px", padding: "30px" }}>
        <div>
          {product.image_urls?.[0] ? (
            <img src={product.image_urls[0]} alt={product.name} style={{ width: "100%", aspectRatio: "1/1", objectFit: "cover", border: "1px solid #f1f1f1" }} />
          ) : (
            <div className={`product-art ${product.product_type}`} style={{ aspectRatio: "1/1", borderRadius: "4px" }}>
              <span>{productInitials(product)}</span>
            </div>
          )}
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div>
            <h1 style={{ fontSize: "1.4rem", fontWeight: 700, color: "#222222", lineHeight: 1.3 }}>{product.name}</h1>
            <div style={{ display: "flex", gap: "16px", alignItems: "center", marginTop: "8px", fontSize: "0.85rem", color: "#555" }}>
              <span>Thương hiệu: <strong style={{ color: "#ee4d2d" }}>{product.brand}</strong></span>
              <span style={{ opacity: 0.3 }}>|</span>
              <span>SKU: <strong>{product.sku}</strong></span>
            </div>
          </div>

          <div style={{ background: "#fafafa", padding: "16px 20px", borderRadius: "4px" }}>
            <strong style={{ fontSize: "2rem", color: "#ee4d2d", fontWeight: 700 }}>
              {price ? money(price.amount, currency) : "Liên hệ để biết giá"}
            </strong>
          </div>

          <p style={{ fontSize: "0.9rem", color: "#666", lineHeight: 1.5 }}>
            {product.description || "Không có mô tả cho sản phẩm này."}
          </p>

          <div style={{ display: "flex", alignItems: "center", gap: "16px", fontSize: "0.88rem" }}>
            <span>Số lượng:</span>
            <div className="quantity-stepper">
              <button onClick={() => setQty((v) => Math.max(1, v - 1))}>-</button>
              <b>{qty}</b>
              <button onClick={() => setQty((v) => Math.min(stock, v + 1))}>+</button>
            </div>
            <span style={{ color: "#757575" }}>{stock} sản phẩm sẵn có</span>
          </div>

          <div style={{ display: "flex", gap: "12px", marginTop: "10px" }}>
            <button className="secondary-button" style={{ borderColor: "#ee4d2d", color: "#ee4d2d", background: "#ffeae6", minHeight: "46px", padding: "0 24px" }} onClick={() => void addToCart(product, qty)}>
              <ShoppingCart size={18} /> Thêm Vào Giỏ Hàng
            </button>
            <button className="primary-button" style={{ minHeight: "46px", padding: "0 28px" }} onClick={() => void handleBuyNow()}>
              Mua Ngay
            </button>
          </div>
        </div>
      </section>

      {/* Specifications context according to guide_tieuluan.md product fields */}
      <section className="panel">
        <h2>Thông Số Sản Phẩm</h2>
        <div style={{ display: "grid", gridTemplateColumns: "180px 1fr", gap: "12px 20px", fontSize: "0.88rem", padding: "10px 0" }}>
          <span style={{ color: "#757575" }}>Danh mục</span>
          <strong>{product.product_type.toUpperCase()}</strong>
          
          <span style={{ color: "#757575" }}>Thương hiệu</span>
          <strong>{product.brand}</strong>

          <span style={{ color: "#757575" }}>Mã sản phẩm (SKU)</span>
          <strong>{product.sku}</strong>

          {/* Dynamic properties from JSON attributes */}
          {product.product_type === "book" && (
            <>
              <span style={{ color: "#757575" }}>Tác giả</span>
              <strong>{String(product.attributes.author || "Chưa cập nhật")}</strong>
              <span style={{ color: "#757575" }}>Nhà xuất bản</span>
              <strong>{String(product.attributes.publisher || "Chưa cập nhật")}</strong>
              <span style={{ color: "#757575" }}>Mã ISBN</span>
              <strong>{String(product.attributes.isbn || "Chưa cập nhật")}</strong>
            </>
          )}

          {product.product_type === "electronics" && (
            <>
              <span style={{ color: "#757575" }}>Thời hạn bảo hành</span>
              <strong>{String(product.attributes.warranty || "12 tháng")}</strong>
              <span style={{ color: "#757575" }}>Model</span>
              <strong>{String(product.attributes.model || "Standard")}</strong>
            </>
          )}

          {product.product_type === "fashion" && (
            <>
              <span style={{ color: "#757575" }}>Màu sắc</span>
              <strong>{String(product.attributes.color || "Nhiều màu")}</strong>
              <span style={{ color: "#757575" }}>Kích cỡ</span>
              <strong>{String(product.attributes.size || "Free size")}</strong>
            </>
          )}

          {Object.entries(product.attributes).map(([key, val]) => {
            if (["author", "publisher", "isbn", "warranty", "model", "color", "size"].includes(key)) return null;
            return (
              <div key={key} style={{ display: "contents" }}>
                <span style={{ color: "#757575", textTransform: "capitalize" }}>{key}</span>
                <strong>{String(val)}</strong>
              </div>
            );
          })}
        </div>
      </section>

      {/* Reviews context */}
      <section className="panel">
        <h2>Đánh Giá Sản Phẩm</h2>
        <div style={{ display: "flex", flexDirection: "column", gap: "16px", marginTop: "10px" }}>
          {/* List existing approved reviews */}
          {productReviews.map((review) => (
            <div key={review.id} style={{ borderBottom: "1px solid #f1f1f1", paddingBottom: "16px", display: "flex", gap: "12px" }}>
              <div style={{ width: "32px", height: "32px", borderRadius: "50%", background: "#ccc", display: "grid", placeItems: "center", fontWeight: "bold", fontSize: "0.8rem", color: "white" }}>
                U
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                <div style={{ display: "flex", gap: "4px", color: "#ffb700" }}>
                  {Array.from({ length: review.rating }).map((_, i) => (
                    <Star key={i} size={14} fill="#ffb700" />
                  ))}
                </div>
                <strong style={{ fontSize: "0.88rem" }}>{review.title || "Người dùng ẩn danh"}</strong>
                <p style={{ fontSize: "0.85rem", color: "#555", marginTop: "2px" }}>{review.body}</p>
                <small style={{ fontSize: "0.75rem", color: "#999" }}>{new Date(review.created_at || "").toLocaleString()}</small>

              </div>
            </div>
          ))}
          {!productReviews.length && <span style={{ color: "#757575", fontSize: "0.88rem" }}>Chưa có đánh giá nào cho sản phẩm này.</span>}

          {/* Form to submit review if logged in */}
          {session ? (
            <form onSubmit={submitReview} style={{ background: "#fafafa", padding: "20px", borderRadius: "4px", display: "flex", flexDirection: "column", gap: "12px", marginTop: "10px" }}>
              <strong style={{ fontSize: "0.95rem" }}>Viết Đánh Giá Của Bạn</strong>
              <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
                <span style={{ fontSize: "0.85rem" }}>Đánh giá sao:</span>
                <select value={reviewRating} onChange={(e) => setReviewRating(Number(e.target.value))} style={{ width: "100px", minHeight: "36px" }}>
                  <option value={5}>5 sao</option>
                  <option value={4}>4 sao</option>
                  <option value={3}>3 sao</option>
                  <option value={2}>2 sao</option>
                  <option value={1}>1 sao</option>
                </select>
              </div>
              <label className="field">
                <span>Tiêu đề</span>
                <input value={reviewTitle} onChange={(e) => setReviewTitle(e.target.value)} placeholder="Tóm tắt cảm nhận..." required />
              </label>
              <label className="field">
                <span>Nội dung đánh giá</span>
                <textarea value={reviewComment} onChange={(e) => setReviewComment(e.target.value)} rows={3} placeholder="Viết đánh giá chi tiết..." style={{ resize: "vertical", width: "100%", padding: "10px" }} required />
              </label>
              <button type="submit" className="primary-button" style={{ alignSelf: "flex-start" }}>Gửi Đánh Giá</button>
            </form>
          ) : (
            <div style={{ background: "#fafafa", padding: "14px", textAlign: "center", borderRadius: "4px", fontSize: "0.85rem" }}>
              Hãy <Link to="/login" style={{ color: "#ee4d2d", fontWeight: "bold", textDecoration: "none" }}>đăng nhập</Link> để viết đánh giá cho sản phẩm này.
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

/* ========================================================
   PAGE 5: SEARCH RESULTS PAGE
   ======================================================== */

function SearchResultsPage({
  data,
  priceBySku,
  currencyMap,
  stockBySku,
  addToCart,
  addToWishlist
}: {
  data: AppData;
  priceBySku: Map<string, ProductPrice>;
  currencyMap: Map<string, string>;
  stockBySku: Map<string, number>;
  addToCart: (product: Product) => Promise<void>;
  addToWishlist: (product: Product) => Promise<void>;
}) {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const q = searchParams.get("q") || "";

  const results = useMemo(() => {
    const term = q.trim().toLowerCase();
    if (!term) return data.products;
    return data.products.filter(
      (p) =>
        p.name.toLowerCase().includes(term) ||
        p.sku.toLowerCase().includes(term) ||
        p.brand.toLowerCase().includes(term) ||
        (p.description && p.description.toLowerCase().includes(term))
    );
  }, [data.products, q]);

  return (
    <section style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      <div style={{ fontSize: "0.95rem", color: "#555" }}>
        Kết quả tìm kiếm cho từ khóa: <strong style={{ color: "#ee4d2d", fontSize: "1.1rem" }}>"{q}"</strong>
      </div>

      <div className="product-grid">
        {results.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            price={priceBySku.get(product.sku)}
            currency={currencyMap.get(priceBySku.get(product.sku)?.price_book || "") || "VND"}
            stock={stockBySku.get(product.sku) || 0}
            onAdd={() => addToCart(product)}
            onWishlist={() => addToWishlist(product)}
          />
        ))}
        {!results.length && (
          <EmptyState icon={<Package size={26} />} title="Không tìm thấy kết quả" text="Hãy thử tìm kiếm bằng từ khóa khác." />
        )}
      </div>
    </section>
  );
}

/* ========================================================
   PAGE 6: CUSTOMER PORTAL
   ======================================================== */

function CustomerPage({
  data,
  activeCart,
  cartCount,
  currentProfile,
  priceBySku,
  stockBySku,
  token,
  session,
  run,
  refreshData,
  ensureProfile,
  addToCart,
  addToWishlist
}: {
  data: AppData;
  activeCart: Cart | null;
  cartCount: number;
  currentProfile?: CustomerProfile;
  priceBySku: Map<string, ProductPrice>;
  stockBySku: Map<string, number>;
  token: string;
  session: AuthSession | null;
  run: <T>(operation: () => Promise<T>, success?: string) => Promise<T | null>;
  refreshData: () => Promise<void>;
  ensureProfile: () => Promise<CustomerProfile>;
  addToCart: (product: Product) => Promise<void>;
  addToWishlist: (product: Product) => Promise<void>;
}) {
  const [couponCode, setCouponCode] = useState("");
  const [shippingAddress, setShippingAddress] = useState({
    recipient_name: session?.user.full_name || "Demo Customer",
    phone: "0900000000",
    line1: "123 Đường Tên Lửa",
    line2: "",
    city: "Thành phố Hồ Chí Minh",
    state: "",
    country: "VN",
    postal_code: "700000"
  });

  async function quoteCart() {
    if (!activeCart?.items.length) throw new Error("Giỏ hàng của bạn đang trống.");
    const quote = await api.quote(token, activeCart.items.map((item) => ({ sku: item.sku, quantity: item.quantity })), couponCode);
    window.alert(`Tổng tiền ước tính: ${money(quote.total, quote.currency)}`);
  }

  async function trackPurchasedCartItems(items: CartItem[]) {
    const profile = currentProfile || await ensureProfile();
    await Promise.all(items.map((item) => api.trackInteraction(token, {
      customer_id: profile.id,
      product_id: item.product_id,
      sku: item.sku,
      event_type: "purchased",
      metadata: { source: "frontend", quantity: item.quantity }
    }).catch(() => undefined)));
  }

  async function checkoutCart() {
    if (!activeCart?.items.length) throw new Error("Giỏ hàng của bạn đang trống.");
    const purchasedItems = [...activeCart.items];
    await api.checkout(token, activeCart.id, shippingAddress, couponCode);
    await trackPurchasedCartItems(purchasedItems);
    await refreshData();
  }

  async function createPayment(order: Order) {
    const payment = await api.createPayment(token, order);
    await api.markPaymentSucceeded(token, payment.id);
    await refreshData();
  }

  return (
    <section className="role-page customer-page">
      <div className="role-page-head">
        <div>
          <span>Bảng điều khiển khách hàng</span>
          <h2>Giỏ hàng, thanh toán và theo dõi đơn hàng</h2>
        </div>
        <button className="secondary-button" onClick={() => void run(() => ensureProfile(), "Profile synced.")}>
          <UserRound size={17} /> Đồng bộ hồ sơ
        </button>
      </div>

      <section className="role-dashboard-grid three-columns">
        <section className="panel">
          <div className="panel-title"><ShoppingCart size={20} /><h2>Giỏ Hàng</h2></div>
          <LineStack>
            {activeCart?.items.map((item) => (
              <CartLine key={item.id} item={item} token={token} refreshData={refreshData} />
            ))}
            {!cartCount && <span className="muted">Giỏ hàng trống. Hãy thêm sản phẩm ở trang chủ!</span>}
          </LineStack>
        </section>

        <section className="panel">
          <div className="panel-title"><CreditCard size={20} /><h2>Thanh Toán</h2></div>
          <label className="field"><span>Người nhận</span><input value={shippingAddress.recipient_name} onChange={(event) => setShippingAddress({ ...shippingAddress, recipient_name: event.target.value })} /></label>
          <label className="field"><span>Địa chỉ</span><input value={shippingAddress.line1} onChange={(event) => setShippingAddress({ ...shippingAddress, line1: event.target.value })} /></label>
          <label className="field"><span>Thành phố</span><input value={shippingAddress.city} onChange={(event) => setShippingAddress({ ...shippingAddress, city: event.target.value })} /></label>
          <label className="field"><span>Mã giảm giá (Coupon)</span><input value={couponCode} onChange={(event) => setCouponCode(event.target.value)} placeholder="Tùy chọn" /></label>
          <div className="button-row">
            <button className="secondary-button" disabled={!cartCount} onClick={() => void run(quoteCart, "Đã tính giá.")}>Tính tiền</button>
            <button className="primary-button" disabled={!cartCount} onClick={() => void run(checkoutCart, "Đơn hàng đã được đặt.")}>Đặt Hàng</button>
          </div>
        </section>

        <section className="panel">
          <div className="panel-title"><UserRound size={20} /><h2>Hồ Sơ Của Tôi</h2></div>
          <div className="session-summary">
            <span>Tài khoản</span>
            <strong>{session?.user.email}</strong>
            <p>{session?.user.full_name} / {session?.user.role}</p>
          </div>
          <DataPills items={[
            `Hồ sơ khách hàng: ${currentProfile ? "Sẵn sàng" : "Thiếu"}`,
            `Địa chỉ lưu trữ: ${data.addresses.length}`,
            `Yêu thích: ${data.wishlist.length}`,
            `Gợi ý gợi ý: ${data.recommendations.length}`,
            `AI next-buy: ${data.nextBuyRecommendations.length}`,
            `Tin nhắn thông báo: ${data.notifications.length}`
          ]} />
        </section>
      </section>

      <section className="panel">
        <div className="panel-title"><ShoppingBag size={20} /><h2>AI Next Buy</h2></div>
        <LineStack>
          {data.nextBuyRecommendations.slice(0, 6).map((item) => (
            <div className="line-item" key={`${item.source}-${item.sku}`}>
              <div>
                <strong>{item.name || item.sku}</strong>
                <span>{item.product_type || "product"} / {item.sku} / score {item.score.toFixed(2)}</span>
              </div>
              <span className="status-pill">{item.source}</span>
            </div>
          ))}
          {!data.nextBuyRecommendations.length && <span className="muted">No next-buy prediction yet. View, wishlist, add to cart, or purchase products to create behavior signals.</span>}
        </LineStack>
      </section>

      <section className="role-dashboard-grid two-columns">
        <OrderList title="Lịch sử đơn hàng" orders={data.orders} payments={data.payments} shipments={data.shipments} />
        <section className="panel">
          <div className="panel-title"><CreditCard size={20} /><h2>Thanh toán đơn hàng</h2></div>
          <LineStack>
            {data.orders.slice(0, 6).map((order) => (
              <div className="line-item" key={order.id}>
                <div><strong>Mã Đơn {order.id.slice(0, 8)}</strong><span>{order.status} / {money(order.grand_total, order.currency)}</span></div>
                <button className="primary-button" disabled={order.status !== "pending_payment"} onClick={() => void run(() => createPayment(order), "Đã thanh toán thành công.")}>Thanh toán</button>
              </div>
            ))}
            {!data.orders.length && <span className="muted">Chưa có đơn hàng nào cần thanh toán.</span>}
          </LineStack>
        </section>
      </section>
    </section>
  );
}

/* ========================================================
   PAGE HELPER COMPONENTS
   ======================================================== */

function ProductCard({
  product,
  price,
  currency,
  stock,
  onAdd,
  onWishlist
}: {
  product: Product;
  price?: ProductPrice;
  currency: string;
  stock: number;
  onAdd: () => Promise<void>;
  onWishlist: () => Promise<void>;
}) {
  return (
    <article className="product-card">
      <Link to={`/product/${product.id}`} style={{ textDecoration: "none", color: "inherit" }}>
        {product.image_urls?.[0] ? (
          <img src={product.image_urls[0]} alt={product.name} />
        ) : (
          <div className={`product-art ${product.product_type}`}><span>{productInitials(product)}</span></div>
        )}
      </Link>
      <div className="product-body">
        <div className="product-title-row">
          <Link to={`/product/${product.id}`} style={{ textDecoration: "none", color: "inherit" }}>
            <h3>{product.name}</h3>
          </Link>
          <span>{product.product_type}</span>
        </div>
        <div className="product-facts">
          <strong>{price ? money(price.amount, currency) : "Liên hệ"}</strong>
          <small>{stock > 0 ? `Bán ${stock}` : "Hết hàng"}</small>
        </div>
        <div className="product-actions">
          <button className="primary-button" onClick={() => void onAdd()} disabled={stock <= 0}>
            Mua
          </button>
          <button className="icon-button" onClick={() => void onWishlist()} title="Yêu thích">
            <Heart size={16} />
          </button>
        </div>
      </div>
    </article>
  );
}

function CartLine({ item, token, refreshData }: { item: CartItem; token: string; refreshData: () => Promise<void> }) {
  async function updateQuantity(quantity: number) {
    await api.updateCartItem(token, item.id, { quantity: Math.max(1, quantity) });
    await refreshData();
  }

  return (
    <div className="line-item">
      <div><strong>{item.product_name}</strong><span>{item.sku}</span></div>
      <div className="quantity-stepper">
        <button onClick={() => void updateQuantity(item.quantity - 1)}>-</button>
        <b>{item.quantity}</b>
        <button onClick={() => void updateQuantity(item.quantity + 1)}>+</button>
      </div>
    </div>
  );
}

function StaffPage({
  data,
  token,
  run,
  refreshData
}: {
  data: AppData;
  token: string;
  run: <T>(operation: () => Promise<T>, success?: string) => Promise<T | null>;
  refreshData: () => Promise<void>;
}) {
  const pendingOrders = data.orders.filter((order) => ["paid", "confirmed", "packed", "pending_payment"].includes(order.status));
  const lowStock = data.stockItems.filter((item) => Number(item.available_quantity ?? item.quantity_on_hand) <= 5);
  const pendingReviews = data.reviews.filter((review) => review.status === "pending");
  const openReturns = data.returns.filter((item) => !["closed", "completed"].includes(item.status));

  async function transition(order: Order, action: "confirm" | "cancel" | "ship" | "complete") {
    await api.transitionOrder(token, order.id, action);
    await refreshData();
  }

  async function markShipment(shipment: Shipment, status: string) {
    await api.updateShipmentStatus(token, shipment.id, status);
    await refreshData();
  }

  async function approveReview(review: ProductReview) {
    await api.approveReview(token, review.id);
    await refreshData();
  }

  return (
    <section className="role-page staff-page">
      <div className="role-page-head">
        <div>
          <span>Bảng điều khiển nhân viên</span>
          <h2>Xử lý đơn hàng, điều phối vận chuyển và duyệt đánh giá</h2>
        </div>
      </div>

      <section className="role-dashboard-grid four-columns">
        <MetricCard icon={<PackageCheck size={20} />} label="Đơn hàng đang xử lý" value={pendingOrders.length} />
        <MetricCard icon={<Warehouse size={20} />} label="Tồn kho thấp" value={lowStock.length} />
        <MetricCard icon={<Star size={20} />} label="Review chờ duyệt" value={pendingReviews.length} />
        <MetricCard icon={<RotateCcw size={20} />} label="Yêu cầu trả hàng" value={openReturns.length} />
      </section>

      <section className="role-dashboard-grid two-columns">
        <section className="panel">
          <div className="panel-title"><PackageCheck size={20} /><h2>Thao tác đơn hàng</h2></div>
          <LineStack>
            {data.orders.slice(0, 12).map((order) => (
              <div className="line-item operation-line" key={order.id}>
                <div><strong>Đơn hàng {order.id.slice(0, 8)}</strong><span>{order.status} / {money(order.grand_total, order.currency)}</span></div>
                <div className="button-row">
                  <button className="secondary-button" disabled={order.status !== "paid"} onClick={() => void run(() => transition(order, "confirm"), "Đơn hàng đã được xác nhận.")}>Xác nhận</button>
                  <button className="secondary-button" disabled={order.status !== "confirmed"} onClick={() => void run(() => transition(order, "ship"), "Đang tiến hành giao hàng.")}>Giao hàng</button>
                  <button className="primary-button" disabled={order.status !== "shipped"} onClick={() => void run(() => transition(order, "complete"), "Đơn hàng hoàn tất.")}>Hoàn tất</button>
                </div>
              </div>
            ))}
            {!data.orders.length && <span className="muted">Không có dữ liệu đơn hàng.</span>}
          </LineStack>
        </section>

        <section className="panel">
          <div className="panel-title"><Truck size={20} /><h2>Hành trình vận chuyển</h2></div>
          <LineStack>
            {data.shipments.slice(0, 10).map((shipment) => (
              <div className="line-item operation-line" key={shipment.id}>
                <div><strong>Mã Vận Đơn {shipment.id.slice(0, 8)}</strong><span>{shipment.status} / đơn {shipment.order_id.slice(0, 8)}</span></div>
                <div className="button-row">
                  <button className="secondary-button" onClick={() => void run(() => markShipment(shipment, "in_transit"), "Trạng thái: Đang vận chuyển.")}>Đang đi</button>
                  <button className="primary-button" onClick={() => void run(() => markShipment(shipment, "delivered"), "Trạng thái: Đã giao hàng.")}>Đã giao</button>
                </div>
              </div>
            ))}
            {!data.shipments.length && <span className="muted">Không có dữ liệu vận chuyển.</span>}
          </LineStack>
        </section>
      </section>

      <section className="role-dashboard-grid three-columns">
        <section className="panel">
          <div className="panel-title"><Warehouse size={20} /><h2>Theo dõi kho</h2></div>
          <DataPills items={lowStock.slice(0, 10).map((item) => `${item.sku}: còn ${item.available_quantity ?? item.quantity_on_hand}`)} empty="Không có cảnh báo tồn kho thấp." />
        </section>
        <section className="panel">
          <div className="panel-title"><Star size={20} /><h2>Kiểm duyệt Review</h2></div>
          <LineStack>
            {pendingReviews.slice(0, 6).map((review) => (
              <div className="line-item" key={review.id}>
                <div><strong>{review.title || `Rating ${review.rating}`}</strong><span>{review.status}</span></div>
                <button className="primary-button" onClick={() => void run(() => approveReview(review), "Review đã được duyệt.")}>Duyệt</button>
              </div>
            ))}
            {!pendingReviews.length && <span className="muted">Không có review nào cần duyệt.</span>}
          </LineStack>
        </section>
        <section className="panel">
          <div className="panel-title"><Bell size={20} /><h2>Kênh thông báo</h2></div>
          <DataPills items={data.notifications.slice(0, 8).map((item) => `${item.channel}: ${item.status}`)} empty="Không có tin nhắn nào." />
        </section>
      </section>
    </section>
  );
}

function AdminPage({
  data,
  token,
  run,
  refreshData
}: {
  data: AppData;
  token: string;
  run: <T>(operation: () => Promise<T>, success?: string) => Promise<T | null>;
  refreshData: () => Promise<void>;
}) {
  const [categoryName, setCategoryName] = useState("");
  const [productName, setProductName] = useState("");
  const [productSku, setProductSku] = useState("");
  const [warehouseCode, setWarehouseCode] = useState("");
  const [priceAmount, setPriceAmount] = useState("");
  const [workTitle, setWorkTitle] = useState("");

  async function createCategory() {
    if (!categoryName.trim()) throw new Error("Hãy nhập tên danh mục.");
    await api.createCategory(token, {
      name: categoryName,
      slug: categoryName.toLowerCase().trim().replace(/\s+/g, "-"),
      is_active: true
    });
    setCategoryName("");
    await refreshData();
  }

  async function createProduct() {
    const category = data.categories[0];
    if (!category) throw new Error("Hãy tạo danh mục trước.");
    if (!productName.trim() || !productSku.trim()) throw new Error("Hãy nhập tên sản phẩm và SKU.");
    await api.createProduct(token, {
      category: category.id,
      name: productName,
      sku: productSku,
      slug: productSku.toLowerCase(),
      description: "Sản phẩm được tạo từ admin portal",
      brand: "Shopee OS",
      product_type: "electronics",
      status: "published",
      attributes: {},
      image_urls: []
    });
    setProductName("");
    setProductSku("");
    await refreshData();
  }

  async function createWarehouse() {
    if (!warehouseCode.trim()) throw new Error("Hãy nhập mã kho.");
    await api.createWarehouse(token, {
      code: warehouseCode,
      name: `Kho ${warehouseCode}`,
      city: "Thành phố Hồ Chí Minh",
      country: "VN",
      is_active: true
    });
    setWarehouseCode("");
    await refreshData();
  }

  async function createPrice() {
    const product = data.products[0];
    let priceBook = data.priceBooks[0];
    if (!product) throw new Error("Hãy tạo sản phẩm trước.");
    if (!priceBook) {
      priceBook = await api.createPriceBook(token, {
        code: "DEFAULT",
        name: "Bảng giá VND mặc định",
        currency: "VND",
        is_active: true
      });
    }
    await api.createPrice(token, {
      price_book: priceBook.id,
      product_id: product.id,
      sku: product.sku,
      amount: priceAmount || "100000",
      is_active: true
    });
    setPriceAmount("");
    await refreshData();
  }

  async function createWorkItem() {
    if (!workTitle.trim()) throw new Error("Hãy nhập tiêu đề công việc.");
    await api.createWorkItem(token, {
      context: "admin",
      aggregate_type: "system",
      title: workTitle,
      status: "open",
      priority: 3
    });
    setWorkTitle("");
    await refreshData();
  }

  return (
    <section className="role-page admin-page">
      <div className="role-page-head">
        <div>
          <span>Bảng điều khiển Admin</span>
          <h2>Quản lý danh mục, giá bán, kho hàng và hệ thống</h2>
        </div>
      </div>

      <section className="role-dashboard-grid four-columns">
        <MetricCard icon={<Boxes size={20} />} label="Tổng sản phẩm" value={data.products.length} />
        <MetricCard icon={<Warehouse size={20} />} label="Hệ thống kho" value={data.warehouses.length} />
        <MetricCard icon={<BarChart3 size={20} />} label="Sự kiện Analytics" value={data.analyticsEvents.length} />
        <MetricCard icon={<Settings size={20} />} label="Công việc Backoffice" value={data.workItems.length} />
      </section>

      <section className="role-dashboard-grid two-columns">
        <section className="panel admin-control-panel">
          <div className="panel-title"><Boxes size={20} /><h2>Thiết lập Catalog</h2></div>
          <div className="form-grid">
            <label className="field"><span>Tên danh mục</span><input value={categoryName} onChange={(event) => setCategoryName(event.target.value)} placeholder="Điện tử / Thời trang / Sách" /></label>
            <button className="secondary-button" onClick={() => void run(createCategory, "Danh mục đã được tạo.")}>Tạo danh mục</button>
            <label className="field"><span>Tên sản phẩm</span><input value={productName} onChange={(event) => setProductName(event.target.value)} placeholder="Tên sản phẩm mới..." /></label>
            <label className="field"><span>Mã SKU</span><input value={productSku} onChange={(event) => setProductSku(event.target.value)} placeholder="SKU-001" /></label>
            <button className="primary-button" onClick={() => void run(createProduct, "Sản phẩm đã được tạo.")}><Plus size={17} /> Tạo sản phẩm</button>
          </div>
        </section>

        <section className="panel admin-control-panel">
          <div className="panel-title"><CreditCard size={20} /><h2>Bảng giá và Quản lý Kho</h2></div>
          <div className="form-grid">
            <label className="field"><span>Mã kho hàng</span><input value={warehouseCode} onChange={(event) => setWarehouseCode(event.target.value)} placeholder="KHO-HCM" /></label>
            <button className="secondary-button" onClick={() => void run(createWarehouse, "Kho hàng đã được tạo.")}>Tạo kho hàng</button>
            <label className="field"><span>Đơn giá VND</span><input value={priceAmount} onChange={(event) => setPriceAmount(event.target.value)} placeholder="150000" /></label>
            <button className="primary-button" onClick={() => void run(createPrice, "Thiết lập giá bán thành công.")}>Tạo giá bán sản phẩm</button>
          </div>
        </section>
      </section>

      <section className="role-dashboard-grid three-columns">
        <section className="panel">
          <div className="panel-title"><Settings size={20} /><h2>Backoffice</h2></div>
          <label className="field"><span>Yêu cầu vận hành</span><input value={workTitle} onChange={(event) => setWorkTitle(event.target.value)} placeholder="Kiểm tra bồi hoàn khi hủy đơn..." /></label>
          <button className="primary-button" onClick={() => void run(createWorkItem, "Đã gửi công việc.")}>Tạo công việc</button>
          <DataPills items={data.workItems.slice(0, 8).map((item) => `${item.title}: ${item.status}`)} empty="Không có công việc nào." />
        </section>
        <section className="panel">
          <div className="panel-title"><BarChart3 size={20} /><h2>Analytics</h2></div>
          <DataPills items={data.analyticsEvents.slice(0, 8).map((item) => `${item.event_name}: ${item.aggregate_type}`)} empty="Không có sự kiện thống kê." />
        </section>
        <section className="panel">
          <div className="panel-title"><ShieldCheck size={20} /><h2>Bản đồ Microservices</h2></div>
          <DataPills items={Object.entries(serviceUrls).map(([service, url]) => `${service}: ${url.replace("http://localhost:", ":")}`)} />
        </section>
      </section>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function MetricCard({ icon, label, value }: { icon: JSX.Element; label: string; value: string | number }) {
  return (
    <section className="metric-card">
      <div>{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
    </section>
  );
}

function LineStack({ children }: { children: React.ReactNode }) {
  return <div className="line-stack">{children}</div>;
}

function DataPills({ items, empty = "Không có dữ liệu." }: { items: string[]; empty?: string }) {
  if (!items.length) return <span className="muted">{empty}</span>;
  return <div className="small-list">{items.map((item) => <span key={item}>{item}</span>)}</div>;
}

function OrderList({
  title,
  orders,
  payments,
  shipments
}: {
  title: string;
  orders: Order[];
  payments: Payment[];
  shipments: Shipment[];
}) {
  return (
    <section className="panel">
      <div className="panel-title"><PackageCheck size={20} /><h2>{title}</h2></div>
      <div className="order-board compact-board">
        {orders.map((order) => {
          const payment = payments.find((item) => item.order_id === order.id);
          const shipment = shipments.find((item) => item.order_id === order.id);
          return (
            <article className="order-card" key={order.id}>
              <div className="order-head">
                <div><strong>Mã Đơn {order.id.slice(0, 8)}</strong><span>{order.status} / {new Date(order.created_at).toLocaleString()}</span></div>
                <b>{money(order.grand_total, order.currency)}</b>
              </div>
              <div className="line-stack compact">
                {order.lines.map((line) => <span key={line.id}>{line.quantity}x {line.product_name} / {line.sku}</span>)}
              </div>
              <div className="order-meta">
                <span>Thanh toán: {payment?.status || "Chưa tạo"}</span>
                <span>Vận chuyển: {shipment?.status || "Chờ xử lý"}</span>
              </div>
            </article>
          );
        })}
        {!orders.length && <span className="muted">Không có đơn hàng nào.</span>}
      </div>
    </section>
  );
}

function EmptyState({ icon, title, text }: { icon: JSX.Element; title: string; text: string }) {
  return (
    <div className="empty-state">
      {icon}
      <strong>{title}</strong>
      <span>{text}</span>
    </div>
  );
}
