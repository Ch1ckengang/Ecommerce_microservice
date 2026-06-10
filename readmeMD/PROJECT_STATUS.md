# Project Status

## Overview

This repository currently contains a Django microservices-based e-commerce backend in a monorepo layout:

- `api-gateway/`
- `frontend/`
- `services/product-service/`
- `services/user-service/`
- `services/cart-service/`
- `services/order-service/`
- `services/payment-service/`
- `services/shipping-service/`
- `docker-compose.yml`
- `.env`

The implementation follows the requested architectural baseline:

- Monorepo structure
- Database per service
- PostgreSQL used by `product-service`, `order-service`, `payment-service`
- MySQL used by `user-service`, `cart-service`, `shipping-service`
- No cross-service foreign keys
- Inter-service references stored as scalar IDs only
- Layering style: `views -> services -> models`
- Docker and Docker Compose setup
- Nginx API gateway
- Environment-variable based service configuration
- Dedicated health endpoints for each Django service

## What Has Been Implemented

### 1. Product Service

Location:

- `services/product-service/`

Implemented:

- Django project `product_service`
- App `products`
- Models:
  - `Category`
  - `Product`
- Internal relationship:
  - `Product.category -> Category`
- DRF serializers, service layer, CRUD views, URLs
- CRUD for both `Category` and `Product`
- Pagination and filtering
- PostgreSQL configuration through environment variables
- Dockerfile and startup entrypoint
- Initial migration
- Seed command for local development

Important rule:

- The `Category -> Product` relation is inside one service and one database, so the foreign key is valid.

### 2. User Service

Location:

- `services/user-service/`

Implemented:

- Standalone Django service on MySQL
- Custom `User` model
- Django auth integration
- JWT authentication with `djangorestframework-simplejwt`
- Endpoints for:
  - registration
  - token obtain
  - token refresh
  - current profile read/update
- Dockerfile and startup entrypoint
- Initial migration

Important rule:

- Other services must store `user_id` only. They must not reference `user-service` via foreign key.

### 3. Cart Service

Location:

- `services/cart-service/`

Implemented:

- Standalone Django service on MySQL
- Models:
  - `Cart`
  - `CartItem`
- Internal relationship:
  - `CartItem.cart -> Cart`
- Cross-service references:
  - `Cart.user_id`
  - `CartItem.product_id`
- CRUD views for carts and cart items
- Pagination and simple filtering
- Dockerfile and startup entrypoint
- Initial migration

### 4. Order Service

Location:

- `services/order-service/`

Implemented:

- Standalone Django service on PostgreSQL
- Models:
  - `Order`
  - `OrderItem`
- Internal relationship:
  - `OrderItem.order -> Order`
- Cross-service references:
  - `Order.user_id`
  - `OrderItem.product_id`
- CRUD views for orders and order items
- Pagination and simple filtering
- Dockerfile and startup entrypoint
- Initial migration

### 5. Payment Service

Location:

- `services/payment-service/`

Implemented:

- Standalone Django service on PostgreSQL
- Model:
  - `Payment`
- Cross-service reference:
  - `Payment.order_id`
- CRUD views
- Pagination and simple filtering
- Dockerfile and startup entrypoint
- Initial migration

### 6. Shipping Service

Location:

- `services/shipping-service/`

Implemented:

- Standalone Django service on MySQL
- Model:
  - `Shipment`
- Cross-service reference:
  - `Shipment.order_id`
- CRUD views
- Pagination and simple filtering
- Dockerfile and startup entrypoint
- Initial migration

### 7. API Gateway

Location:

- `api-gateway/conf.d/default.conf`

Implemented:

- Nginx gateway container
- Routing rules:
  - `/users/` -> `user-service`
  - `/products/` -> `product-service`
  - `/cart/` -> `cart-service`
  - `/orders/` -> `order-service`
  - `/payments/` -> `payment-service`
  - `/shipping/` -> `shipping-service`

### 8. Compose and Environment Setup

Implemented:

- Root `.env` with namespaced variables per service database
- `docker-compose.yml` with:
  - 6 application containers
  - 6 database containers
  - 1 nginx gateway container
- Per-service DB connection via service container names on the Docker network
- Application containers now receive only their own DB connection variables explicitly through `environment`
- Container healthchecks now exist for all databases, all Django services, and the nginx gateway
- Database containers are no longer bound to host ports; they are internal to the Docker network only

### 9. Developer Tooling

Implemented:

- Root `Makefile` for common Docker and test commands
- Root `Makefile` now supports:
  - health-only checks (`test-health`)
  - per-service API checks (`test-api`, plus per-service `*-api` targets)
  - full per-service suites (`test-all`, alias `test`)
  - containerized API/full suite checks (`test-container-api`, `test-container-all`, plus per-service `*-container` targets)
  - CI helper target (`ci-backend`) to run `verify` + containerized API suite with automatic compose teardown
- GitHub Actions workflow added for backend CI (`.github/workflows/backend-ci.yml`) using `make ci-backend`
- Per-service `.dockerignore` files
- Baseline smoke tests for service health endpoints
- API test coverage now includes `product`, `user`, `cart`, `order`, `payment`, and `shipping`
- Product API tests now cover create/list/detail/update/delete paths plus core filter/validation edge cases
- Cart and order API tests now cover update/delete/not-found and filter edge cases for parent and item endpoints
- Payment and shipping API tests now cover ownership-verification edge cases (`401/403/404/unavailable`) plus detail/update/delete flows
- Cart, order, payment, and shipping now include unit-level tests for `services.py` and `serializers.py`
- Cart, order, payment, and shipping API tests now include auth edge cases for missing/invalid tokens (matching current `403` behavior)

### 10. API Contract Hardening

Implemented:

- Standard response envelope added across services
- Standard error envelope added through DRF exception handlers
- JWT validation added to `cart-service`, `order-service`, `payment-service`, and `shipping-service`
- Ownership enforcement added where local service data is sufficient:
  - `cart-service` by `cart.user_id`
  - `order-service` by `order.user_id`
- Ownership enforcement added for:
  - `payment-service` through REST verification against `order-service`
  - `shipping-service` through REST verification against `order-service`
- List ownership verification for `payment-service` and `shipping-service` optimized via batch verification endpoint in `order-service` (`/orders/ownership/verify-batch/`)

### 11. Runtime Validation

Implemented and verified:

- Full `docker compose up --build -d` startup completed successfully
- All databases, all Django services, and the nginx gateway reached healthy state
- HTTP smoke checks passed for:
  - gateway health
  - product listing
  - user registration
  - JWT token issuance
  - cart creation
  - order creation
  - payment creation with ownership verification
  - shipment creation with ownership verification

Runtime issues fixed during validation:

- Removed database host port publishing to avoid host port collisions
- Fixed executable permission issue for bind-mounted `entrypoint.sh` files
- Fixed missing `_get_token()` helper access in payment/shipping list-create views
- Added MySQL test database grants for Django test runner compatibility

### 12. Order-Stock + Security Hardening (Latest)

Implemented:

- `order-service` now supports stock-aware order creation in `POST /orders/` when `order_items` is provided.
- `OrderSerializer` now accepts write-only `order_items` payload for integrated order creation.
- Order flow now performs stock check + stock reserve before saving order and items.
- If DB write fails after stock reservation, stock release is triggered automatically.
- Added tests for stock-aware creation success, insufficient stock rejection, and rollback release behavior.

Security improvements:

- Product stock endpoints are now protected by internal service token permission:
  - `POST /products/stock/check/`
  - `POST /products/stock/reserve/`
  - `POST /products/stock/release/`
- Added `InternalServiceTokenPermission` in `product-service`.
- `order-service` now sends `X-Service-Token` to product stock endpoints via `ProductServiceClient`.

Environment and secret hygiene improvements:

- Added `.env` ignore rules in `.gitignore` while keeping `.env.example` tracked.
- Added `SERVICE_INTERNAL_TOKEN` to `.env.example`.
- Wired secret variables in `docker-compose.yml`:
  - `JWT_SECRET_KEY` for user/cart/order/payment/shipping services
  - `JWT_ACCESS_TOKEN_LIFETIME`, `JWT_REFRESH_TOKEN_LIFETIME` for `user-service`
  - `INTERNAL_SERVICE_TOKEN` for `product-service`
  - `PRODUCT_SERVICE_TOKEN` for `order-service`
- Non-user services now validate JWT using `JWT_SIGNING_KEY` derived from `JWT_SECRET_KEY`.

### 13. High-Priority Reliability Work (Latest)

Implemented:

- Idempotency for create flows via `Idempotency-Key` header:
  - `POST /orders/`
  - `POST /payments/`
  - `POST /shipping/`
- Replay behavior now returns the previously created record without duplicate side effects.
- Added persistent `idempotency_key` fields and migrations for:
  - `Order`
  - `Payment`
  - `Shipment`

Implemented resilience improvements:

- Added bounded retry/backoff for `order-service -> product-service` stock calls.
- Added bounded retry/backoff for `payment-service` and `shipping-service` ownership verification calls to `order-service`.
- Added environment-driven retry tuning:
  - `PRODUCT_SERVICE_MAX_RETRIES`
  - `PRODUCT_SERVICE_RETRY_BACKOFF`
  - `ORDER_SERVICE_MAX_RETRIES`
  - `ORDER_SERVICE_RETRY_BACKOFF`

## Current Endpoint Summary

### Health Endpoints

- `GET /health/` on each Django service container
- `GET /health/` on the nginx gateway

### Product Service

- `GET /products/categories/`
- `POST /products/categories/`
- `GET /products/categories/{id}/`
- `PUT /products/categories/{id}/`
- `DELETE /products/categories/{id}/`
- `GET /products/`
- `POST /products/`
- `GET /products/{id}/`
- `PUT /products/{id}/`
- `DELETE /products/{id}/`
- `POST /products/stock/check/` (requires `X-Service-Token`)
- `POST /products/stock/reserve/` (requires `X-Service-Token`)
- `POST /products/stock/release/` (requires `X-Service-Token`)

### User Service

- `POST /users/register/`
- `POST /users/token/`
- `POST /users/token/refresh/`
- `GET /users/me/`
- `PUT /users/me/`

### Cart Service

- `GET /cart/carts/`
- `POST /cart/carts/`
- `GET /cart/carts/{id}/`
- `PUT /cart/carts/{id}/`
- `DELETE /cart/carts/{id}/`
- `GET /cart/items/`
- `POST /cart/items/`
- `GET /cart/items/{id}/`
- `PUT /cart/items/{id}/`
- `DELETE /cart/items/{id}/`

### Order Service

- `GET /orders/`
- `POST /orders/`
- `POST /orders/ownership/verify-batch/`
- `GET /orders/{id}/`
- `PUT /orders/{id}/`
- `DELETE /orders/{id}/`
- `GET /orders/items/`
- `POST /orders/items/`
- `GET /orders/items/{id}/`
- `PUT /orders/items/{id}/`
- `DELETE /orders/items/{id}/`

Order create note:

- `POST /orders/` now supports optional `order_items` payload for stock-aware order creation.

### Payment Service

- `GET /payments/`
- `POST /payments/`
- `GET /payments/{id}/`
- `PUT /payments/{id}/`
- `DELETE /payments/{id}/`

### Shipping Service

- `GET /shipping/`
- `POST /shipping/`
- `GET /shipping/{id}/`
- `PUT /shipping/{id}/`
- `DELETE /shipping/{id}/`

## Constraints That Must Continue To Be Respected

- Each service must keep exactly one database connection.
- No shared database between services.
- No cross-database joins.
- No cross-service foreign keys.
- Service-to-service references must remain scalar IDs only.
- Business logic should continue to live in `services.py`, not in views.

## Review Notes and Known Gaps

These items are not yet resolved and should guide the next steps:

1. Inter-service failure handling still needs stronger resilience tests (timeout/retry/degraded path).
2. Secret rotation policy is not yet automated (`JWT_SECRET_KEY`, `SERVICE_INTERNAL_TOKEN`).
3. Idempotency strategy for create operations (`orders`, `payments`, `shipping`) is not implemented yet.
4. The `frontend/` directory is still empty.

## Suggested Next Steps

1. Add resilience tests for cross-service failures (stock check/reserve timeout, malformed downstream response, rollback edge cases).
2. Implement bounded retry/backoff strategy in order/payment/shipping service clients.
3. Add idempotency keys for create flows to prevent duplicate side effects.
4. Add CI quality/security gates (Ruff/Black/isort + dependency vulnerability scan).
5. Define secret lifecycle process (rotation, environment source, rollout plan).
6. Start frontend minimum vertical slice: login -> products -> cart -> order -> payment -> shipment tracking.

## Verification Performed So Far

- Python syntax verification with `python3 -m compileall services`
- CI workflow scaffolded for backend regression via GitHub Actions (`.github/workflows/backend-ci.yml`) using `make ci-backend`
- Baseline automated health smoke tests added for all services
- Full API suite executed in one command via `make test-container-api` with all service API suites passing (`69` total tests)
- Product API suite executed in containerized environment (`docker compose exec product-service python manage.py test products.tests.test_api`) with 16 tests passing
- Cart API suite executed in containerized environment (`docker compose exec cart-service python manage.py test carts.tests.test_api`) with 14 tests passing
- Order API suite executed in containerized environment (`docker compose exec order-service python manage.py test orders.tests.test_api`) with 17 tests passing
- Payment API suite executed in containerized environment (`docker compose exec payment-service python manage.py test payments.tests.test_api`) with 10 tests passing
- Shipping API suite executed in containerized environment (`docker compose exec shipping-service python manage.py test shipments.tests.test_api`) with 10 tests passing
- Cart unit-level tests executed in containerized environment (`docker compose exec cart-service python manage.py test carts.tests.test_services carts.tests.test_serializers`) with 17 tests passing
- Order unit-level tests executed in containerized environment (`docker compose exec order-service python manage.py test orders.tests.test_services orders.tests.test_serializers`) with 21 tests passing
- Payment unit-level tests executed in containerized environment (`docker compose exec payment-service python manage.py test payments.tests.test_services payments.tests.test_serializers`) with 9 tests passing
- Shipping unit-level tests executed in containerized environment (`docker compose exec shipping-service python manage.py test shipments.tests.test_services shipments.tests.test_serializers`) with 9 tests passing
- Product API suite re-validated after stock endpoint protection (`make test-product-api-container`) with 17 tests passing
- Order API suite re-validated after order-stock workflow update (`make test-order-api-container`) with 19 tests passing
- Order unit/service/serializer suite re-validated (`make test-order-unit-container`) with 21 tests passing
- Order API suite re-validated after idempotency/reliability updates (`make test-order-api-container`) with 20 tests passing
- Order unit/service/serializer/client suite re-validated (`make test-order-unit-container`) with 22 tests passing
- Payment API suite re-validated after idempotency updates (`make test-payment-api-container`) with 11 tests passing
- Payment unit/service/serializer/client suite re-validated (`make test-payment-unit-container`) with 10 tests passing
- Shipping API suite re-validated after idempotency updates (`make test-shipping-api-container`) with 11 tests passing
- Shipping unit/service/serializer/client suite re-validated (`make test-shipping-unit-container`) with 10 tests passing
- Full runtime validation completed successfully with Docker Compose
- Manual review of:
  - `docker-compose.yml`
  - `.env`
  - nginx gateway config
  - service settings, models, views, and layer separation
- Hardening changes:
  - gateway redirects added for non-trailing-slash prefixes
  - health endpoints added
  - compose environment exposure narrowed per application container
  - compose healthchecks added for app containers and gateway
  - response/error envelopes standardized
  - JWT validation added to non-user private services
  - payment/shipping ownership verification delegated to `order-service` via REST

## Working Rule For Future Changes

Before implementing new features:

1. Check this file first.
2. Keep the database-per-service boundary intact.
3. Avoid introducing any cross-service model relation.
4. Update this file after each meaningful architectural change.
