# Product Service

`product-service` is a standalone Django + DRF microservice for product catalog data.

Architecture:

- `views` handle HTTP input/output only.
- `services` contain business logic.
- `models` map directly to PostgreSQL tables.

Rules:

- This service connects to one PostgreSQL database only.
- `Category` -> `Product` uses an internal ForeignKey because both tables belong to the same service.
- No cross-service ForeignKey is allowed anywhere else in the system.

Environment variables used by this service:

- `DB_NAME=${PRODUCT_DB_NAME}`
- `DB_USER=${PRODUCT_DB_USER}`
- `DB_PASSWORD=${PRODUCT_DB_PASSWORD}`
- `DB_HOST=${PRODUCT_DB_HOST}`
- `DB_PORT=${PRODUCT_DB_PORT}`
