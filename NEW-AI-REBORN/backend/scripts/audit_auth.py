#!/usr/bin/env python3
"""Audit script: scan all routers and report endpoints lacking authentication.

Uses AST parsing for reliable static analysis without runtime imports.
Usage:
    python backend/scripts/audit_auth.py

Output:
    JSON report with all endpoints, their auth status, and a summary.
"""

from __future__ import annotations

import ast
import json
import os
import sys
from pathlib import Path
from typing import Any

# Add backend to path
BACKEND_DIR = Path(__file__).resolve().parent.parent

# Router modules to scan (relative to backend dir)
ROUTER_MODULES = [
    "src/routers/health",
    "src/routers/auth",
    "src/routers/natal",
    "src/routers/transit",
    "src/routers/synastry",
    "src/routers/branches",
    "src/routers/dashboard",
    "src/routers/payments",
    "src/routers/notifications",
    "src/routers/memory",
    "src/routers/tarot",
    "src/routers/horary",
    "src/routers/western",
    "src/routers/fusion",
    "src/routers/fusion_profile",
    "src/routers/fusion_full",
    "src/routers/fusion_grand",
    "src/routers/bazi",
    "src/routers/chinese",
    "src/routers/reports",
    "src/routers/vedic",
    "src/routers/muhurta",
    "src/routers/chat",
    "src/routers/accuracy",
    "src/routers/new_engines",
    "src/routers/sky",
    "src/routers/life",
    "src/routers/research",
    "src/routers/narrative_router",
    "src/routers/grand_narrative_router",
]

# Patterns that indicate authentication is enforced
AUTH_INDICATORS = [
    "get_current_user",
    "_require_user",
    "authorization",
    "Authorization",
]

# Public prefixes that are intentionally exempt
PUBLIC_PREFIXES = [
    "/ready",
    "/health",
    "/v1/health",
    "/v1/auth",
    "/docs",
    "/openapi.json",
    "/redoc",
]


def _is_public_path(path: str) -> bool:
    """Check if a path is intentionally public."""
    for prefix in PUBLIC_PREFIXES:
        if path.startswith(prefix) or path == prefix.rstrip("/"):
            return True
    return False


def _check_function_has_auth(func_node: ast.FunctionDef) -> tuple[bool, list[str]]:
    """Check if a function AST node contains auth patterns.

    Returns:
        Tuple of (has_auth, list_of_indicators_found)
    """
    found_indicators = []
    source = ast.dump(func_node)

    for indicator in AUTH_INDICATORS:
        if indicator in source:
            found_indicators.append(indicator)

    # Also check for Depends with auth in function arguments
    for arg in func_node.args.args:
        arg_str = ast.dump(arg)
        if "Depends" in arg_str or "_require_user" in arg_str or "get_current_user" in arg_str:
            if "Depends(auth)" not in found_indicators:
                found_indicators.append("Depends(auth)")

    # Check decorators for auth
    for decorator in func_node.decorator_list:
        dec_str = ast.dump(decorator)
        if "Depends" in dec_str and ("_require_user" in dec_str or "get_current_user" in dec_str):
            if "Depends(auth)" not in found_indicators:
                found_indicators.append("Depends(auth)")

    return len(found_indicators) > 0, found_indicators


def scan_router_file(router_file: Path, module_name: str) -> list[dict[str, Any]]:
    """Scan a router file using AST and return endpoint auth info."""
    results = []

    if not router_file.exists():
        return [{"error": f"Router file not found: {router_file}"}]

    try:
        source = router_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(router_file))
    except SyntaxError as e:
        return [{"error": f"Syntax error in {router_file}: {e}"}]

    # Find all router assignments (e.g., router = APIRouter())
    router_names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and isinstance(node.value, ast.Call):
                    func = node.value.func
                    if isinstance(func, ast.Name) and func.id == "APIRouter":
                        router_names.append(target.id)
                    elif isinstance(func, ast.Attribute) and func.attr == "APIRouter":
                        router_names.append(target.id)

    if not router_names:
        return [{"error": f"No APIRouter found in {module_name}"}]

    # Find all decorated functions that are route handlers
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue

        # Check if this function has a router decorator
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue

            # Check for router.get/post/put/delete/patch calls
            func = decorator.func
            if not isinstance(func, ast.Attribute):
                continue

            if not hasattr(func.attr, "value") and func.attr not in ("get", "post", "put", "delete", "patch", "head", "options"):
                continue

            # Get the method
            method = func.attr.upper()
            if method not in ("GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"):
                continue

            # Get the path from decorator args
            path = ""
            if decorator.args:
                if isinstance(decorator.args[0], ast.Constant):
                    path = decorator.args[0].value

            # Check for prefix in keywords
            prefix = ""
            for kw in decorator.keywords:
                if kw.arg == "prefix" and isinstance(kw.value, ast.Constant):
                    prefix = kw.value.value

            full_path = prefix + path

            # Check if path is public
            is_public = _is_public_path(full_path)

            # Check for auth in function
            has_auth, auth_indicators = _check_function_has_auth(node)

            results.append({
                "router": router_names[0] if router_names else "unknown",
                "module": module_name,
                "path": full_path,
                "methods": [method],
                "endpoint": node.name,
                "has_auth": has_auth,
                "auth_indicators": auth_indicators,
                "is_public": is_public,
                "needs_auth": not has_auth and not is_public,
            })

    return results


def main() -> dict[str, Any]:
    """Run the audit and return the report."""
    all_endpoints = []
    errors = []

    for module_path in ROUTER_MODULES:
        router_file = BACKEND_DIR / (module_path + ".py")
        try:
            endpoints = scan_router_file(router_file, module_path)
            for ep in endpoints:
                if "error" in ep:
                    errors.append(ep)
                else:
                    all_endpoints.append(ep)
        except Exception as e:
            errors.append({"module": module_path, "error": str(e)})

    # Categorize
    protected = [ep for ep in all_endpoints if ep["has_auth"]]
    unprotected = [ep for ep in all_endpoints if ep["needs_auth"]]
    public = [ep for ep in all_endpoints if ep["is_public"]]

    report = {
        "summary": {
            "total_endpoints": len(all_endpoints),
            "protected": len(protected),
            "unprotected": len(unprotected),
            "public_exempt": len(public),
            "errors": len(errors),
        },
        "unprotected_endpoints": [
            {
                "path": ep["path"],
                "methods": ep["methods"],
                "endpoint": ep["endpoint"],
                "module": ep["module"],
            }
            for ep in sorted(unprotected, key=lambda x: x["path"])
        ],
        "protected_endpoints": [
            {
                "path": ep["path"],
                "methods": ep["methods"],
                "endpoint": ep["endpoint"],
                "auth_indicators": ep["auth_indicators"],
            }
            for ep in sorted(protected, key=lambda x: x["path"])
        ],
        "public_endpoints": [
            {
                "path": ep["path"],
                "methods": ep["methods"],
                "endpoint": ep["endpoint"],
            }
            for ep in sorted(public, key=lambda x: x["path"])
        ],
        "errors": errors,
    }

    return report


if __name__ == "__main__":
    report = main()
    print(json.dumps(report, indent=2, ensure_ascii=False))

    # Exit with error code if unprotected endpoints found
    if report["summary"]["unprotected"] > 0:
        sys.exit(1)