---
name: occ-postman-generator
description: Discover custom SAP Commerce OCC endpoints and help generate accurate Postman collections from source code or OpenAPI specifications.
---

# OCC Postman Generator

## Goal
Create a Postman collection for custom SAP Commerce OCC endpoints without inventing routes or request/response contracts.

## Workflow
1. Prefer an existing OpenAPI / Swagger specification. If one exists, identify its version and use the included `./scripts/openapi_to_postman.py` helper for OpenAPI 3.x JSON input (YAML requires PyYAML; Swagger 2.0 can be imported through Postman or converted to OpenAPI 3.x first).
2. If no specification exists, inspect the source code. Search custom OCC controllers, annotations, request mappings, facade/service calls, DTOs, validators, converters, and security configuration.
3. For every endpoint, capture only facts supported by source:
   - HTTP method and complete route, including base path and class-level mappings
   - path/query parameters and required/optional status
   - request content type and request DTO fields, validation constraints, and examples if present
   - response DTO / status codes / error formats when visible
   - authentication / authorization requirements
4. Follow controller-to-facade/service call paths only as far as needed to understand payloads and behavior. Do not expose internal data or secrets.
5. Organize requests by API resource or controller. Use collection variables such as `baseUrl`, `accessToken`, and sample IDs; never hardcode credentials.
6. Mark unknown or inferred details explicitly. Do not fabricate sample business data, endpoint paths, response codes, or authorization scopes.
7. Validate the generated collection as JSON and explain what needs confirmation.

## Output
- Endpoint inventory with source evidence
- Generated Postman Collection 2.1 JSON or instructions to import the helper output
- Required environment variables
- Known gaps / assumptions requiring confirmation

## Safety
Do not call live endpoints, publish collections, or store tokens unless the user explicitly requests it. Keep credentials in Postman environment secrets, not in the collection JSON.
