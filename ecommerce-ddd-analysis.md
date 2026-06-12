# Phân tích chức năng hệ thống ecommerce theo DDD

## 1. Xác định chức năng hệ thống

Hệ thống ecommerce được thiết kế theo hướng microservice cần được nhìn nhận không chỉ là tập hợp các màn hình hoặc API CRUD, mà là tập hợp các năng lực nghiệp vụ độc lập. Mỗi chức năng nên có trách nhiệm rõ ràng, dữ liệu sở hữu riêng, và giao tiếp với các phần khác thông qua API hoặc domain event.

### 1.1. Quản lý sản phẩm

Chức năng quản lý sản phẩm chịu trách nhiệm quản lý thông tin sản phẩm được bán trên hệ thống.

Các nghiệp vụ chính:

- Tạo, cập nhật, xóa mềm sản phẩm.
- Quản lý SKU, tên sản phẩm, mô tả, hình ảnh, thương hiệu, trạng thái bán.
- Quản lý danh mục sản phẩm.
- Quản lý thuộc tính sản phẩm theo từng nhóm domain như sách, điện tử, thời trang.
- Công bố hoặc ẩn sản phẩm khỏi kênh bán hàng.

Với hệ thống đa domain, sản phẩm không nên bị ép vào một model cứng duy nhất. Ví dụ:

- Book: tác giả, nhà xuất bản, ISBN, số trang, ngôn ngữ.
- Electronics: hãng sản xuất, model, thông số kỹ thuật, bảo hành.
- Fashion: kích cỡ, màu sắc, chất liệu, giới tính, bộ sưu tập.

Catalog chỉ nên quản lý thông tin mô tả sản phẩm. Các phần như tồn kho, giá bán, khuyến mãi, đánh giá và tìm kiếm nên được tách sang các bounded context riêng nếu nghiệp vụ đủ lớn.

### 1.2. Quản lý người dùng

Chức năng quản lý người dùng chịu trách nhiệm định danh, xác thực, phân quyền và quản lý hồ sơ người dùng.

Các nhóm người dùng chính:

- Admin: quản trị toàn hệ thống, cấu hình nghiệp vụ, quản lý nhân sự.
- Staff: vận hành sản phẩm, đơn hàng, kho, giao hàng, chăm sóc khách hàng.
- Customer: người mua hàng, quản lý hồ sơ cá nhân, địa chỉ, đơn hàng.

Các nghiệp vụ chính:

- Đăng ký, đăng nhập, đăng xuất.
- Quản lý thông tin tài khoản.
- Quản lý vai trò và quyền hạn.
- Quản lý hồ sơ khách hàng.
- Quản lý địa chỉ giao hàng.
- Khóa, mở khóa hoặc vô hiệu hóa tài khoản.

Nên tách rõ Identity & Access Management khỏi Customer Profile. Identity quản lý đăng nhập và quyền truy cập, còn Customer quản lý dữ liệu nghiệp vụ của người mua.

### 1.3. Giỏ hàng

Giỏ hàng đại diện cho ý định mua hàng tạm thời của khách hàng trước khi tạo đơn hàng.

Các nghiệp vụ chính:

- Thêm sản phẩm vào giỏ.
- Xóa sản phẩm khỏi giỏ.
- Cập nhật số lượng.
- Lưu giỏ hàng theo khách hàng hoặc phiên truy cập.
- Kiểm tra sơ bộ tình trạng sản phẩm.
- Chuẩn bị dữ liệu checkout.

Cart không nên quyết định cuối cùng về giá, tồn kho hoặc khuyến mãi. Khi checkout, hệ thống cần xác thực lại với Pricing, Promotion và Inventory để tránh sai lệch dữ liệu.

### 1.4. Đặt hàng

Đặt hàng là năng lực trung tâm của hệ thống ecommerce. Order ghi nhận cam kết mua hàng của khách tại một thời điểm cụ thể.

Các nghiệp vụ chính:

- Tạo đơn hàng từ giỏ hàng.
- Lưu snapshot sản phẩm, giá, khuyến mãi và địa chỉ tại thời điểm đặt hàng.
- Quản lý trạng thái đơn hàng.
- Hủy đơn hàng.
- Theo dõi tiến trình xử lý đơn.
- Phối hợp với thanh toán, tồn kho và giao hàng.

Một vòng đời đơn hàng tham khảo:

- PendingPayment: chờ thanh toán.
- Paid: đã thanh toán.
- Confirmed: đã xác nhận.
- Packed: đã đóng gói.
- Shipped: đã giao cho đơn vị vận chuyển.
- Completed: hoàn tất.
- Cancelled: đã hủy.
- Refunded: đã hoàn tiền.

Order không nên chứa toàn bộ logic của payment, shipping, inventory. Thay vào đó, Order nên phản ứng với event như PaymentSucceeded, StockReserved hoặc ShipmentDelivered.

### 1.5. Thanh toán

Payment chịu trách nhiệm xử lý giao dịch thanh toán, trạng thái giao dịch và tích hợp với cổng thanh toán.

Các nghiệp vụ chính:

- Tạo payment intent hoặc payment request.
- Ghi nhận giao dịch thanh toán.
- Xử lý webhook từ cổng thanh toán.
- Xác nhận thanh toán thành công hoặc thất bại.
- Hỗ trợ hoàn tiền.
- Hỗ trợ idempotency để tránh ghi nhận trùng giao dịch.

Payment không nên trực tiếp sửa dữ liệu nội bộ của Order. Sau khi thanh toán thành công hoặc thất bại, Payment nên phát domain event để Order cập nhật trạng thái tương ứng.

### 1.6. Giao hàng

Shipping hoặc Fulfillment chịu trách nhiệm xử lý quá trình giao hàng sau khi đơn hàng đủ điều kiện xử lý.

Các nghiệp vụ chính:

- Tạo shipment cho đơn hàng.
- Chọn phương thức vận chuyển.
- Tích hợp với đơn vị vận chuyển.
- Quản lý mã vận đơn.
- Theo dõi trạng thái vận chuyển.
- Xác nhận giao hàng thành công hoặc thất bại.

Nên phân biệt giữa Fulfillment và Carrier Integration:

- Fulfillment: xử lý đóng gói, chuẩn bị hàng, bàn giao vận chuyển.
- Carrier Integration: tích hợp API với các đơn vị vận chuyển bên ngoài.

### 1.7. Tìm kiếm và gợi ý sản phẩm

Search và Recommendation là các chức năng đọc dữ liệu phục vụ trải nghiệm mua hàng.

Các nghiệp vụ chính của Search:

- Tìm kiếm sản phẩm theo từ khóa.
- Lọc theo danh mục, giá, thương hiệu, thuộc tính.
- Sắp xếp theo độ liên quan, giá, lượt bán, đánh giá.
- Đồng bộ chỉ mục tìm kiếm từ Catalog, Pricing và Inventory.

Các nghiệp vụ chính của Recommendation:

- Gợi ý sản phẩm theo lịch sử xem.
- Gợi ý theo hành vi thêm vào giỏ.
- Gợi ý theo lịch sử mua hàng.
- Gợi ý sản phẩm tương tự hoặc thường được mua cùng nhau.

Search không nên truy vấn trực tiếp đồng thời nhiều service khi người dùng tìm kiếm. Thay vào đó, nên xây dựng read model hoặc search index riêng, được cập nhật bất đồng bộ qua event.

### 1.8. Các chức năng nên bổ sung

Ngoài các chức năng ban đầu, hệ thống ecommerce thực tế thường cần thêm các năng lực sau:

- Inventory: quản lý tồn kho, giữ hàng, trừ hàng, hoàn hàng về kho.
- Pricing & Promotion: quản lý giá bán, coupon, voucher, flash sale, rule khuyến mãi.
- Review & Rating: đánh giá sản phẩm, kiểm duyệt review, xác thực người đã mua.
- Wishlist: lưu danh sách sản phẩm yêu thích.
- Notification: gửi email, SMS, push notification, thông báo trong ứng dụng.
- Return, Refund & Cancellation: xử lý hủy đơn, đổi trả, hoàn tiền.
- Admin Backoffice: màn hình vận hành cho admin và staff.
- Audit Log: ghi nhận lịch sử thao tác quan trọng.
- Analytics & Reporting: báo cáo doanh thu, đơn hàng, sản phẩm bán chạy, hành vi người dùng.

## 2. Phân rã hệ thống theo DDD

DDD khuyến khích phân rã hệ thống theo bounded context. Mỗi bounded context là một vùng nghiệp vụ có mô hình, ngôn ngữ và quy tắc riêng. Trong kiến trúc microservice, một bounded context thường có thể ánh xạ thành một service, nhưng không bắt buộc phải tách service ngay từ đầu nếu hệ thống còn nhỏ.

### 2.1. Nguyên tắc phân rã

Các nguyên tắc nên áp dụng:

- Phân rã theo năng lực nghiệp vụ, không phân rã theo bảng dữ liệu.
- Mỗi bounded context sở hữu dữ liệu riêng.
- Không chia sẻ database giữa các service.
- Giao tiếp đồng bộ qua API khi cần phản hồi ngay.
- Giao tiếp bất đồng bộ qua event khi xử lý quy trình dài hoặc cần giảm coupling.
- Aggregate chỉ nên bảo vệ invariant trong phạm vi nhỏ, tránh aggregate quá lớn.
- Dùng Saga hoặc Process Manager cho các flow liên quan nhiều service như checkout.

### 2.2. Catalog Context

Catalog Context quản lý thông tin mô tả sản phẩm.

Trách nhiệm:

- Quản lý sản phẩm.
- Quản lý danh mục.
- Quản lý thuộc tính sản phẩm theo từng ngành hàng.
- Quản lý trạng thái hiển thị sản phẩm.

Aggregate gợi ý:

- Product
- Category
- ProductVariant

Event gợi ý:

- ProductCreated
- ProductUpdated
- ProductPublished
- ProductUnpublished
- ProductCategoryChanged

Không nên đặt trong Catalog:

- Tồn kho thực tế.
- Rule khuyến mãi.
- Giao dịch thanh toán.
- Trạng thái giao hàng.

### 2.3. Inventory Context

Inventory Context quản lý số lượng hàng hóa và khả năng đáp ứng đơn hàng.

Trách nhiệm:

- Quản lý tồn kho theo SKU.
- Quản lý tồn kho theo kho hàng nếu có nhiều warehouse.
- Giữ hàng khi checkout.
- Giải phóng hàng khi đơn bị hủy hoặc thanh toán thất bại.
- Trừ hàng khi đơn được xác nhận.

Aggregate gợi ý:

- StockItem
- StockReservation
- Warehouse

Event gợi ý:

- StockReserved
- StockReservationFailed
- StockReleased
- StockDeducted
- StockReplenished

Inventory là context quan trọng vì liên quan trực tiếp đến overselling. Các thao tác reserve stock cần có idempotency và kiểm soát concurrency.

### 2.4. Pricing & Promotion Context

Pricing & Promotion Context quản lý giá và các chính sách giảm giá.

Trách nhiệm:

- Quản lý giá niêm yết.
- Quản lý giá bán.
- Quản lý coupon, voucher.
- Quản lý chương trình khuyến mãi.
- Tính toán discount tại thời điểm checkout.

Aggregate gợi ý:

- PriceBook
- PromotionCampaign
- Coupon
- DiscountRule

Event gợi ý:

- PriceChanged
- PromotionStarted
- PromotionEnded
- CouponRedeemed

Order nên lưu snapshot kết quả tính giá, không nên phụ thuộc vào giá động sau khi đơn đã được tạo.

### 2.5. Identity & Access Context

Identity & Access Context quản lý đăng nhập và phân quyền.

Trách nhiệm:

- Xác thực người dùng.
- Quản lý tài khoản.
- Quản lý vai trò.
- Quản lý quyền truy cập.
- Phát hành token hoặc session.

Aggregate gợi ý:

- UserAccount
- Role
- Permission

Event gợi ý:

- UserRegistered
- UserRoleChanged
- UserLocked
- UserUnlocked

Context này nên tập trung vào bảo mật và quyền truy cập, không nên chứa toàn bộ thông tin nghiệp vụ của customer.

### 2.6. Customer Context

Customer Context quản lý dữ liệu nghiệp vụ của khách hàng.

Trách nhiệm:

- Quản lý hồ sơ khách hàng.
- Quản lý địa chỉ giao hàng.
- Quản lý wishlist nếu phạm vi nhỏ.
- Lưu một số preference phục vụ trải nghiệm mua hàng.

Aggregate gợi ý:

- Customer
- Address
- Wishlist

Event gợi ý:

- CustomerProfileUpdated
- CustomerAddressAdded
- CustomerAddressChanged
- ProductAddedToWishlist

### 2.7. Cart Context

Cart Context quản lý giỏ hàng trước checkout.

Trách nhiệm:

- Quản lý cart theo customer hoặc session.
- Thêm, xóa, cập nhật item trong giỏ.
- Chuẩn bị dữ liệu checkout.
- Gửi yêu cầu xác thực giá, khuyến mãi và tồn kho khi checkout.

Aggregate gợi ý:

- Cart
- CartItem

Event gợi ý:

- ItemAddedToCart
- ItemRemovedFromCart
- CartUpdated
- CartCheckedOut

Cart không phải nguồn sự thật về giá cuối cùng. Giá hiển thị trong cart chỉ nên xem là thông tin tham khảo cho đến khi checkout được xác nhận.

### 2.8. Order Context

Order Context quản lý đơn hàng và vòng đời đơn hàng.

Trách nhiệm:

- Tạo order từ checkout.
- Lưu snapshot sản phẩm, giá, địa chỉ, phí vận chuyển.
- Quản lý trạng thái order.
- Ghi nhận kết quả thanh toán.
- Ghi nhận kết quả giao hàng.
- Xử lý hủy đơn theo rule nghiệp vụ.

Aggregate gợi ý:

- Order
- OrderLine

Event gợi ý:

- OrderCreated
- OrderConfirmed
- OrderCancelled
- OrderPaid
- OrderShipped
- OrderCompleted

Order nên là aggregate bảo vệ các rule liên quan đến trạng thái đơn hàng. Ví dụ: không cho hủy đơn khi đã giao thành công, không cho chuyển sang Shipped nếu chưa Confirmed.

### 2.9. Payment Context

Payment Context quản lý giao dịch thanh toán.

Trách nhiệm:

- Tạo payment request.
- Tích hợp payment gateway.
- Xử lý callback hoặc webhook.
- Ghi nhận trạng thái giao dịch.
- Hoàn tiền.

Aggregate gợi ý:

- Payment
- PaymentTransaction
- Refund

Event gợi ý:

- PaymentRequested
- PaymentSucceeded
- PaymentFailed
- RefundRequested
- RefundCompleted

Webhook từ cổng thanh toán cần được xử lý idempotent vì cùng một callback có thể được gửi nhiều lần.

### 2.10. Shipping Context

Shipping Context quản lý quá trình vận chuyển.

Trách nhiệm:

- Tạo shipment.
- Chọn đơn vị vận chuyển.
- Ghi nhận mã vận đơn.
- Cập nhật trạng thái giao hàng.
- Đồng bộ trạng thái từ carrier.

Aggregate gợi ý:

- Shipment
- Delivery
- Carrier

Event gợi ý:

- ShipmentCreated
- ShipmentPickedUp
- ShipmentInTransit
- ShipmentDelivered
- ShipmentFailed

Shipping nên nhận dữ liệu cần thiết từ Order dưới dạng snapshot, ví dụ địa chỉ giao hàng và danh sách kiện hàng, thay vì truy vấn sâu vào Order database.

### 2.11. Search Context

Search Context phục vụ truy vấn sản phẩm tốc độ cao.

Trách nhiệm:

- Xây dựng search index.
- Đồng bộ dữ liệu từ Catalog, Pricing, Inventory, Review.
- Tìm kiếm, lọc, sắp xếp sản phẩm.
- Tối ưu truy vấn đọc.

Read model gợi ý:

- SearchProductDocument

Event đầu vào gợi ý:

- ProductUpdated
- PriceChanged
- StockDeducted
- StockReplenished
- ReviewCreated

Search thường là read-side context, phù hợp với CQRS. Dữ liệu trong search index có thể eventual consistency so với dữ liệu gốc.

### 2.12. Recommendation Context

Recommendation Context phục vụ gợi ý sản phẩm cá nhân hóa.

Trách nhiệm:

- Thu thập hành vi người dùng.
- Phân tích sản phẩm đã xem, đã mua, đã thêm vào giỏ.
- Tạo danh sách gợi ý sản phẩm.
- Cung cấp API gợi ý cho giao diện người dùng.

Event đầu vào gợi ý:

- ProductViewed
- ItemAddedToCart
- OrderCompleted
- ProductAddedToWishlist

Recommendation nên được tách khỏi Search vì mục tiêu nghiệp vụ khác nhau. Search trả lời nhu cầu chủ động của người dùng, Recommendation chủ động đề xuất sản phẩm phù hợp.

### 2.13. Notification Context

Notification Context quản lý việc gửi thông báo.

Trách nhiệm:

- Gửi email, SMS, push notification.
- Quản lý template thông báo.
- Gửi thông báo theo event nghiệp vụ.
- Theo dõi trạng thái gửi.

Event đầu vào gợi ý:

- OrderCreated
- PaymentSucceeded
- PaymentFailed
- ShipmentDelivered
- RefundCompleted

Notification nên là subscriber của các domain event. Các service khác không nên tự triển khai logic gửi email hoặc SMS.

### 2.14. Return & Refund Context

Return & Refund Context quản lý đổi trả và hoàn tiền sau bán hàng.

Trách nhiệm:

- Tạo yêu cầu trả hàng.
- Duyệt hoặc từ chối yêu cầu trả hàng.
- Theo dõi hàng hoàn về kho.
- Phối hợp hoàn tiền với Payment.
- Cập nhật trạng thái hậu mãi của đơn hàng.

Aggregate gợi ý:

- ReturnRequest
- RefundRequest

Event gợi ý:

- ReturnRequested
- ReturnApproved
- ReturnRejected
- ReturnReceived
- RefundRequested
- RefundCompleted

Context này nên được tách riêng khi nghiệp vụ hậu mãi phức tạp, đặc biệt với marketplace hoặc sản phẩm có chính sách đổi trả khác nhau.

### 2.15. Admin Backoffice Context

Admin Backoffice cung cấp công cụ vận hành cho admin và staff.

Trách nhiệm:

- Quản lý nhân sự vận hành.
- Duyệt sản phẩm.
- Theo dõi đơn hàng.
- Xử lý khiếu nại.
- Cấu hình hệ thống.
- Xem báo cáo vận hành.

Backoffice có thể gọi API từ nhiều bounded context khác, nhưng không nên sở hữu trực tiếp toàn bộ dữ liệu nghiệp vụ của các context đó.

### 2.16. Analytics & Reporting Context

Analytics & Reporting phục vụ báo cáo và phân tích.

Trách nhiệm:

- Tổng hợp doanh thu.
- Báo cáo đơn hàng.
- Báo cáo sản phẩm bán chạy.
- Theo dõi conversion funnel.
- Phân tích hành vi người dùng.

Context này nên lấy dữ liệu qua event stream, data pipeline hoặc replica phục vụ phân tích. Không nên query trực tiếp database vận hành của từng service cho báo cáo nặng.

## 3. Gợi ý phân rã microservice

Với hệ thống đầy đủ, có thể phân rã thành các service sau:

```text
identity-service
customer-service
catalog-service
inventory-service
pricing-promotion-service
cart-service
order-service
payment-service
shipping-service
search-service
recommendation-service
review-service
notification-service
return-refund-service
admin-backoffice-service
analytics-service
```

Với MVP, nên bắt đầu nhỏ hơn để giảm chi phí vận hành:

```text
identity-service
catalog-service
inventory-service
cart-service
order-service
payment-service
shipping-service
search-service
notification-service
```

Các context như recommendation, review, refund, promotion và analytics có thể được tách sau khi nghiệp vụ phát sinh đủ rõ.

## 4. Luồng checkout tham khảo

Một luồng checkout theo hướng event-driven có thể diễn ra như sau:

1. Customer checkout cart.
2. Cart gửi yêu cầu tạo checkout.
3. Pricing & Promotion tính giá cuối cùng.
4. Inventory reserve stock.
5. Order tạo đơn hàng ở trạng thái PendingPayment.
6. Payment tạo payment request.
7. Payment nhận webhook từ gateway.
8. Nếu thanh toán thành công, Payment phát PaymentSucceeded.
9. Order chuyển sang Paid hoặc Confirmed.
10. Inventory deduct stock.
11. Shipping tạo shipment.
12. Notification gửi thông báo cho khách hàng.

Nếu thanh toán thất bại:

1. Payment phát PaymentFailed.
2. Order chuyển sang PaymentFailed hoặc Cancelled theo rule.
3. Inventory release stock.
4. Notification gửi thông báo thanh toán thất bại.

Luồng này nên dùng Saga hoặc Process Manager để điều phối, vì nó đi qua nhiều bounded context và có khả năng thất bại ở nhiều bước.

## 5. Các lưu ý kỹ thuật quan trọng

- Sử dụng idempotency key cho checkout, payment callback, order creation và refund.
- Dùng optimistic locking hoặc cơ chế tương đương cho tồn kho.
- Lưu snapshot dữ liệu quan trọng trong Order để tránh bị ảnh hưởng khi Product hoặc Price thay đổi sau này.
- Dùng domain event để đồng bộ Search, Recommendation, Notification và Analytics.
- Thiết kế retry và dead-letter queue cho message processing.
- Không để một service đọc trực tiếp database của service khác.
- Không gom mọi logic vào Order Service.
- Không thiết kế Product model quá tổng quát khiến mọi ngành hàng đều khó mở rộng.
- Cân nhắc CQRS cho các use case đọc nhiều như search, product listing, reporting.

## 6. Kết luận

Danh sách chức năng ban đầu gồm sản phẩm, người dùng, giỏ hàng, đặt hàng, thanh toán, giao hàng, tìm kiếm và gợi ý là nền tảng hợp lý cho hệ thống ecommerce. Tuy nhiên, khi áp dụng DDD và microservice, nên phân rã sâu hơn theo bounded context để tránh service quá lớn và giảm coupling giữa các nghiệp vụ.

Hướng thiết kế phù hợp là bắt đầu với các context cốt lõi như Catalog, Inventory, Cart, Order, Payment, Shipping và Identity. Sau đó mở rộng dần sang Pricing & Promotion, Review, Recommendation, Return & Refund, Notification và Analytics khi hệ thống phát triển.
