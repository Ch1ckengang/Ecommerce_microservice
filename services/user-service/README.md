# User Service

`user-service` is a standalone Django + DRF microservice for identity and authentication.

Architecture:

- `views` handle HTTP input/output.
- `services` contain business logic.
- `models` map directly to MySQL tables.

Rules:

- This service connects to one MySQL database only.
- It does not create ForeignKey links to other services.
- Other services must use `user_id` values only, never cross-service joins.
