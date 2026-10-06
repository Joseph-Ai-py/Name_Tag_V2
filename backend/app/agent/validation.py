from typing import Any

from app.agent.permissions import can_use_tool
from app.tools.registry import tool_registry


class AgentToolValidator:
    """Validates an LLM tool proposal before it reaches a ToolExecutor."""

    _backend_owned_fields = {"brand_id", "user_id", "role", "db"}

    def validate(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        role: str,
        *,
        allow_apply: bool = False,
    ) -> None:
        definition = tool_registry.get(tool_name)
        if not can_use_tool(role, definition.permission):
            raise PermissionError(f"Role {role} cannot use tool {tool_name}")
        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be an object")
        forbidden = self._backend_owned_fields.intersection(arguments)
        if forbidden:
            fields = ", ".join(sorted(forbidden))
            raise ValueError(f"Tool arguments cannot set backend-owned fields: {fields}")
        if tool_name == "apply_brand_change" and not allow_apply:
            raise PermissionError("Agent runs cannot apply brand changes")
        self._validate_schema(definition.input_schema, arguments, path="arguments")

    def _validate_schema(self, schema: dict[str, Any], value: Any, path: str) -> None:
        expected_type = schema.get("type")
        if expected_type == "object":
            if not isinstance(value, dict):
                raise ValueError(f"{path} must be an object")
            required = schema.get("required", [])
            missing = [name for name in required if name not in value]
            if missing:
                raise ValueError(f"{path} is missing required fields: {', '.join(missing)}")
            properties = schema.get("properties", {})
            additional = schema.get("additionalProperties", True)
            if additional is False:
                unknown = set(value).difference(properties)
                if unknown:
                    raise ValueError(f"{path} has unknown fields: {', '.join(sorted(unknown))}")
            for name, child in properties.items():
                if name in value:
                    self._validate_schema(child, value[name], f"{path}.{name}")
            return
        if expected_type == "string" and not isinstance(value, str):
            raise ValueError(f"{path} must be a string")
        if expected_type == "object" and not isinstance(value, dict):
            raise ValueError(f"{path} must be an object")
        if expected_type == "array" and not isinstance(value, list):
            raise ValueError(f"{path} must be an array")
        if expected_type == "boolean" and not isinstance(value, bool):
            raise ValueError(f"{path} must be a boolean")
        if expected_type == "number" and not isinstance(value, (int, float)):
            raise ValueError(f"{path} must be a number")
        if expected_type == "integer" and not isinstance(value, int):
            raise ValueError(f"{path} must be an integer")
        if "enum" in schema and value not in schema["enum"]:
            raise ValueError(f"{path} must be one of: {', '.join(map(str, schema['enum']))}")
