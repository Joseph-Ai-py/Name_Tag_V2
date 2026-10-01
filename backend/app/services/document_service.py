from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_block import DocumentBlock


def create_document(db: Session, brand_id: str, user_id: str, title: str) -> Document:
	document = Document(brand_id=brand_id, created_by=user_id, title=title)
	db.add(document)
	db.commit()
	db.refresh(document)
	return document


def get_document(db: Session, brand_id: str, document_id: str) -> Document | None:
	return db.scalar(select(Document).where(Document.brand_id == brand_id, Document.id == document_id))


def get_brand_documents(db: Session, brand_id: str) -> list[Document]:
	result = db.execute(select(Document).where(Document.brand_id == brand_id).order_by(Document.updated_at.desc()))
	return list(result.scalars())


def update_document(db: Session, document: Document, title: str) -> Document:
	document.title = title
	db.commit()
	db.refresh(document)
	return document


def get_document_blocks(db: Session, document_id: str) -> list[DocumentBlock]:
	result = db.execute(select(DocumentBlock).where(DocumentBlock.document_id == document_id).order_by(DocumentBlock.position, DocumentBlock.created_at))
	return list(result.scalars())


def create_block(db: Session, document_id: str, block_type: str, content: dict, position: int) -> DocumentBlock:
	block = DocumentBlock(document_id=document_id, type=block_type, content=content, position=position)
	db.add(block)
	db.commit()
	db.refresh(block)
	return block


def get_block(db: Session, document_id: str, block_id: str) -> DocumentBlock | None:
	return db.scalar(select(DocumentBlock).where(DocumentBlock.document_id == document_id, DocumentBlock.id == block_id))


def update_block(db: Session, block: DocumentBlock, content: dict) -> DocumentBlock:
	block.content = content
	db.commit()
	db.refresh(block)
	return block


def delete_block(db: Session, block: DocumentBlock) -> None:
	db.delete(block)
	db.commit()
