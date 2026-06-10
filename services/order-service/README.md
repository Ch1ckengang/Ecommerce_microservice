# Order Service

- Database: PostgreSQL only
- Models: `Order`, `OrderItem`
- Cross-service references use scalar IDs only: `user_id`, `product_id`
- Internal FK is allowed only inside this service: `OrderItem -> Order`
