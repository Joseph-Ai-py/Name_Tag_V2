from app.tools.base import ToolDefinition


class ToolRegistry:
	def __init__(self, definitions: list[ToolDefinition] | None = None) -> None:
		self._tools = {tool.name: tool for tool in definitions or []}

	def register(self, tool: ToolDefinition) -> None:
		if tool.name in self._tools:
			raise ValueError(f"Tool already registered: {tool.name}")
		self._tools[tool.name] = tool

	def get(self, name: str) -> ToolDefinition:
		tool = self._tools.get(name)
		if tool is None:
			raise ValueError(f"Unknown tool: {name}")
		return tool

	def names(self) -> tuple[str, ...]:
		return tuple(sorted(self._tools))


tool_registry = ToolRegistry([
	ToolDefinition("get_brand_state", "read"),
	ToolDefinition("get_brand_context", "read"),
	ToolDefinition("run_employee_meeting", "write"),
	ToolDefinition("propose_brand_change", "write"),
	ToolDefinition("apply_brand_change", "action"),
	ToolDefinition("get_research_job", "read"),
	ToolDefinition("create_research_job", "write"),
	ToolDefinition("apply_research_finding", "action"),
	ToolDefinition("create_document", "write"),
	ToolDefinition("update_block", "write"),
	ToolDefinition("save_asset", "write"),
	ToolDefinition("export_pdf", "action"),
])
