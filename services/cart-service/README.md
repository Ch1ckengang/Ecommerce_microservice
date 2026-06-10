# Cart Service

- Database: MySQL only
- Models: `Cart`, `CartItem`
- Cross-service references use scalar IDs only: `user_id`, `product_id`
- Internal FK is allowed only inside this service: `CartItem -> Cart`
