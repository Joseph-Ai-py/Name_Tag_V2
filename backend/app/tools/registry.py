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
	ToolDefinition("get_brand_state", "read", description="현재 BrandState와 version을 조회합니다.", input_schema={"type": "object", "properties": {}, "additionalProperties": False}, output_schema={"type": "object", "required": ["state", "version"]}, category="brand"),
	ToolDefinition("get_brand_context", "read", description="요청에 필요한 브랜드 맥락을 조회합니다.", input_schema={"type": "object", "properties": {"task": {"type": "string"}}, "additionalProperties": False}, category="brand"),
	ToolDefinition("run_employee_meeting", "write", description="선택된 AI Employee의 의견을 모아 제안을 만듭니다.", input_schema={"type": "object", "required": ["agenda"], "properties": {"agenda": {"type": "string"}, "mode": {"type": "string", "enum": ["lite", "full"]}}, "additionalProperties": False}, category="meeting", risk_level="medium"),
	ToolDefinition("propose_brand_change", "approval_required", description="승인 대기 상태의 BrandState 변경 Proposal을 만듭니다.", input_schema={"type": "object", "required": ["title", "summary", "changes"], "properties": {"title": {"type": "string"}, "summary": {"type": "string"}, "changes": {"type": "object"}}, "additionalProperties": False}, category="proposal", risk_level="medium"),
	ToolDefinition("apply_brand_change", "action", description="승인된 Proposal을 적용합니다.", input_schema={"type": "object", "required": ["proposal_id"], "properties": {"proposal_id": {"type": "string"}}, "additionalProperties": False}, category="proposal", risk_level="high"),
	ToolDefinition("get_research_job", "read", description="Research Job 상태를 조회합니다.", input_schema={"type": "object", "required": ["job_id"], "properties": {"job_id": {"type": "string"}}, "additionalProperties": False}, category="research"),
	ToolDefinition("create_research_job", "approval_required", description="Research 실행을 위한 Job을 생성합니다.", input_schema={"type": "object", "required": ["query"], "properties": {"query": {"type": "string"}, "plan": {"type": "object"}}, "additionalProperties": False}, category="research", risk_level="medium"),
	ToolDefinition("apply_research_finding", "approval_required", description="Research Finding을 Proposal로 변환합니다.", input_schema={"type": "object", "required": ["report_id", "finding_id"], "properties": {"report_id": {"type": "string"}, "finding_id": {"type": "string"}}, "additionalProperties": False}, category="research", risk_level="medium"),
	ToolDefinition("create_document", "write", description="초안 Document를 생성합니다.", input_schema={"type": "object", "required": ["title"], "properties": {"title": {"type": "string"}}, "additionalProperties": False}, category="document"),
	ToolDefinition("update_block", "write", description="Document Block을 수정합니다.", input_schema={"type": "object", "required": ["document_id", "block_id", "content"], "properties": {"document_id": {"type": "string"}, "block_id": {"type": "string"}, "content": {"type": "object"}}, "additionalProperties": False}, category="document"),
	ToolDefinition("save_asset", "write", description="Asset 메타데이터를 저장합니다.", input_schema={"type": "object", "required": ["type", "filename", "mime_type", "storage_path"], "properties": {"type": {"type": "string"}, "filename": {"type": "string"}, "mime_type": {"type": "string"}, "storage_path": {"type": "string"}, "metadata": {"type": "object"}}, "additionalProperties": False}, category="asset"),
	ToolDefinition("export_pdf", "action", description="브랜드 데이터를 JSON으로 내보냅니다.", input_schema={"type": "object", "properties": {}, "additionalProperties": False}, category="export", risk_level="medium"),
])
