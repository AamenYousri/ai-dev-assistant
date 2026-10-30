#!/usr/bin/env python3
"""Convert an OpenAPI 3.x JSON (or YAML with PyYAML) file to Postman Collection 2.1.

This intentionally implements the common OpenAPI subset needed for request
scaffolding. Review generated auth, examples, and server variables before use.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import uuid
from pathlib import Path
from typing import Any

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}

def load_spec(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise RuntimeError("YAML input requires PyYAML. Install with: python -m pip install PyYAML") from exc
        data = yaml.safe_load(raw)
    else:
        data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("OpenAPI document root must be an object")
    version = str(data.get("openapi", ""))
    if not version.startswith("3."):
        raise ValueError(f"Expected OpenAPI 3.x; found {version or 'no openapi field'}")
    return data

def example_from_schema(schema: dict[str, Any]) -> Any:
    if "example" in schema:
        return schema["example"]
    if "default" in schema:
        return schema["default"]
    if schema.get("type") == "object":
        # Do not invent field values. Return a minimal placeholder object only.
        return {name: "<value>" for name in schema.get("properties", {})}
    if schema.get("type") == "array":
        return []
    return None

def convert(spec: dict[str, Any], collection_name: str | None = None) -> dict[str, Any]:
    info = spec.get("info") or {}
    name = collection_name or info.get("title") or "OpenAPI generated collection"
    servers = spec.get("servers") or []
    server = servers[0] if servers and isinstance(servers[0], dict) else {}
    raw_server_url = str(server.get("url") or "http://localhost")
    server_variables = server.get("variables") or {}
    base_url = raw_server_url
    collection_variables = [{"key": "accessToken", "value": ""}]
    for variable_name, variable_info in server_variables.items():
        default_value = str((variable_info or {}).get("default", ""))
        base_url = base_url.replace("{" + str(variable_name) + "}", default_value)
    items_by_group: dict[str, list[dict[str, Any]]] = {}
    warnings: list[str] = []
    for route, path_item in (spec.get("paths") or {}).items():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            method = str(method).lower()
            if method not in HTTP_METHODS or not isinstance(operation, dict):
                continue
            tags = operation.get("tags") or ["Endpoints"]
            group = str(tags[0]) if tags else "Endpoints"
            path = re.sub(r"\{([^}]+)\}", r":\1", str(route))
            raw_url = "{{baseUrl}}" + (path if path.startswith("/") else "/" + path)
            query_params = []
            for param in operation.get("parameters", []) or []:
                if not isinstance(param, dict):
                    continue
                if param.get("$ref"):
                    warnings.append(f"{method.upper()} {route}: referenced parameter {param['$ref']} was not expanded")
                    continue
                if param.get("in") == "query":
                    schema_for_param = param.get("schema") or {}
                    has_example = "example" in param or "example" in schema_for_param or "default" in schema_for_param
                    value = param.get("example", schema_for_param.get("example", schema_for_param.get("default", "<value>")))
                    query_params.append({"key": str(param.get("name", "param")), "value": str(value), "disabled": not bool(param.get("required", False) or has_example)})
            if query_params:
                raw_url += "?" + "&".join(f"{p['key']}={p['value']}" for p in query_params)
            request: dict[str, Any] = {
                "method": method.upper(),
                "header": [],
                "url": {"raw": raw_url},
                "description": operation.get("description") or operation.get("summary") or "",
            }
            if query_params:
                request["url"]["query"] = query_params
            path_vars = re.findall(r":([A-Za-z0-9_]+)", path)
            if path_vars:
                request["url"]["variable"] = [{"key": key, "value": "<value>"} for key in path_vars]
            request_body = operation.get("requestBody")
            if isinstance(request_body, dict):
                if request_body.get("$ref"):
                    warnings.append(f"{method.upper()} {route}: requestBody reference {request_body['$ref']} was not expanded")
                else:
                    content = request_body.get("content") or {}
                    json_content = content.get("application/json") or next(iter(content.values()), {})
                    schema = json_content.get("schema", {}) if isinstance(json_content, dict) else {}
                    example = json_content.get("example") if isinstance(json_content, dict) else None
                    if example is None and isinstance(schema, dict):
                        example = example_from_schema(schema)
                    if example is not None:
                        request["header"].append({"key": "Content-Type", "value": "application/json"})
                        request["body"] = {"mode": "raw", "raw": json.dumps(example, indent=2), "options": {"raw": {"language": "json"}}}
            item = {"name": operation.get("summary") or f"{method.upper()} {route}", "request": request, "response": []}
            items_by_group.setdefault(group, []).append(item)
    folders = [{"name": group, "item": items} for group, items in sorted(items_by_group.items())]
    if not folders:
        warnings.append("No HTTP operations were found under paths.")
    result = {
        "info": {
            "_postman_id": str(uuid.uuid4()),
            "name": name,
            "description": "Generated from OpenAPI. Review examples, auth, and variables before use.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": folders,
        "variable": [{"key": "baseUrl", "value": base_url}, *collection_variables],
    }
    # Use collection-level bearer auth only when OpenAPI declares HTTP bearer security.
    schemes = (spec.get("components") or {}).get("securitySchemes") or {}
    security_requirements = spec.get("security") or []
    bearer_scheme_names = {name for name, value in schemes.items() if isinstance(value, dict) and value.get("type") == "http" and value.get("scheme", "").lower() == "bearer"}
    bearer_found = any(bearer_scheme_names.intersection(requirement.keys()) for requirement in security_requirements if isinstance(requirement, dict))
    if bearer_found:
        result["auth"] = {"type": "bearer", "bearer": [{"key": "token", "value": "{{accessToken}}", "type": "string"}]}
    result["_ai_dev_assistant_warnings"] = warnings
    return result

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", help="OpenAPI 3.x JSON or YAML file")
    parser.add_argument("-o", "--output", default="postman_collection.json", help="Output file")
    parser.add_argument("--name", help="Collection name (defaults to OpenAPI info.title)")
    args = parser.parse_args()
    source = Path(args.spec)
    if not source.is_file():
        parser.error(f"Specification not found: {source}")
    try:
        result = convert(load_spec(source), args.name)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        for warning in result.get("_ai_dev_assistant_warnings", []):
            print(f"WARNING: {warning}", file=sys.stderr)
        # Keep collection importable by removing toolkit-only metadata.
        result.pop("_ai_dev_assistant_warnings", None)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Wrote {output}")
    except (OSError, json.JSONDecodeError, ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
