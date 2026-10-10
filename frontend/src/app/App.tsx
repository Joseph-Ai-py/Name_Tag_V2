import { FormEvent, useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
	ArrowUpRight,
	BarChart3,
	BookOpen,
	BriefcaseBusiness,
	ChevronDown,
	CircleCheck,
	FileText,
	FileJson,
	FolderOpen,
	History as HistoryIcon,
	LayoutDashboard,
	Lightbulb,
	LogIn,
	MessageCircle,
	MessageSquare,
	Palette,
	Plus,
	Search,
	Send,
	Sparkles,
	Moon,
	Sun,
	Trash2,
	Users,
	UserPlus,
	X,
} from "lucide-react";
import { api } from "../api/client";
import { brandStateQueryKey } from "../api/brands";
import { useBrandState } from "../hooks/useBrandState";

type Section = "Overview" | "Business" | "Market" | "Customer" | "Brand" | "Visual" | "Research" | "Assets" | "Documents" | "History" | "Export";
type Artifact = { id: string; type: string; title: string; content: Record<string, unknown>; status: string; proposalId?: string };
type ProposalPayload = { id: string; title: string; summary: string; changes: Record<string, unknown>; status: string; base_state_version?: number; created_at?: string; updated_at?: string };
type ResearchJobPayload = { id: string; query: string; status: string; plan: Record<string, unknown>; progress: Record<string, unknown> };
type AgentChatResult = { message: string; conversation_id: string; artifact: Artifact | null; proposal?: ProposalPayload | null; research_job?: ResearchJobPayload | null; proposal_id?: string };
type Message = { role: "assistant" | "user"; text: string; artifact?: Artifact };
type CurrentUser = { id: string; email: string };
type BrandStatePayload = { state: { business?: Record<string, unknown>; market?: Record<string, unknown>; customer?: Record<string, unknown>; brand?: Record<string, unknown>; visual?: Record<string, unknown> } };
type ConversationSummary = { id: string; title: string | null; updated_at: string };
type StoredMessage = { role: "assistant" | "user"; content: string };
type ThemeMode = "light" | "dark";
type ResearchReport = { id: string; title: string; executive_summary: string; status: string; findings: Array<{ id: string; statement: string; confidence: string; applied: boolean }>; sources?: Array<{ title: string; url: string; publisher?: string | null }> };
type HistoryEntry = { id: string; action: string; details: Record<string, unknown>; created_at: string };
type Asset = { id: string; type: string; filename: string; mime_type: string; storage_path: string; metadata: Record<string, unknown>; created_at: string };
type Snapshot = { id: string; version: number; created_at: string };
type DocumentRecord = { id: string; title: string; blocks: Array<{ id: string; type: string; content: Record<string, unknown> }>; updated_at: string };
type ExportPayload = Record<string, unknown>;
type WorkspaceState = {
	business: { service: string; problem: string };
	market: { trend: string; competitors: string };
	customer: { target: string; need: string };
	brand: { name: string; positioning: string; tone: string };
	visual: { mood: string; palette: string[]; colors: unknown[]; typography: unknown; logo: unknown; character: unknown };
};

function toChatArtifact(result: AgentChatResult): Artifact | null {
	if (result.artifact) return { ...result.artifact, proposalId: result.proposal_id };
	if (result.research_job) return {
		id: result.research_job.id,
		type: "research_job",
		title: "Deep Research 승인 대기",
		content: { query: result.research_job.query, status: result.research_job.status, plan: result.research_job.plan },
		status: "pending",
	};
	if (!result.proposal) return null;
	return {
		id: result.proposal.id,
		type: "proposal",
		title: result.proposal.title,
		content: { summary: result.proposal.summary, changes: result.proposal.changes },
		status: result.proposal.status,
		proposalId: result.proposal.id,
	};
}

function ExportValue({ value }: { value: unknown }) {
	if (Array.isArray(value)) return <div className="export-list">{value.map((item, index) => <div className="export-list-item" key={index}><ExportValue value={item} /></div>)}</div>;
	if (value !== null && typeof value === "object") return <div className="export-object">{Object.entries(value as Record<string, unknown>).map(([key, nested]) => <div className="export-entry" key={key}><span>{key.replaceAll("_", " ")}</span><div><ExportValue value={nested} /></div></div>)}</div>;
	return <p className="export-scalar">{value === null || value === undefined ? "-" : String(value)}</p>;
}

function getArtifactOptions(artifact: Artifact | null): Array<Record<string, unknown>> | undefined {
	if (!artifact) return undefined;
	const optionEntry = Object.entries(artifact.content).find(([, value]) => Array.isArray(value));
	return optionEntry?.[1] as Array<Record<string, unknown>> | undefined;
}

function getResearchPrompt(artifact: Artifact): string | null {
	const prompt = Object.values(artifact.content).find((value) => typeof value === "string" && (value.includes("프롬프트") || value.length > 500));
	return typeof prompt === "string" ? prompt : null;
}

const demoState: WorkspaceState = {
	business: { service: "AI Brand Workspace", problem: "브랜드 기획의 맥락이 대화마다 흩어져요." },
	market: { trend: "경험 중심의 초기 브랜드 구축", competitors: "대화형 AI · 브랜드 에이전시" },
	customer: { target: "만들고 있는 것이 있는 예비 창업자", need: "아이디어를 실행 가능한 구조로 정리" },
	brand: { name: "Luma", positioning: "복잡한 시작을 선명한 브랜드로", tone: "명확하고 따뜻하게" },
	visual: { mood: "Quiet confidence", palette: ["#1b4332", "#d8f3dc", "#f4f1eb"], colors: [], typography: null, logo: null, character: null },
};

const emptyState: WorkspaceState = {
	business: { service: "", problem: "" },
	market: { trend: "", competitors: "" },
	customer: { target: "", need: "" },
	brand: { name: "", positioning: "", tone: "" },
	visual: { mood: "", palette: [] as string[], colors: [] as unknown[], typography: null as unknown, logo: null as unknown, character: null as unknown },
};

function ThemeToggle({ theme, onToggle }: { theme: ThemeMode; onToggle: () => void }) {
	return <button className="theme-toggle" onClick={onToggle} aria-label={`${theme === "light" ? "다크" : "라이트"} 모드로 전환`} title={`${theme === "light" ? "다크" : "라이트"} 모드`}>{theme === "light" ? <Moon size={16} /> : <Sun size={16} />}</button>;
}

function ArtifactCard({ artifact, onStatusChange, onOptionContinue, onResearch, onDismiss }: { artifact: Artifact; onStatusChange: (status: "approve" | "reject") => void; onOptionContinue?: (option: Record<string, unknown>) => void; onResearch?: (prompt: string) => void; onDismiss?: () => void }) {
	const [selectedOption, setSelectedOption] = useState<number | null>(null);
	const options = getArtifactOptions(artifact);
	const researchPrompt = getResearchPrompt(artifact);
	const optionKey = Object.entries(artifact.content).find(([, value]) => Array.isArray(value))?.[0];
	const entries = Object.entries(artifact.content).filter(([key, value]) => key !== optionKey && value !== null && value !== undefined && value !== "");
	return <article className="artifact-card"><div className="artifact-card-head"><span className="artifact-kicker"><Sparkles size={13} /> AI PROPOSAL</span><span className={`artifact-status ${artifact.status}`}>{artifact.status === "applied" ? "적용됨" : artifact.status === "approved" ? "승인됨" : artifact.status === "rejected" ? "보류됨" : "검토 필요"}</span><button className="artifact-dismiss" onClick={onDismiss} title="닫기" aria-label="추천 닫기"><X size={14} /></button></div><h4>{options ? "추천 방향을 선택하세요" : researchPrompt ? "추가 정보가 필요해요" : artifact.title}</h4>{options ? <div className="artifact-options">{options.map((option, index) => <button key={index} className={selectedOption === index ? "artifact-option selected" : "artifact-option"} onClick={() => setSelectedOption(index)}><span className="option-number">{String(index + 1).padStart(2, "0")}</span><span className="option-copy"><strong>{String(option.direction ?? option.title ?? `추천 방향 ${index + 1}`)}</strong>{Object.entries(option).filter(([key]) => !["direction", "title"].includes(key)).slice(0, 2).map(([key, value]) => <small key={key}>{Array.isArray(value) ? value.join(" · ") : String(value)}</small>)}</span><span className="option-check">{selectedOption === index ? "선택됨" : "선택"}</span></button>)}</div> : researchPrompt ? <div className="artifact-prompt-preview"><span>RESEARCH PROMPT</span><p>{researchPrompt.slice(0, 360)}{researchPrompt.length > 360 ? "..." : ""}</p></div> : <div className="artifact-content">{entries.map(([key, value]) => <div className="artifact-field" key={key}><span>{key.replaceAll("_", " ")}</span><strong>{typeof value === "object" ? JSON.stringify(value) : String(value)}</strong></div>)}</div>}{(artifact.status === "draft" || artifact.status === "pending") && <div className="artifact-actions">{researchPrompt ? <button className="artifact-approve" onClick={() => researchPrompt && onResearch?.(researchPrompt)}><Search size={14} /> Deep Research로 실행</button> : <><button onClick={() => onStatusChange("reject")}>보류</button>{options ? <button className="artifact-approve" disabled={selectedOption === null} onClick={() => selectedOption !== null && onOptionContinue?.(options[selectedOption])}><CircleCheck size={14} /> {selectedOption === null ? "먼저 선택" : "이 방향으로 진행"}</button> : <button className="artifact-approve" onClick={() => onStatusChange("approve")}><CircleCheck size={14} /> 적용 검토</button>}</>}</div>}</article>;
}

function LoginScreen({ onDemo, onLogin, onSignup, theme, onToggleTheme }: { onDemo: () => void; onLogin: (email: string, password: string) => Promise<void>; onSignup: (email: string, password: string) => Promise<void>; theme: ThemeMode; onToggleTheme: () => void }) {
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [error, setError] = useState("");
	const [isSignup, setIsSignup] = useState(false);
	const submit = async (event: FormEvent) => {
		event.preventDefault();
		setError("");
		try { await (isSignup ? onSignup(email, password) : onLogin(email, password)); } catch (caught) { setError(caught instanceof Error ? caught.message : "요청에 실패했어요."); }
	};
	return (
		<main className="auth-shell">
			<div className="auth-glow" />
			<ThemeToggle theme={theme} onToggle={onToggleTheme} />
			<section className="auth-card">
				<div className="brand-mark"><img src={theme === "dark" ? "/brand/main-logo-white.png" : "/brand/main-logo-black.png"} alt="NAME TAG" /></div>
				<p className="eyebrow">AI BRAND WORKSPACE</p>
				<h1>{isSignup ? <>새로운 작업을<br /><em>시작하세요.</em></> : <>생각을 브랜드로<br /><em>이어가세요.</em></>}</h1>
				<p className="auth-copy">사업 아이디어부터 시장, 고객, 비주얼까지<br />하나의 작업 공간에서 계속 발전시켜요.</p>
				<form onSubmit={submit} className="auth-form">
					<label>이메일<input value={email} onChange={(event) => setEmail(event.target.value)} type="email" placeholder="name@example.com" required /></label>
					<label>비밀번호<input value={password} onChange={(event) => setPassword(event.target.value)} type="password" placeholder="••••••••" required /></label>
					{error && <p className="form-error">{error}</p>}
					<button className="primary-button" type="submit">{isSignup ? <UserPlus size={17} /> : <LogIn size={17} />} {isSignup ? "회원가입" : "로그인"}</button>
				</form>
				<button className="demo-button" onClick={() => { setIsSignup((current) => !current); setError(""); }}>{isSignup ? "이미 계정이 있나요? 로그인" : "처음이신가요? 무료로 회원가입"}</button>
				<button className="demo-button" onClick={onDemo}>Demo Workspace 열기 <ArrowUpRight size={15} /></button>
				<p className="auth-note">Backend가 실행 중이면 실제 세션과 Brand 데이터가 연결됩니다.</p>
			</section>
		</main>
	);
}

function Workspace({ onLogout, liveBrandId, user, theme, onToggleTheme }: { onLogout: () => void; liveBrandId: string | null; user: CurrentUser; theme: ThemeMode; onToggleTheme: () => void }) {
	const queryClient = useQueryClient();
	const brandStateQuery = useBrandState(liveBrandId);
	const [section, setSection] = useState<Section>("Overview");
	const [messages, setMessages] = useState<Message[]>([{ role: "assistant", text: "좋아요. 지금까지의 브랜드 방향을 한 화면에 정리했어요. 어디부터 더 선명하게 만들어볼까요?" }]);
	const [input, setInput] = useState("");
	const [saving, setSaving] = useState(false);
	const [activeArtifact, setActiveArtifact] = useState<Artifact | null>(null);
	const [conversationId, setConversationId] = useState<string | null>(null);
	const [conversationSummaries, setConversationSummaries] = useState<ConversationSummary[]>([]);
	const [liveState, setLiveState] = useState<WorkspaceState>(liveBrandId ? emptyState : demoState);
	const [researchQuery, setResearchQuery] = useState("");
	const [researchReport, setResearchReport] = useState<ResearchReport | null>(null);
	const [researchBusy, setResearchBusy] = useState(false);
	const [proposedFindingIds, setProposedFindingIds] = useState<string[]>([]);
	const [historyEntries, setHistoryEntries] = useState<HistoryEntry[]>([]);
	const [assets, setAssets] = useState<Asset[]>([]);
	const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
	const [documents, setDocuments] = useState<DocumentRecord[]>([]);
	const [proposals, setProposals] = useState<ProposalPayload[]>([]);
	const [exportData, setExportData] = useState<ExportPayload | null>(null);
	const conversationRef = useRef<HTMLDivElement>(null);
	const composerInputRef = useRef<HTMLTextAreaElement>(null);
	const shouldStickToBottom = useRef(true);
	const messagesEndRef = useRef<HTMLDivElement>(null);
	const loadConversation = async (id: string) => {
		const stored = await api<StoredMessage[]>(`/api/conversations/${id}/messages`);
		setConversationId(id);
		setMessages(stored.map((message) => ({ role: message.role, text: message.content })));
		shouldStickToBottom.current = true;
	};
	const refreshConversations = async (selectLatest = true) => {
		if (!liveBrandId) return;
		const conversations = await api<ConversationSummary[]>(`/api/brands/${liveBrandId}/conversations`);
		setConversationSummaries(conversations);
		if (selectLatest && conversations[0]) await loadConversation(conversations[0].id);
	};
	useEffect(() => {
		setLiveState(liveBrandId ? emptyState : demoState);
		setConversationId(null);
		setConversationSummaries([]);
		setMessages(liveBrandId ? [] : [{ role: "assistant", text: "좋아요. 지금까지의 브랜드 방향을 한 화면에 정리했어요. 어디부터 더 선명하게 만들어볼까요?" }]);
		refreshConversations().catch(() => undefined);
	}, [liveBrandId]);
	useEffect(() => {
		if (shouldStickToBottom.current) messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
	}, [messages]);
	useEffect(() => {
		const textarea = composerInputRef.current;
		if (!textarea) return;
		const maxHeight = 210;
		textarea.style.height = "auto";
		const nextHeight = Math.min(textarea.scrollHeight, maxHeight);
		textarea.style.height = `${nextHeight}px`;
		textarea.style.overflowY = textarea.scrollHeight > maxHeight ? "auto" : "hidden";
	}, [input]);
	useEffect(() => {
		if (!liveBrandId || !brandStateQuery.data) return;
		const state = brandStateQuery.data.state;
		setLiveState(() => ({
			business: { service: String(state.business?.service ?? ""), problem: String(state.business?.problem ?? "") },
			market: { trend: String(state.market?.trends ?? ""), competitors: String(state.market?.competitors ?? "") },
			customer: { target: String(state.customer?.target ?? ""), need: String(state.customer?.needs ?? "") },
			brand: { name: String(state.brand?.name ?? ""), positioning: String(state.brand?.positioning ?? ""), tone: String(state.brand?.tone ?? "") },
			visual: { mood: String(state.visual?.mood ?? ""), palette: [], colors: Array.isArray(state.visual?.colors) ? state.visual.colors : [], typography: state.visual?.typography ?? null, logo: state.visual?.logo ?? null, character: state.visual?.character ?? null },
		}));
	}, [brandStateQuery.data, liveBrandId]);
	useEffect(() => {
		if (!liveBrandId) return;
		Promise.all([
			api<HistoryEntry[]>(`/api/brands/${liveBrandId}/history`),
			api<Asset[]>(`/api/brands/${liveBrandId}/assets`),
			api<Snapshot[]>(`/api/brands/${liveBrandId}/snapshots`),
			api<DocumentRecord[]>(`/api/brands/${liveBrandId}/documents`),
			api<ProposalPayload[]>(`/api/brands/${liveBrandId}/proposals`),
		]).then(([history, loadedAssets, loadedSnapshots, loadedDocuments, loadedProposals]) => {
			setHistoryEntries(history);
			setAssets(loadedAssets);
			setSnapshots(loadedSnapshots);
			setDocuments(loadedDocuments);
			setProposals(loadedProposals);
		}).catch(() => undefined);
		api<ExportPayload>(`/api/brands/${liveBrandId}/export`, { method: "POST", body: JSON.stringify({ format: "json" }) })
			.then(setExportData)
			.catch(() => setExportData(null));
	}, [liveBrandId]);
	const brandName = liveState.brand.name || "새 Brand";
	const nav = [
		["Overview", LayoutDashboard], ["Business", BriefcaseBusiness], ["Market", BarChart3], ["Customer", Users], ["Brand", Sparkles], ["Visual", Palette], ["Research", Search], ["Assets", FolderOpen], ["Documents", FileText], ["History", HistoryIcon], ["Export", FileJson],
	] as const;
	const sendMessage = async (event: FormEvent) => {
		event.preventDefault();
		if (!input.trim()) return;
		const message = input.trim();
		const options = getArtifactOptions(activeArtifact);
		const optionNumber = message.match(/(?:선택|고를게|고르|번)?\s*(\d+)\s*번?/i)?.[1];
		if (options && optionNumber) {
			const selectedIndex = Number(optionNumber) - 1;
			if (selectedIndex >= 0 && selectedIndex < options.length) {
				setInput("");
				await continueWithOption(options[selectedIndex]);
				return;
			}
		}
		setMessages((current) => [...current, { role: "user", text: message }]);
		setInput("");
		setSaving(true);
		try {
			if (liveBrandId) {
				const result = await api<AgentChatResult>("/api/agent/chat", { method: "POST", body: JSON.stringify({ brand_id: liveBrandId, conversation_id: conversationId, message }) });
				const artifact = toChatArtifact(result);
				setConversationId(result.conversation_id);
				setActiveArtifact(artifact);
				setConversationSummaries((current) => [{ id: result.conversation_id, title: current.find((item) => item.id === result.conversation_id)?.title ?? message, updated_at: new Date().toISOString() }, ...current.filter((item) => item.id !== result.conversation_id)]);
				setMessages((current) => [...current, { role: "assistant", text: result.message, artifact: artifact ?? undefined }]);
			} else {
				await new Promise((resolve) => setTimeout(resolve, 450));
				setMessages((current) => [...current, { role: "assistant", text: "좋아요. 그 방향을 BrandState에 반영할 수 있도록 제안으로 정리했어요." }]);
			}
		} catch (caught) { setMessages((current) => [...current, { role: "assistant", text: caught instanceof Error ? caught.message : "잠시 후 다시 시도해주세요." }]); }
		finally { setSaving(false); }
	};
	const startNewChat = () => {
		setConversationId(null);
		setMessages([]);
		shouldStickToBottom.current = true;
	};
	const deleteCurrentChat = async () => {
		if (!conversationId) return;
		await api(`/api/conversations/${conversationId}`, { method: "DELETE" });
		setConversationSummaries((current) => current.filter((item) => item.id !== conversationId));
		startNewChat();
	};
	const updateArtifactStatus = async (artifact: Artifact, status: "approve" | "reject") => {
		if (!liveBrandId) return;
		try {
		if (artifact.type === "research_job") {
			if (status === "approve") {
				await api(`/api/research/jobs/${artifact.id}/approve`, { method: "POST" });
				await api(`/api/research/jobs/${artifact.id}/start`, { method: "POST" });
				setActiveArtifact(null);
				setSection("Research");
				setResearchBusy(true);
				await waitForResearchReport(artifact.id);
				setMessages((current) => [...current, { role: "assistant", text: "Deep Research를 시작했습니다. Research 화면에서 진행 상태와 결과를 확인할 수 있습니다." }]);
			}
			setActiveArtifact(null);
		} else if (artifact.proposalId) {
			if (status === "approve") {
				await api(`/api/brands/${liveBrandId}/proposals/${artifact.proposalId}/approve`, { method: "POST" });
				await api(`/api/brands/${liveBrandId}/proposals/${artifact.proposalId}/apply`, { method: "POST" });
			} else {
				await api(`/api/brands/${liveBrandId}/proposals/${artifact.proposalId}/reject`, { method: "POST" });
			}
		} else {
			const endpoint = status === "approve" ? "apply" : "reject";
			await api(`/api/brands/${liveBrandId}/artifacts/${artifact.id}/${endpoint}`, { method: "POST" });
		}
		if (status === "approve") {
			queryClient.invalidateQueries({ queryKey: brandStateQueryKey(liveBrandId) });
			const payload = await api<BrandStatePayload>(`/api/brands/${liveBrandId}/state`);
			const state = payload.state;
			setLiveState({ business: { service: String(state.business?.service ?? ""), problem: String(state.business?.problem ?? "") }, market: { trend: String(state.market?.trends ?? ""), competitors: String(state.market?.competitors ?? "") }, customer: { target: String(state.customer?.target ?? ""), need: String(state.customer?.needs ?? "") }, brand: { name: String(state.brand?.name ?? ""), positioning: String(state.brand?.positioning ?? ""), tone: String(state.brand?.tone ?? "") }, visual: { mood: String(state.visual?.mood ?? ""), palette: [], colors: Array.isArray(state.visual?.colors) ? state.visual.colors : [], typography: state.visual?.typography ?? null, logo: state.visual?.logo ?? null, character: state.visual?.character ?? null } });
		}
		setMessages((current) => current.map((message) => message.artifact?.id === artifact.id ? { ...message, artifact: { ...artifact, status: status === "approve" ? "applied" : "rejected" } } : message));
		setActiveArtifact(null);
		} catch (caught) {
			setResearchBusy(false);
			setMessages((current) => [...current, { role: "assistant", text: caught instanceof Error ? `제안을 적용하지 못했어요: ${caught.message}` : "제안을 적용하지 못했어요." }]);
		}
	};
	const continueWithOption = async (option: Record<string, unknown>) => {
		if (!liveBrandId) return;
		const direction = String(option.direction ?? option.title ?? "선택한 방향");
		const request = `선택한 퍼스널 브랜드 방향 '${direction}'으로 진행해줘. 이 방향을 기준으로 다음 작업을 구체화해줘.\n${JSON.stringify(option)}`;
		setMessages((current) => [...current, { role: "user", text: `선택: ${direction}` }]);
		setSaving(true);
		try {
			const result = await api<AgentChatResult>("/api/agent/chat", { method: "POST", body: JSON.stringify({ brand_id: liveBrandId, conversation_id: conversationId, message: request }) });
			const artifact = toChatArtifact(result);
			setConversationId(result.conversation_id);
			setActiveArtifact(artifact);
			setMessages((current) => [...current, { role: "assistant", text: result.message, artifact: artifact ?? undefined }]);
		} catch (caught) {
			setMessages((current) => [...current, { role: "assistant", text: caught instanceof Error ? caught.message : "선택한 방향을 적용하지 못했어요." }]);
		} finally {
			setSaving(false);
		}
	};
	const waitForResearchReport = async (jobId: string) => {
		let jobStatus = "queued";
		for (let attempt = 0; attempt < 60 && jobStatus !== "completed"; attempt += 1) {
			await new Promise((resolve) => setTimeout(resolve, 1000));
			const status = await api<{ status: string }>(`/api/research/jobs/${jobId}`);
			jobStatus = status.status;
			if (jobStatus === "failed" || jobStatus === "cancelled") throw new Error(`Deep Research ${jobStatus}`);
		}
		if (jobStatus !== "completed") throw new Error("Deep Research timed out");
		const report = await api<ResearchReport>(`/api/research/jobs/${jobId}/report`);
		setResearchReport(report);
		setResearchBusy(false);
	};
	const runDeepResearchQuery = async (query: string) => {
		if (!liveBrandId || !query.trim()) return;
		setResearchBusy(true);
		try {
			const plan = await api<{ title: string; objective: string; questions: string[]; scope: string[]; output_type: string }>("/api/research/plan", { method: "POST", body: JSON.stringify({ brand_id: liveBrandId, query: query.trim() }) });
			const job = await api<{ id: string }>("/api/research/jobs", { method: "POST", body: JSON.stringify({ brand_id: liveBrandId, query: query.trim(), plan }) });
			await api(`/api/research/jobs/${job.id}/approve`, { method: "POST" });
			await api(`/api/research/jobs/${job.id}/start`, { method: "POST" });
			await waitForResearchReport(job.id);
		} catch (caught) {
			setResearchReport({ id: "failed", title: "Research failed", executive_summary: caught instanceof Error ? caught.message : "Deep Research를 실행하지 못했어요.", status: "failed", findings: [] });
		} finally { setResearchBusy(false); }
	};
	const runDeepResearch = async (event: FormEvent) => {
		event.preventDefault();
		await runDeepResearchQuery(researchQuery);
	};
	const proposeResearchFinding = async (findingId: string) => {
		if (!liveBrandId || !researchReport || proposedFindingIds.includes(findingId)) return;
		const created = await api<{ proposal_id: string }>(`/api/research/reports/${researchReport.id}/findings/${findingId}/propose`, { method: "POST" });
		const proposal = await api<ProposalPayload>(`/api/brands/${liveBrandId}/proposals/${created.proposal_id}`);
		setActiveArtifact({
			id: proposal.id,
			type: "proposal",
			title: proposal.title,
			content: { summary: proposal.summary, changes: proposal.changes },
			status: proposal.status,
			proposalId: proposal.id,
		});
		setProposedFindingIds((current) => [...current, findingId]);
	};
	const exportBrand = async () => {
		if (!liveBrandId) return;
		const payload = await api<Record<string, unknown>>(`/api/brands/${liveBrandId}/export`, { method: "POST", body: JSON.stringify({ format: "json" }) });
		setExportData(payload);
		const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
		const url = URL.createObjectURL(blob);
		const anchor = document.createElement("a");
		anchor.href = url;
		anchor.download = `${brandName.toLowerCase().replaceAll(" ", "-") || "brand"}-export.json`;
		anchor.click();
		URL.revokeObjectURL(url);
	};
	const restoreSnapshot = async (snapshotId: string) => {
		if (!liveBrandId) return;
		await api(`/api/brands/${liveBrandId}/snapshots/${snapshotId}/restore`, { method: "POST" });
		const payload = await api<BrandStatePayload>(`/api/brands/${liveBrandId}/state`);
		const state = payload.state;
		setLiveState({ business: { service: String(state.business?.service ?? ""), problem: String(state.business?.problem ?? "") }, market: { trend: String(state.market?.trends ?? ""), competitors: String(state.market?.competitors ?? "") }, customer: { target: String(state.customer?.target ?? ""), need: String(state.customer?.needs ?? "") }, brand: { name: String(state.brand?.name ?? ""), positioning: String(state.brand?.positioning ?? ""), tone: String(state.brand?.tone ?? "") }, visual: { mood: String(state.visual?.mood ?? ""), palette: [], colors: Array.isArray(state.visual?.colors) ? state.visual.colors : [], typography: state.visual?.typography ?? null, logo: state.visual?.logo ?? null, character: state.visual?.character ?? null } });
		const history = await api<HistoryEntry[]>(`/api/brands/${liveBrandId}/history`);
		setHistoryEntries(history);
	};
	const createDocument = async () => {
		if (!liveBrandId) return;
		const document = await api<DocumentRecord>(`/api/brands/${liveBrandId}/documents`, { method: "POST", body: JSON.stringify({ title: "새 Brand 문서" }) });
		setDocuments((current) => [document, ...current]);
	};
	const createAsset = async (filename: string) => {
		if (!liveBrandId || !filename.trim()) return;
		const asset = await api<Asset>(`/api/brands/${liveBrandId}/assets`, { method: "POST", body: JSON.stringify({ type: "document", filename: filename.trim(), mime_type: "text/plain", storage_path: `workspace://${filename.trim()}`, metadata: { source: "workspace" } }) });
		setAssets((current) => [asset, ...current]);
	};
	const deleteAsset = async (assetId: string) => {
		if (!liveBrandId) return;
		await api(`/api/brands/${liveBrandId}/assets/${assetId}`, { method: "DELETE" });
		setAssets((current) => current.filter((asset) => asset.id !== assetId));
	};
	return (
		<div className="workspace-shell">
			<aside className="sidebar">
				<div className="sidebar-logo"><img src="/brand/main-logo-white.png" alt="NAME TAG" /></div>
				<button className="brand-switcher"><span className="brand-avatar">{brandName.slice(0, 1)}</span><span><small>현재 Brand</small>{brandName}</span><ChevronDown size={16} /></button>
				<div className="nav-label">WORKSPACE</div>
				<nav>{nav.map(([label, Icon]) => <button key={label} className={section === label ? "nav-item active" : "nav-item"} onClick={() => setSection(label)}><Icon size={17} />{label}</button>)}</nav>
				<div className="chat-history"><div className="chat-history-heading"><span><MessageSquare size={13} /> CHATS</span><button onClick={startNewChat} title="새 대화"><Plus size={15} /></button></div>{conversationSummaries.slice(0, 4).map((conversation) => <button key={conversation.id} className={conversation.id === conversationId ? "chat-history-item active" : "chat-history-item"} onClick={() => loadConversation(conversation.id)}>{conversation.title || "새 대화"}</button>)}{conversationId && <button className="chat-delete-button" onClick={() => deleteCurrentChat().catch(() => undefined)}><Trash2 size={13} /> 현재 대화 삭제</button>}</div>
				<div className="sidebar-bottom"><div className="saved-state"><CircleCheck size={15} /> All changes saved</div><button className="user-row" onClick={onLogout}><span className="user-avatar">{user.email.slice(0, 1).toUpperCase()}</span><span><strong>{user.email}</strong><small>로그아웃</small></span><ArrowUpRight size={14} /></button></div>
			</aside>
			<main className="workspace-main">
				<header className="topbar"><div><p className="breadcrumb">{brandName} <span>/</span> {section}</p><h2>{section === "Overview" ? "브랜드의 현재 모습" : section}</h2></div><div className="top-actions"><span className="live-pill"><i /> {liveBrandId ? "Connected" : "Demo mode"}</span><ThemeToggle theme={theme} onToggle={onToggleTheme} /><button className="icon-button" title="문서 보기"><FileText size={17} /></button><button className="export-button" onClick={() => exportBrand().catch(() => undefined)}>Export <ChevronDown size={15} /></button></div></header>
				<div className="content-scroll">
					{section === "Overview" ? <Overview state={liveState} proposals={proposals} history={historyEntries} assets={assets} documents={documents} exportData={exportData} onNavigate={setSection} onOpenProposal={(proposal) => setActiveArtifact({ id: proposal.id, type: "proposal", title: proposal.title, content: { summary: proposal.summary, changes: proposal.changes }, status: proposal.status, proposalId: proposal.id })} /> : section === "Research" ? <ResearchView query={researchQuery} setQuery={setResearchQuery} report={researchReport} busy={researchBusy} proposedFindingIds={proposedFindingIds} onProposeFinding={proposeResearchFinding} onRun={runDeepResearch} /> : section === "Visual" ? <VisualIdentityView visual={liveState.visual} /> : section === "Assets" ? <AssetsView assets={assets} onCreate={createAsset} onDelete={deleteAsset} /> : section === "Documents" ? <DocumentsView documents={documents} onCreate={createDocument} /> : section === "History" ? <HistoryView entries={historyEntries} snapshots={snapshots} onRestore={restoreSnapshot} /> : section === "Export" ? <ExportView data={exportData} /> : <DomainWorkspaceView section={section} state={liveState} exportData={exportData} />}
				</div>
			</main>
			<aside className="consultant-panel legacy-consultant"><div className="consultant-head"><div><span className="ai-orb"><img src={theme === "dark" ? "/brand/symbol-white.png" : "/brand/symbol-black.png"} alt="" /></span><div><strong>AI Consultant</strong><small>Brand context aware</small></div></div><div className="consultant-actions"><button onClick={() => deleteCurrentChat().catch(() => undefined)} disabled={!conversationId} title="현재 대화 삭제"><Trash2 size={15} /></button><span className="online-dot" /></div></div><div className="conversation" ref={conversationRef} onScroll={(event) => { const target = event.currentTarget; shouldStickToBottom.current = target.scrollHeight - target.scrollTop - target.clientHeight < 80; }}>{messages.length === 0 && <div className="chat-empty"><MessageSquare size={19} /><strong>새 대화를 시작하세요</strong><span>사업, 고객, 시장에 대해 자유롭게 물어보세요.</span></div>}{messages.map((message, index) => <div key={`${message.role}-${index}`} className={`chat-message ${message.role}`}>{message.role === "assistant" && <span className="message-avatar"><img src={theme === "dark" ? "/brand/symbol-white.png" : "/brand/symbol-black.png"} alt="NAME TAG AI" /></span>}<div className="message-body"><span className="message-label">{message.role === "assistant" ? "AI CONSULTANT" : "YOU"}</span><div className="message-content"><ReactMarkdown remarkPlugins={[remarkGfm]}>{message.text}</ReactMarkdown></div>{message.role === "assistant" && index === 0 && <div className="suggestion"><Lightbulb size={15} /><span>Positioning을 더 구체화해볼까요?</span><ArrowUpRight size={14} /></div>}</div></div>)}{saving && <div className="typing"><i /><i /><i /></div>}<div ref={messagesEndRef} /></div><form className="composer" onSubmit={sendMessage}><textarea ref={composerInputRef} value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} rows={1} placeholder="무엇을 만들고 싶나요?" aria-label="AI Consultant 메시지" /><button type="submit" aria-label="메시지 보내기"><Send size={17} /></button></form><div className="composer-hint"><span>⌘/Ctrl Enter</span> to send <span className="hint-right">Context: {section}</span></div></aside>
			<aside className="consultant-panel"><div className="consultant-head"><div><span className="ai-orb"><img src={theme === "dark" ? "/brand/symbol-white.png" : "/brand/symbol-black.png"} alt="" /></span><div><strong>AI Consultant</strong><small>Brand context aware</small></div></div><div className="consultant-actions"><button onClick={() => deleteCurrentChat().catch(() => undefined)} disabled={!conversationId} title="현재 대화 삭제"><Trash2 size={15} /></button><span className="online-dot" /></div></div><div className="conversation" ref={conversationRef} onScroll={(event) => { const target = event.currentTarget; shouldStickToBottom.current = target.scrollHeight - target.scrollTop - target.clientHeight < 80; }}>{messages.length === 0 && <div className="chat-empty"><MessageSquare size={19} /><strong>새 대화를 시작하세요</strong><span>사업, 고객, 시장에 대해 자유롭게 물어보세요.</span></div>}{messages.map((message, index) => <div key={`${message.role}-${index}`} className={`chat-message ${message.role}`}>{message.role === "assistant" && <span className="message-avatar"><img src={theme === "dark" ? "/brand/symbol-white.png" : "/brand/symbol-black.png"} alt="NAME TAG AI" /></span>}<div className="message-body"><span className="message-label">{message.role === "assistant" ? "AI CONSULTANT" : "YOU"}</span><div className="message-content"><ReactMarkdown remarkPlugins={[remarkGfm]}>{message.text}</ReactMarkdown></div>{message.role === "assistant" && index === 0 && <div className="suggestion"><Lightbulb size={15} /><span>Positioning을 더 구체화해볼까요?</span><ArrowUpRight size={14} /></div>}</div></div>)}{saving && <div className="typing"><i /><i /><i /></div>}<div ref={messagesEndRef} /></div><form className="composer" onSubmit={sendMessage}><textarea ref={composerInputRef} value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.metaKey && !event.ctrlKey) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} rows={1} placeholder="무엇을 만들고 싶나요?" aria-label="AI Consultant 메시지" /><button type="submit" aria-label="메시지 보내기"><Send size={17} /></button></form><div className="composer-hint"><span>Enter</span> to send · <span>⌘/Ctrl Enter</span> for line break <span className="hint-right">Context: {section}</span></div></aside>
			{activeArtifact && <div className="artifact-toast"><ArtifactCard artifact={activeArtifact} onOptionContinue={continueWithOption} onResearch={runDeepResearchQuery} onDismiss={() => setActiveArtifact(null)} onStatusChange={async (status) => { await updateArtifactStatus(activeArtifact, status); setActiveArtifact((current) => current ? { ...current, status: status === "approve" ? "approved" : "rejected" } : current); }} /></div>}
		</div>
	);
}

function Overview({ state, proposals, history, assets, documents, exportData, onNavigate, onOpenProposal }: { state: WorkspaceState; proposals: ProposalPayload[]; history: HistoryEntry[]; assets: Asset[]; documents: DocumentRecord[]; exportData: ExportPayload | null; onNavigate: (section: Section) => void; onOpenProposal: (proposal: ProposalPayload) => void }) {
	const pending = proposals.filter((proposal) => proposal.status === "pending");
	const research = Array.isArray(exportData?.research) ? exportData.research as Array<Record<string, unknown>> : [];
	const artifacts = Array.isArray(exportData?.artifacts) ? exportData.artifacts as Array<Record<string, unknown>> : [];
	const brandRecord = asObject(exportData?.brand);
	const missing = [!state.business.problem && "Business problem", !state.customer.target && "Customer target", !state.brand.positioning && "Brand positioning", !state.visual.mood && "Visual mood"].filter(Boolean) as string[];
	const nextAction = pending[0] ? { eyebrow: "REVIEW NEEDED", title: pending[0].title, detail: "승인 대기 중인 제안이 있습니다. 확정된 BrandState와 분리해서 검토하세요.", action: "제안 검토", run: () => onOpenProposal(pending[0]) } : missing.length ? { eyebrow: "NEXT FOUNDATION", title: missing[0], detail: "이 항목이 아직 BrandState에 확정되지 않았습니다.", action: "해당 영역 열기", run: () => onNavigate(missing[0].startsWith("Business") ? "Business" : missing[0].startsWith("Customer") ? "Customer" : missing[0].startsWith("Visual") ? "Visual" : "Brand") } : { eyebrow: "NEXT MOVE", title: "현재 브랜드를 더 날카롭게", detail: "확정된 정보를 바탕으로 다음 제안을 Consultant와 검토할 수 있습니다.", action: "Brand 열기", run: () => onNavigate("Brand") };
	const snapshot = [
		{ key: "Business", value: state.business.service || state.business.problem, detail: state.business.problem, target: "Business" as Section, tone: "sage" },
		{ key: "Customer", value: state.customer.target, detail: state.customer.need, target: "Customer" as Section, tone: "paper" },
		{ key: "Market", value: state.market.trend, detail: compactValue(state.market.competitors), target: "Market" as Section, tone: "sand" },
		{ key: "Brand", value: state.brand.positioning, detail: state.brand.tone, target: "Brand" as Section, tone: "dark" },
		{ key: "Visual", value: state.visual.mood, detail: state.visual.colors.length ? `${state.visual.colors.length} color tokens` : "컬러 미정", target: "Visual" as Section, tone: "paper" },
	];
	return <section className="overview-command-center"><header className="overview-brand-header"><div><span className="eyebrow">BRAND WORKSPACE</span><h3>{brandRecord.name ? String(brandRecord.name) : "새 Brand"}</h3><p>{textValue(state.brand.positioning, "아직 승인된 포지셔닝이 없습니다.")}</p><small>{textValue(brandRecord.description, "BrandState를 기준으로 브랜드의 현재 상태를 관리합니다.")}</small></div><div className="overview-header-state"><span>STATE SOURCE</span><strong>BrandState v{String(asObject(exportData?.brand_state).version ?? "-")}</strong><small>저장된 BrandState를 기준으로 표시</small></div></header><div className="overview-section-heading"><div><span className="eyebrow">SNAPSHOT</span><h4>현재 브랜드를 구성하는 핵심 정보</h4></div><button className="text-button" onClick={() => onNavigate("Export")}>전체 데이터 보기 <ArrowUpRight size={14} /></button></div><div className="brand-snapshot-grid">{snapshot.map((item) => <article className={`snapshot-card ${item.tone}`} key={item.key} onClick={() => onNavigate(item.target)}><div className="card-kicker">{item.key}</div><h4>{compactValue(item.value, "아직 미정")}</h4><p>{compactValue(item.detail, "추가 정보가 필요합니다.")}</p><span className="snapshot-link">열어보기 <ArrowUpRight size={13} /></span></article>)}</div><div className="overview-main-grid"><section className="overview-progress-panel"><div className="overview-section-heading"><div><span className="eyebrow">BRAND PROGRESS</span><h4>지금 확인할 상태</h4></div><span className="status-note">{pending.length ? "검토 필요" : missing.length ? "상태 확인 필요" : "저장된 정보 확인"}</span></div><div className="progress-rows"><div><span>BrandState 정보 범위</span><strong>{missing.length ? `${5 - missing.length} / 5 영역에 값 있음` : "핵심 영역에 값 있음"}</strong></div><div><span>승인 대기 Proposal</span><strong>{pending.length ? `${pending.length}개` : "없음"}</strong></div><div><span>Research Report</span><strong>{research.length ? `${research.length}개 저장됨` : "아직 없음"}</strong></div></div></section><section className="next-action-panel"><span className="eyebrow">{nextAction.eyebrow}</span><h4>{nextAction.title}</h4><p>{nextAction.detail}</p><button className="dark-button" onClick={nextAction.run}>{nextAction.action} <ArrowUpRight size={14} /></button></section></div>{pending.length > 0 && <section className="overview-list-panel"><div className="overview-section-heading"><div><span className="eyebrow">PENDING PROPOSALS</span><h4>검토 후 승인할 제안</h4></div><span className="status-note">{pending.length} pending</span></div>{pending.slice(0, 3).map((proposal) => <button className="proposal-row" key={proposal.id} onClick={() => onOpenProposal(proposal)}><span><strong>{proposal.title}</strong><small>{proposal.summary}</small></span><ArrowUpRight size={15} /></button>)}</section>}<section className="overview-list-panel"><div className="overview-section-heading"><div><span className="eyebrow">RECENT ACTIVITY</span><h4>최근 저장된 작업</h4></div></div>{history.length || artifacts.length || assets.length || documents.length ? <div className="activity-list">{history.slice(0, 2).map((entry) => <div className="activity-item" key={entry.id}><CircleCheck size={15} /><span><strong>{entry.action.replaceAll("_", " ")}</strong><small>{new Date(entry.created_at).toLocaleString("ko-KR")}</small></span></div>)}{artifacts.slice(-2).reverse().map((artifact) => <div className="activity-item" key={String(artifact.id)}><FileText size={15} /><span><strong>{compactValue(artifact.title, "Artifact")}</strong><small>{compactValue(artifact.status, "저장됨")}</small></span></div>)}<div className="activity-count"><span>Assets {assets.length}</span><span>Documents {documents.length}</span><span>Research {research.length}</span></div></div> : <div className="overview-empty-inline"><Sparkles size={18} /><span>아직 저장된 활동이 없습니다.</span></div>}</section></section>;
}

function ExportView({ data }: { data: ExportPayload | null }) {
	if (!data) return <section className="section-view"><div className="section-title"><span className="eyebrow">EXPORT ARCHIVE</span><h3>아직 내보낼 데이터가 없어요.</h3><p>연결된 Brand를 선택하면 저장된 모든 상태와 산출물을 이곳에서 확인할 수 있습니다.</p></div></section>;
	return <section className="export-view"><div className="section-title"><span className="eyebrow">EXPORT ARCHIVE</span><h3>브랜드 데이터 전체 보기</h3><p>BrandState, Visual, Artifacts, Research, Sources를 원본 JSON 구조 그대로 확인합니다.</p></div><div className="export-grid">{Object.entries(data).map(([key, value]) => <article className="export-section" key={key}><div className="card-kicker">{key.replaceAll("_", " ").toUpperCase()}</div><ExportValue value={value} /></article>)}</div></section>;
}

function AssetsView({ assets, onCreate, onDelete }: { assets: Asset[]; onCreate: (filename: string) => Promise<void>; onDelete: (assetId: string) => Promise<void> }) {
	const [filename, setFilename] = useState("");
	return <section className="section-view"><div className="section-title"><span className="eyebrow">ASSET LIBRARY</span><h3>{assets.length ? `${assets.length}개의 브랜드 자산` : "아직 저장된 자산이 없어요."}</h3><p>업로드된 파일과 생성된 브랜드 자료를 한 곳에서 확인합니다.</p><div className="asset-create-row"><input value={filename} onChange={(event) => setFilename(event.target.value)} placeholder="파일 이름" /><button className="dark-button" type="button" disabled={!filename.trim()} onClick={() => { onCreate(filename).catch(() => undefined); setFilename(""); }}><Plus size={15} /> 자산 저장</button></div></div>{assets.length ? <div className="overview-grid">{assets.map((asset) => <article className="metric-card paper" key={asset.id}><div className="card-kicker">{asset.type}</div><h4>{asset.filename}</h4><p>{asset.mime_type}</p><small>{new Date(asset.created_at).toLocaleDateString("ko-KR")}</small><button className="icon-button" type="button" title="자산 삭제" onClick={() => onDelete(asset.id).catch(() => undefined)}><Trash2 size={14} /></button></article>)}</div> : <div className="empty-action"><div className="empty-icon"><FolderOpen size={22} /></div><h4>첫 번째 브랜드 자산을 저장해보세요.</h4><p>AI Consultant가 만든 결과물이나 브랜드 파일이 이곳에 쌓입니다.</p></div>}</section>;
}

function DocumentsView({ documents, onCreate }: { documents: DocumentRecord[]; onCreate: () => Promise<void> }) {
	return <section className="section-view"><div className="section-title"><span className="eyebrow">DOCUMENTS</span><h3>{documents.length ? `${documents.length}개의 Brand 문서` : "아직 Brand 문서가 없어요."}</h3><p>AI가 만든 전략과 리서치 결과를 편집 가능한 문서로 관리합니다.</p><button className="dark-button" type="button" onClick={() => onCreate().catch(() => undefined)}><Plus size={15} /> 새 문서 만들기</button></div>{documents.length > 0 && <div className="overview-grid">{documents.map((document) => <article className="metric-card paper" key={document.id}><div className="card-kicker">DOCUMENT · {document.blocks.length} BLOCKS</div><h4>{document.title}</h4><p>마지막 수정 {new Date(document.updated_at).toLocaleDateString("ko-KR")}</p></article>)}</div>}</section>;
}

function asObject(value: unknown): Record<string, unknown> {
	return value !== null && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : {};
}

function textValue(value: unknown, fallback = "아직 정리되지 않았어요."): string {
	return typeof value === "string" && value.trim() ? value : fallback;
}

export function compactValue(value: unknown, fallback = "미정"): string {
	if (typeof value === "string" && value.trim()) return value;
	if (typeof value === "number" || typeof value === "boolean") return String(value);
	if (Array.isArray(value)) return value.map((item) => compactValue(item, "")).filter(Boolean).slice(0, 3).join(" · ") || fallback;
	if (value !== null && typeof value === "object") {
		const record = value as Record<string, unknown>;
		const preferred = record.name ?? record.title ?? record.description ?? record.statement;
		return preferred ? compactValue(preferred, fallback) : fallback;
	}
	return fallback;
}

function VisualIdentityView({ visual }: { visual: { mood: string; colors?: unknown[]; typography?: unknown; logo?: unknown; character?: unknown } }) {
	const logo = asObject(visual.logo);
	const concept = asObject(logo.concept);
	const character = asObject(visual.character);
	const guide = asObject(character.character_guide);
	const intro = asObject(guide.intro);
	const reasoning = asObject(guide.reasoning);
	const story = asObject(guide.story);
	const colors = visual.colors ?? [];
	const typography = asObject(visual.typography);
	return <section className="visual-identity-view">
		<div className="visual-identity-header"><div><span className="eyebrow">VISUAL IDENTITY SYSTEM</span><h3>브랜드의 철학을<br /><em>보이는 언어</em>로 정리합니다.</h3><p>PDF의 D-1 Logo Identity와 E-1 Brand Persona 구조를 바탕으로, 생성된 시각 자산을 실제 브랜드 가이드처럼 확인합니다.</p></div><div className="visual-mood-badge"><span>MOOD</span><strong>{textValue(visual.mood, "Visual direction")}</strong></div></div>
		<div className="visual-section-label"><span>D-1</span><strong>Logo Identity & Concept</strong><small>브랜드의 철학과 핵심 가치를 시각적으로 압축한 마스터 로고</small></div>
		<div className="visual-logo-layout"><article className="visual-logo-stage"><div className="visual-logo-mark">{textValue(concept.direction_text, "AI") .slice(0, 2).toUpperCase()}</div><span>LOGO CONCEPT PREVIEW</span></article><div className="visual-logo-copy"><div className="visual-highlight"><span>Design Direction</span><strong>{textValue(concept.direction_text, "아직 로고 방향성이 정리되지 않았어요.")}</strong></div><div className="visual-reason-grid"><article><span>SYMBOL MOTIF</span><p>{textValue(concept.symbol_reason)}</p></article><article><span>COLOR IDENTITY</span><p>{textValue(concept.color_reason)}</p></article></div><div className="visual-promise"><span>BRAND MESSAGE</span><p>{textValue(concept.overall_message, "로고가 전달해야 할 브랜드 메시지를 준비 중입니다.")}</p></div></div></div>
		<div className="visual-section-label"><span>E-1</span><strong>Brand Persona & Character</strong><small>고객과 브랜드 사이의 정서적 유대감을 형성하는 핵심 페르소나</small></div>
		<div className="visual-character-layout"><article className="visual-character-stage"><div className="visual-character-placeholder">{textValue(intro.name, "CHARACTER").slice(0, 1)}</div><span>CHARACTER GUIDE</span></article><div className="visual-character-copy"><div className="visual-persona-name"><span>PERSONA NAME</span><h4>{textValue(intro.name, "캐릭터 이름을 준비 중입니다.")}</h4></div><div className="visual-highlight"><span>WORLDVIEW & ROLE</span><strong>{textValue(story.brand_role)}</strong><p>{textValue(story.background)}</p></div><div className="visual-reason-grid"><article><span>CORE VALUE</span><p>{textValue(intro.symbolic_value)}<br />{textValue(reasoning.selection_reason)}</p></article><article><span>EMOTIONAL LINK</span><p>{textValue(reasoning.emotional_connection)}</p></article></div></div></div>
		<div className="visual-system-grid"><article><span className="card-kicker">COLOR SYSTEM</span>{colors.length ? <div className="visual-color-list">{colors.map((color, index) => { const colorData = asObject(color); const hex = textValue(colorData.hex, typeof color === "string" ? color : "#d8e6d8"); return <div key={index}><i style={{ background: hex }} /><span><strong>{textValue(colorData.name, `Color ${index + 1}`)}</strong><small>{hex} · {textValue(colorData.usage, "Brand palette")}</small></span></div>; })}</div> : <p>컬러 시스템을 준비 중입니다.</p>}</article><article><span className="card-kicker">TYPOGRAPHY</span><h4>{textValue(typography.primary, "Primary typeface 미정")}</h4><p>{textValue(typography.secondary, "Secondary typeface 미정")}</p><small>{textValue(typography.description, "타이포그래피 사용 원칙을 준비 중입니다.")}</small></article></div>
	</section>;
}

function HistoryView({ entries, snapshots, onRestore }: { entries: HistoryEntry[]; snapshots: Snapshot[]; onRestore: (snapshotId: string) => Promise<void> }) {
	return <section className="section-view"><div className="section-title"><span className="eyebrow">BRANDSTATE HISTORY</span><h3>{entries.length ? "브랜드가 이렇게 발전했어요." : "아직 변경 기록이 없어요."}</h3><p>승인된 제안과 Snapshot 복구 기록을 시간순으로 확인합니다.</p></div>{entries.length ? <div className="history-list">{entries.map((entry) => <article className="history-item" key={entry.id}><div><span className="card-kicker">{entry.action.replaceAll("_", " ")}</span><strong>{String(entry.details?.to_version ?? entry.details?.snapshot_version ?? "변경 기록")}</strong></div><time>{new Date(entry.created_at).toLocaleString("ko-KR")}</time></article>)}{snapshots.length > 0 && <div className="empty-action"><h4>이전 상태로 되돌리기</h4>{snapshots.slice(0, 3).map((snapshot) => <button className="dark-button" type="button" key={snapshot.id} onClick={() => onRestore(snapshot.id).catch(() => undefined)}>Version {snapshot.version} 복구</button>)}</div>}</div> : <div className="empty-action"><div className="empty-icon"><HistoryIcon size={22} /></div><h4>첫 번째 제안을 승인하면 기록이 시작됩니다.</h4><p>BrandState에 적용된 변화는 모두 이곳에서 추적할 수 있어요.</p></div>}</section>;
}

function DomainWorkspaceView({ section, state, exportData }: { section: Section; state: WorkspaceState; exportData: ExportPayload | null }) {
	const titles: Record<string, { eyebrow: string; title: string; description: string }> = {
		Business: { eyebrow: "BUSINESS SYSTEM", title: "문제를 사업 구조로 정리합니다.", description: "서비스, 문제, 해결책, 수익 모델을 하나의 실행 가능한 구조로 연결합니다." },
		Market: { eyebrow: "MARKET INTELLIGENCE", title: "시장을 읽고 기회를 좁힙니다.", description: "트렌드, 경쟁사, TAM/SAM/SOM과 SWOT을 근거 중심으로 비교합니다." },
		Customer: { eyebrow: "CUSTOMER PROFILE", title: "고객의 맥락을 선명하게 만듭니다.", description: "타깃, 페르소나, 니즈, 페인포인트를 실제 의사결정에 사용할 수 있게 정리합니다." },
		Brand: { eyebrow: "BRAND CORE", title: "브랜드의 중심 문장을 고정합니다.", description: "포지셔닝, 미션, 가치, 톤을 하나의 일관된 브랜드 시스템으로 관리합니다." },
	};
	const config = titles[section] ?? titles.Brand;
	const fullState = asObject(exportData?.brand_state);
	const sectionData = asObject(fullState.state ? asObject(fullState.state)[section.toLowerCase()] : null);
	const summary = section === "Business" ? [state.business.problem, state.business.service] : section === "Market" ? [state.market.trend, state.market.competitors] : section === "Customer" ? [state.customer.target, state.customer.need] : [state.brand.positioning, state.brand.tone];
	const populated = Object.entries(sectionData).filter(([, value]) => value !== null && value !== "" && !(Array.isArray(value) && value.length === 0));
	return <section className="domain-workspace"><header className="domain-hero"><div><span className="eyebrow">{config.eyebrow}</span><h3>{config.title}</h3><p>{config.description}</p></div><div className="domain-hero-stat"><strong>{populated.length}</strong><span>정리된 필드</span></div></header><div className="domain-summary-grid">{summary.map((value, index) => <article key={index} className={index === 0 ? "domain-summary primary" : "domain-summary"}><span>{index === 0 ? "CURRENT FOCUS" : "NEXT SIGNAL"}</span><strong>{textValue(value, "아직 입력되지 않았어요.")}</strong></article>)}</div><div className="domain-detail-layout"><section className="domain-fields"><div className="domain-panel-heading"><div><span className="card-kicker">WORKSPACE RECORD</span><h4>{config.eyebrow}</h4></div><span>{populated.length} fields</span></div>{populated.length ? populated.map(([key, value]) => <article className="domain-field" key={key}><div><span>{key.replaceAll("_", " ")}</span><ExportValue value={value} /></div></article>) : <div className="domain-empty"><BookOpen size={20} /><strong>아직 정리된 정보가 없어요.</strong><p>오른쪽 AI Consultant에게 {section} 관련 내용을 요청하면 이곳에 누적됩니다.</p></div>}</section><aside className="domain-next"><span className="eyebrow">NEXT MOVE</span><h4>{section === "Market" ? "근거를 더 단단하게" : section === "Customer" ? "고객의 순간을 더 자세하게" : section === "Business" ? "아이디어를 실행 구조로" : "브랜드 문장을 더 날카롭게"}</h4><p>현재 Brand context를 바탕으로 다음 제안을 만들 수 있습니다.</p><button className="dark-button" type="button" onClick={() => undefined}><MessageCircle size={15} /> Consultant에게 요청</button></aside></div></section>;
}

function ResearchView({ query, setQuery, report, busy, proposedFindingIds, onProposeFinding, onRun }: { query: string; setQuery: (value: string) => void; report: ResearchReport | null; busy: boolean; proposedFindingIds: string[]; onProposeFinding: (findingId: string) => Promise<void>; onRun: (event: FormEvent) => void }) {
	return <section className="research-view"><div className="section-title"><span className="eyebrow">DEEP RESEARCH</span><h3>근거가 필요한 질문을<br />깊게 조사하세요.</h3><p>시장, 고객, 경쟁사에 대한 복합 질문을 Research Report와 Finding으로 정리합니다.</p><form className="research-form" onSubmit={onRun}><textarea value={query} onChange={(event) => setQuery(event.target.value)} placeholder="예: 국내 AI 브랜드 워크스페이스 시장의 경쟁사와 진입 기회를 분석해줘" rows={3} /><button className="dark-button" type="submit" disabled={busy || !query.trim()}>{busy ? "Research 실행 중..." : "Deep Research 시작"}</button></form></div>{report ? <article className="research-report"><div className="card-kicker">{report.status.toUpperCase()}</div><h4>{report.title}</h4><div className="research-report-body"><ReactMarkdown remarkPlugins={[remarkGfm]}>{report.executive_summary}</ReactMarkdown></div>{report.sources && report.sources.length > 0 && <div className="research-sources"><span className="card-kicker">SOURCES · {report.sources.length}</span>{report.sources.map((source) => <a key={source.url} href={source.url} target="_blank" rel="noreferrer">{source.title}<small>{source.publisher || source.url}</small></a>)}</div>}<div className="research-findings">{report.findings.map((finding, index) => { const proposed = finding.applied || proposedFindingIds.includes(finding.id); return <div key={finding.id}><span>FINDING {index + 1}</span><strong>{finding.statement}</strong><small>{finding.confidence}</small><button className="dark-button" type="button" disabled={proposed} onClick={() => onProposeFinding(finding.id)}>{proposed ? "제안 생성됨" : "BrandState 제안 만들기"}</button></div>; })}</div></article> : <div className="research-empty"><Search size={22} /><strong>아직 Research Report가 없습니다.</strong><span>왼쪽 질문창에 조사하고 싶은 내용을 입력해보세요.</span></div>}</section>;
}

export default function App() {
	const [mode, setMode] = useState<"login" | "workspace">("login");
	const [theme, setTheme] = useState<ThemeMode>(() => (localStorage.getItem("name-tag-theme") as ThemeMode) || "light");
	const [liveBrandId, setLiveBrandId] = useState<string | null>(null);
	const [user, setUser] = useState<CurrentUser | null>(null);
	useEffect(() => { document.documentElement.dataset.theme = theme; localStorage.setItem("name-tag-theme", theme); }, [theme]);
	const enterWorkspace = async () => { const session = await api<{ user: CurrentUser }>("/api/auth/me"); setUser(session.user); const brands = await api<Array<{ id: string }>>("/api/brands"); if (brands[0]) { setLiveBrandId(brands[0].id); setMode("workspace"); } };
	useEffect(() => { enterWorkspace().catch(() => undefined); }, []);
	const login = async (email: string, password: string) => { await api("/api/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }); const brands = await api<Array<{ id: string }>>("/api/brands"); if (!brands[0]) throw new Error("먼저 Brand를 만들어주세요."); setLiveBrandId(brands[0].id); const session = await api<{ user: CurrentUser }>("/api/auth/me"); setUser(session.user); setMode("workspace"); };
	const signup = async (email: string, password: string) => { await api("/api/auth/signup", { method: "POST", body: JSON.stringify({ email, password }) }); const brand = await api<{ id: string }>("/api/brands", { method: "POST", body: JSON.stringify({ name: "My Brand", description: "새로운 AI Brand Workspace" }) }); setLiveBrandId(brand.id); const session = await api<{ user: CurrentUser }>("/api/auth/me"); setUser(session.user); setMode("workspace"); };
	const logout = async () => { if (liveBrandId) await api("/api/auth/logout", { method: "POST" }).catch(() => undefined); setLiveBrandId(null); setMode("login"); };
	return mode === "login" ? <LoginScreen onDemo={() => setMode("workspace")} onLogin={login} onSignup={signup} theme={theme} onToggleTheme={() => setTheme((current) => current === "light" ? "dark" : "light")} /> : <Workspace onLogout={logout} liveBrandId={liveBrandId} user={user ?? { id: "demo", email: "demo@nametag.local" }} theme={theme} onToggleTheme={() => setTheme((current) => current === "light" ? "dark" : "light")} />;
}
