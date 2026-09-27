# NAME TAG V2 — Architecture Reality Lock

## Product

NAME TAG is an AI Brand Workspace.

Chat is an input method.
Workspace is the product.

## Source of Truth

BrandState is the single source of truth for brand information.

AI must never directly overwrite BrandState.

All important AI-generated changes follow:

Proposal
→ Approval
→ Snapshot
→ Mutation
→ History

## Authentication

V1 authentication:

- Email
- Password
- Argon2id
- Secure HttpOnly Session Cookie

Authentication flow:

Request
→ Session Authentication
→ Current User
→ Brand Membership
→ Role Check
→ Resource Access

Backend is the final authority for authentication and authorization.

## Brand Isolation

User
→ Brand
→ Workspace

Every Brand resource must be scoped by brand_id.

The backend must verify BrandMember membership for every protected Brand request.

## Roles

### Owner

- Read
- Edit
- Member management

### Editor

- Read
- Edit

### Viewer

- Read only

## BrandState

BrandState contains:

- business
- market
- customer
- brand
- visual
- assets
- research
- feedback
- decisions

## Research

Research never directly modifies BrandState.

Research flow:

Request
→ Research Mode
→ Plan
→ Approval
→ Job
→ Report
→ Finding
→ Brand Change Proposal
→ Approval
→ BrandState Mutation

## Legacy

Legacy Section O/A/B/C/DE must not be deleted yet.

Migration strategy:

Legacy
→ Adapter
→ BrandState
→ Workspace

Legacy UI remains temporarily for compatibility.

## Frontend State

TanStack Query:

- Server state
- BrandState
- Conversation
- Research
- Documents
- Assets

Zustand:

- UI state only

BrandState must never be stored in Zustand.

## Current Implementation Status

### P0

- [ ] Reality Lock
- [ ] Authentication
- [ ] Session
- [ ] User
- [ ] Brand
- [ ] BrandMember
- [ ] BrandState
- [ ] Proposal
- [ ] Mutation
- [ ] Snapshot
- [ ] History

### P1

- [ ] Legacy → Skill migration
- [ ] Business
- [ ] Market
- [ ] Customer
- [ ] Quick Research
- [ ] AI Consultant
- [ ] Workspace

### P2

- [ ] Deep Research
- [ ] Dependency Engine
- [ ] Block Editor
- [ ] Assets
- [ ] PDF Export

### P3

- [ ] RAG
- [ ] Redis
- [ ] SSE
- [ ] MCP
- [ ] Multi-model