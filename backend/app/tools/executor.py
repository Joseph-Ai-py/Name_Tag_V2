from typing import Any

from app.agent.permissions import can_use_tool
from app.services.asset_service import create_asset
from app.services.brand_service import get_brand
from app.services.brand_state_service import get_brand_state
from app.services.document_service import create_document, get_block, get_document, update_block
from app.services.export_service import build_json_export
from app.services.proposal_service import apply_proposal, create_proposal, get_proposal
from app.services.research_service import create_deep_research_job, create_research_plan, get_research_job
from app.tools.base import ToolContext
from app.tools.registry import tool_registry


class ToolExecutor:
    def execute(self, name: str, context: ToolContext, **arguments: Any) -> Any:
        definition = tool_registry.get(name)
        if not can_use_tool(context.role, definition.permission):
            raise PermissionError(f"Role {context.role} cannot use tool {name}")

        handlers = {
            "get_brand_state": self._get_brand_state,
            "get_brand_context": self._get_brand_context,
            "propose_brand_change": self._propose_brand_change,
            "apply_brand_change": self._apply_brand_change,
            "get_research_job": self._get_research_job,
            "create_research_job": self._create_research_job,
            "create_document": self._create_document,
            "update_block": self._update_block,
            "save_asset": self._save_asset,
            "export_pdf": self._export_json,
        }
        handler = handlers.get(name)
        if handler is None:
            raise NotImplementedError(f"Tool handler is not implemented: {name}")
        return handler(context, **arguments)

    @staticmethod
    def _get_brand_state(context: ToolContext, **_: Any) -> dict:
        state = get_brand_state(context.db, context.brand_id)
        if state is None:
            raise ValueError("Brand state not found")
        return {"state": state.state, "version": state.version}

    @staticmethod
    def _get_brand_context(context: ToolContext, task: str = "general", **_: Any) -> dict:
        state = ToolExecutor._get_brand_state(context)
        data = state["state"]
        if task == "logo_generation":
            return {"brand": data.get("brand", {}), "visual": data.get("visual", {})}
        if task == "customer_analysis":
            return {"business": data.get("business", {}), "customer": data.get("customer", {})}
        return {key: data.get(key, {}) for key in ("business", "market", "customer", "brand", "visual")}

    @staticmethod
    def _propose_brand_change(context: ToolContext, title: str, summary: str, changes: dict) -> Any:
        return create_proposal(context.db, context.brand_id, context.user_id, title, summary, changes)

    @staticmethod
    def _apply_brand_change(context: ToolContext, proposal_id: str) -> Any:
        proposal = get_proposal(context.db, context.brand_id, proposal_id)
        if proposal is None:
            raise ValueError("Proposal not found")
        return apply_proposal(context.db, proposal, context.user_id)

    @staticmethod
    def _get_research_job(context: ToolContext, job_id: str) -> Any:
        job = get_research_job(context.db, job_id)
        if job is None or job.brand_id != context.brand_id:
            raise ValueError("Research job not found")
        return job

    @staticmethod
    def _create_research_job(context: ToolContext, query: str, plan: dict | None = None) -> Any:
        return create_deep_research_job(context.db, context.brand_id, context.user_id, query, plan or create_research_plan(query))

    @staticmethod
    def _create_document(context: ToolContext, title: str) -> Any:
        return create_document(context.db, context.brand_id, context.user_id, title)

    @staticmethod
    def _update_block(context: ToolContext, document_id: str, block_id: str, content: dict) -> Any:
        document = get_document(context.db, context.brand_id, document_id)
        if document is None:
            raise ValueError("Document not found")
        block = get_block(context.db, document_id, block_id)
        if block is None:
            raise ValueError("Block not found")
        return update_block(context.db, block, content)

    @staticmethod
    def _save_asset(context: ToolContext, **values: Any) -> Any:
        return create_asset(context.db, context.brand_id, context.user_id, **values)

    @staticmethod
    def _export_json(context: ToolContext, **_: Any) -> dict:
        brand = get_brand(context.db, context.brand_id)
        if brand is None:
            raise ValueError("Brand not found")
        return build_json_export(context.db, brand)