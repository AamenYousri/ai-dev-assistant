---
description: Discover custom SAP Commerce OCC APIs and produce a Postman collection or endpoint inventory.
---

Use the `occ-postman-generator` skill. First look for OpenAPI / Swagger specifications. If none are available, inspect custom OCC controllers and related DTOs / validators. Produce only endpoints and payload fields supported by source evidence. Include HTTP method, path, parameters, request body, response shape, and authentication notes. Use `{{baseUrl}}` and `{{accessToken}}` variables. Do not invent endpoints or call live services. State any unknowns. If an OpenAPI JSON file is available, you may recommend running the included converter script.
