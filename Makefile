COMPOSE=docker compose
PYTHON=$(if $(wildcard $(CURDIR)/.venv/bin/python),$(CURDIR)/.venv/bin/python,python3)

.PHONY: build up down logs ps restart verify ci-backend test test-all test-health test-api test-container-api test-container-unit test-container-all test-product test-user test-cart test-order test-payment test-shipping test-product-api test-user-api test-cart-api test-order-api test-payment-api test-shipping-api test-product-all test-user-all test-cart-all test-order-all test-payment-all test-shipping-all test-product-api-container test-user-api-container test-cart-api-container test-order-api-container test-payment-api-container test-shipping-api-container test-cart-unit-container test-order-unit-container test-payment-unit-container test-shipping-unit-container test-product-all-container test-user-all-container test-cart-all-container test-order-all-container test-payment-all-container test-shipping-all-container

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

restart:
	$(COMPOSE) down
	$(COMPOSE) up --build

verify:
	python3 -m compileall services

ci-backend:
	@set -e; \
	trap '$(COMPOSE) down' EXIT; \
	$(COMPOSE) up --build -d; \
	$(MAKE) verify; \
	$(MAKE) test-container-api; \
	$(MAKE) test-container-unit

test: test-all

test-all:
	$(MAKE) test-product-all
	$(MAKE) test-user-all
	$(MAKE) test-cart-all
	$(MAKE) test-order-all
	$(MAKE) test-payment-all
	$(MAKE) test-shipping-all

test-health:
	$(MAKE) test-product
	$(MAKE) test-user
	$(MAKE) test-cart
	$(MAKE) test-order
	$(MAKE) test-payment
	$(MAKE) test-shipping

test-api:
	$(MAKE) test-product-api
	$(MAKE) test-user-api
	$(MAKE) test-cart-api
	$(MAKE) test-order-api
	$(MAKE) test-payment-api
	$(MAKE) test-shipping-api

test-container-api:
	$(MAKE) test-product-api-container
	$(MAKE) test-user-api-container
	$(MAKE) test-cart-api-container
	$(MAKE) test-order-api-container
	$(MAKE) test-payment-api-container
	$(MAKE) test-shipping-api-container

test-container-unit:
	$(MAKE) test-cart-unit-container
	$(MAKE) test-order-unit-container
	$(MAKE) test-payment-unit-container
	$(MAKE) test-shipping-unit-container

test-container-all:
	$(MAKE) test-product-all-container
	$(MAKE) test-user-all-container
	$(MAKE) test-cart-all-container
	$(MAKE) test-order-all-container
	$(MAKE) test-payment-all-container
	$(MAKE) test-shipping-all-container

test-product:
	cd services/product-service && "$(PYTHON)" manage.py test products.tests.test_health

test-product-api:
	cd services/product-service && "$(PYTHON)" manage.py test products.tests.test_api

test-product-all:
	cd services/product-service && "$(PYTHON)" manage.py test products.tests

test-product-api-container:
	$(COMPOSE) exec product-service python manage.py test products.tests.test_api

test-product-all-container:
	$(COMPOSE) exec product-service python manage.py test products.tests

test-user:
	cd services/user-service && "$(PYTHON)" manage.py test users.tests.test_health

test-user-api:
	cd services/user-service && "$(PYTHON)" manage.py test users.tests.test_api

test-user-all:
	cd services/user-service && "$(PYTHON)" manage.py test users.tests

test-user-api-container:
	$(COMPOSE) exec user-service python manage.py test users.tests.test_api

test-user-all-container:
	$(COMPOSE) exec user-service python manage.py test users.tests

test-cart:
	cd services/cart-service && "$(PYTHON)" manage.py test carts.tests.test_health

test-cart-api:
	cd services/cart-service && "$(PYTHON)" manage.py test carts.tests.test_api

test-cart-all:
	cd services/cart-service && "$(PYTHON)" manage.py test carts.tests

test-cart-api-container:
	$(COMPOSE) exec cart-service python manage.py test carts.tests.test_api

test-cart-all-container:
	$(COMPOSE) exec cart-service python manage.py test carts.tests

test-order:
	cd services/order-service && "$(PYTHON)" manage.py test orders.tests.test_health

test-order-api:
	cd services/order-service && "$(PYTHON)" manage.py test orders.tests.test_api

test-order-all:
	cd services/order-service && "$(PYTHON)" manage.py test orders.tests

test-order-api-container:
	$(COMPOSE) exec order-service python manage.py test orders.tests.test_api

test-order-all-container:
	$(COMPOSE) exec order-service python manage.py test orders.tests

test-payment:
	cd services/payment-service && "$(PYTHON)" manage.py test payments.tests.test_health

test-payment-api:
	cd services/payment-service && "$(PYTHON)" manage.py test payments.tests.test_api

test-payment-all:
	cd services/payment-service && "$(PYTHON)" manage.py test payments.tests

test-payment-api-container:
	$(COMPOSE) exec payment-service python manage.py test payments.tests.test_api

test-cart-unit-container:
	$(COMPOSE) exec cart-service python manage.py test carts.tests.test_services carts.tests.test_serializers

test-order-unit-container:
	$(COMPOSE) exec order-service python manage.py test orders.tests.test_services orders.tests.test_serializers orders.tests.test_product_client

test-payment-unit-container:
	$(COMPOSE) exec payment-service python manage.py test payments.tests.test_services payments.tests.test_serializers payments.tests.test_order_client

test-shipping-unit-container:
	$(COMPOSE) exec shipping-service python manage.py test shipments.tests.test_services shipments.tests.test_serializers shipments.tests.test_order_client

test-payment-all-container:
	$(COMPOSE) exec payment-service python manage.py test payments.tests

test-shipping:
	cd services/shipping-service && "$(PYTHON)" manage.py test shipments.tests.test_health

test-shipping-api:
	cd services/shipping-service && "$(PYTHON)" manage.py test shipments.tests.test_api

test-shipping-all:
	cd services/shipping-service && "$(PYTHON)" manage.py test shipments.tests

test-shipping-api-container:
	$(COMPOSE) exec shipping-service python manage.py test shipments.tests.test_api

test-shipping-all-container:
	$(COMPOSE) exec shipping-service python manage.py test shipments.tests
