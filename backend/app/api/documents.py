from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import require_editor_role
from app.dependencies import get_current_user, get_database
from app.models.user import User
from app.schemas.document import (
	BlockCreateRequest,
	BlockResponse,
	BlockUpdateRequest,
	DocumentCreateRequest,
	DocumentResponse,
	DocumentUpdateRequest,
)
from app.services.brand_service import get_brand_membership
from app.services.document_service import (
	create_block,
	create_document,
	delete_block,
	get_block,
	get_brand_documents,
	get_document,
	get_document_blocks,
	update_block,
	update_document,
)

router = APIRouter(prefix="/api/brands/{brand_id}/documents", tags=["documents"])


def membership_or_404(db: Session, brand_id: str, user_id: str):
	membership = get_brand_membership(db, brand_id, user_id)
	if membership is None:
		raise HTTPException(status_code=404, detail="Brand not found")
	return membership


def document_response(db: Session, document) -> DocumentResponse:
	return DocumentResponse(
		id=document.id,
		brand_id=document.brand_id,
		created_by=document.created_by,
		title=document.title,
		blocks=[BlockResponse.model_validate(block, from_attributes=True) for block in get_document_blocks(db, document.id)],
		created_at=document.created_at,
		updated_at=document.updated_at,
	)


def document_or_404(db: Session, brand_id: str, document_id: str):
	document = get_document(db, brand_id, document_id)
	if document is None:
		raise HTTPException(status_code=404, detail="Document not found")
	return document


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document_endpoint(brand_id: str, payload: DocumentCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
	membership = membership_or_404(db, brand_id, current_user.id)
	require_editor_role(membership.role)
	return document_response(db, create_document(db, brand_id, current_user.id, payload.title))


@router.get("", response_model=list[DocumentResponse])
def list_documents(brand_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
	membership_or_404(db, brand_id, current_user.id)
	return [document_response(db, document) for document in get_brand_documents(db, brand_id)]


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document_endpoint(brand_id: str, document_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
	membership_or_404(db, brand_id, current_user.id)
	return document_response(db, document_or_404(db, brand_id, document_id))


@router.patch("/{document_id}", response_model=DocumentResponse)
def update_document_endpoint(brand_id: str, document_id: str, payload: DocumentUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
	membership = membership_or_404(db, brand_id, current_user.id)
	require_editor_role(membership.role)
	document = document_or_404(db, brand_id, document_id)
	return document_response(db, update_document(db, document, payload.title))


@router.post("/{document_id}/blocks", response_model=BlockResponse, status_code=status.HTTP_201_CREATED)
def create_block_endpoint(brand_id: str, document_id: str, payload: BlockCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
	membership = membership_or_404(db, brand_id, current_user.id)
	require_editor_role(membership.role)
	document_or_404(db, brand_id, document_id)
	return BlockResponse.model_validate(create_block(db, document_id, payload.type, payload.content, payload.position), from_attributes=True)


@router.patch("/{document_id}/blocks/{block_id}", response_model=BlockResponse)
def update_block_endpoint(brand_id: str, document_id: str, block_id: str, payload: BlockUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
	membership = membership_or_404(db, brand_id, current_user.id)
	require_editor_role(membership.role)
	document_or_404(db, brand_id, document_id)
	block = get_block(db, document_id, block_id)
	if block is None:
		raise HTTPException(status_code=404, detail="Block not found")
	return BlockResponse.model_validate(update_block(db, block, payload.content), from_attributes=True)


@router.delete("/{document_id}/blocks/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_block_endpoint(brand_id: str, document_id: str, block_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
	membership = membership_or_404(db, brand_id, current_user.id)
	require_editor_role(membership.role)
	document_or_404(db, brand_id, document_id)
	block = get_block(db, document_id, block_id)
	if block is None:
		raise HTTPException(status_code=404, detail="Block not found")
	delete_block(db, block)
