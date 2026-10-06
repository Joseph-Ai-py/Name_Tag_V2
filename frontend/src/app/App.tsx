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

type Section = "Overview" | "Business" | "Market" | "Customer" | "Brand" | "Visual" | "Research" | "Assets" | "Documents" | "History";
type Artifact = { id: string; type: string; title: string; content: Record<string, unknown>; status: string; proposalId?: string };
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

function getArtifactOptions(artifact: Artifact | null): Array<Record<string, unknown>> | undefined {
	if (!artifact) return undefined;
	const optionEntry = Object.entries(artifact.content).find(([, value]) => Array.isArray(value));
	return optionEntry?.[1] as Array<Record<string, unknown>> | undefined;
}

function getResearchPrompt(artifact: Artifact): string | null {
	const prompt = Object.values(artifact.content).find((value) => typeof value === "string" && (value.includes("프롬프트") || value.length > 500));
	return typeof prompt === "string" ? prompt : null;
}

const demoState = {
	business: { service: "AI Brand Workspace", problem: "브랜드 기획의 맥락이 대화마다 흩어져요." },
	market: { trend: "경험 중심의 초기 브랜드 구축", competitors: "대화형 AI · 브랜드 에이전시" },
	customer: { target: "만들고 있는 것이 있는 예비 창업자", need: "아이디어를 실행 가능한 구조로 정리" },
	brand: { name: "Luma", positioning: "복잡한 시작을 선명한 브랜드로", tone: "명확하고 따뜻하게" },
	visual: { mood: "Quiet confidence", palette: ["#1b4332", "#d8f3dc", "#f4f1eb"] },
};

const emptyState = {
	business: { service: "", problem: "" },
	market: { trend: "", competitors: "" },
	customer: { target: "", need: "" },
	brand: { name: "", positioning: "", tone: "" },
	visual: { mood: "", palette: [] as string[] },
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
	return <article className="artifact-card"><div className="artifact-card-head"><span className="artifact-kicker"><Sparkles size={13} /> AI PROPOSAL</span><span className={`artifact-status ${artifact.status}`}>{artifact.status === "applied" ? "적용됨" : artifact.status === "approved" ? "승인됨" : artifact.status === "rejected" ? "보류됨" : "검토 필요"}</span><button className="artifact-dismiss" onClick={onDismiss} title="닫기" aria-label="추천 닫기"><X size={14} /></button></div><h4>{options ? "추천 방향을 선택하세요" : researchPrompt ? "추가 정보가 필요해요" : artifact.title}</h4>{options ? <div className="artifact-options">{options.map((option, index) => <button key={index} className={selectedOption === index ? "artifact-option selected" : "artifact-option"} onClick={() => setSelectedOption(index)}><span className="option-number">{String(index + 1).padStart(2, "0")}</span><span className="option-copy"><strong>{String(option.direction ?? option.title ?? `추천 방향 ${index + 1}`)}</strong>{Object.entries(option).filter(([key]) => !["direction", "title"].includes(key)).slice(0, 2).map(([key, value]) => <small key={key}>{Array.isArray(value) ? value.join(" · ") : String(value)}</small>)}</span><span className="option-check">{selectedOption === index ? "선택됨" : "선택"}</span></button>)}</div> : researchPrompt ? <div className="artifact-prompt-preview"><span>RESEARCH PROMPT</span><p>{researchPrompt.slice(0, 360)}{researchPrompt.length > 360 ? "..." : ""}</p></div> : <div className="artifact-content">{entries.map(([key, value]) => <div className="artifact-field" key={key}><span>{key.replaceAll("_", " ")}</span><strong>{typeof value === "object" ? JSON.stringify(value) : String(value)}</strong></div>)}</div>}{artifact.status === "draft" && <div className="artifact-actions">{researchPrompt ? <button className="artifact-approve" onClick={() => researchPrompt && onResearch?.(researchPrompt)}><Search size={14} /> Deep Research로 실행</button> : <><button onClick={() => onStatusChange("reject")}>보류</button>{options ? <button className="artifact-approve" disabled={selectedOption === null} onClick={() => selectedOption !== null && onOptionContinue?.(options[selectedOption])}><CircleCheck size={14} /> {selectedOption === null ? "먼저 선택" : "이 방향으로 진행"}</button> : <button className="artifact-approve" onClick={() => onStatusChange("approve")}><CircleCheck size={14} /> 적용 검토</button>}</>}</div>}</article>;
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
	const [liveState, setLiveState] = useState<typeof demoState>(liveBrandId ? emptyState : demoState);
	const [researchQuery, setResearchQuery] = useState("");
	const [researchReport, setResearchReport] = useState<ResearchReport | null>(null);
	const [researchBusy, setResearchBusy] = useState(false);
	const [proposedFindingIds, setProposedFindingIds] = useState<string[]>([]);
	const [historyEntries, setHistoryEntries] = useState<HistoryEntry[]>([]);
	const [assets, setAssets] = useState<Asset[]>([]);
	const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
	const [documents, setDocuments] = useState<DocumentRecord[]>([]);
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
			visual: { mood: String(state.visual?.mood ?? ""), palette: [] },
		}));
	}, [brandStateQuery.data, liveBrandId]);
	useEffect(() => {
		if (!liveBrandId) return;
		Promise.all([
			api<HistoryEntry[]>(`/api/brands/${liveBrandId}/history`),
			api<Asset[]>(`/api/brands/${liveBrandId}/assets`),
			api<Snapshot[]>(`/api/brands/${liveBrandId}/snapshots`),
			api<DocumentRecord[]>(`/api/brands/${liveBrandId}/documents`),
		]).then(([history, loadedAssets, loadedSnapshots, loadedDocuments]) => {
			setHistoryEntries(history);
			setAssets(loadedAssets);
			setSnapshots(loadedSnapshots);
			setDocuments(loadedDocuments);
		}).catch(() => undefined);
	}, [liveBrandId]);
	const brandName = liveState.brand.name || "새 Brand";
	const nav = [
		["Overview", LayoutDashboard], ["Business", BriefcaseBusiness], ["Market", BarChart3], ["Customer", Users], ["Brand", Sparkles], ["Visual", Palette], ["Research", Search], ["Assets", FolderOpen], ["Documents", FileText], ["History", HistoryIcon],
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
				const result = await api<{ message: string; conversation_id: string; artifact: Artifact | null; proposal_id?: string }>("/api/agent/chat", { method: "POST", body: JSON.stringify({ brand_id: liveBrandId, conversation_id: conversationId, message }) });
				const artifact = result.artifact ? { ...result.artifact, proposalId: result.proposal_id } : null;
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
		if (artifact.proposalId) {
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
			setLiveState({ business: { service: String(state.business?.service ?? ""), problem: String(state.business?.problem ?? "") }, market: { trend: String(state.market?.trends ?? ""), competitors: String(state.market?.competitors ?? "") }, customer: { target: String(state.customer?.target ?? ""), need: String(state.customer?.needs ?? "") }, brand: { name: String(state.brand?.name ?? ""), positioning: String(state.brand?.positioning ?? ""), tone: String(state.brand?.tone ?? "") }, visual: { mood: String(state.visual?.mood ?? ""), palette: [] } });
		}
		setMessages((current) => current.map((message) => message.artifact?.id === artifact.id ? { ...message, artifact: { ...artifact, status: status === "approve" ? "applied" : "rejected" } } : message));
		setActiveArtifact(null);
		} catch (caught) {
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
			const result = await api<{ message: string; conversation_id: string; artifact: Artifact | null; proposal_id?: string }>("/api/agent/chat", { method: "POST", body: JSON.stringify({ brand_id: liveBrandId, conversation_id: conversationId, message: request }) });
			const artifact = result.artifact ? { ...result.artifact, proposalId: result.proposal_id } : null;
			setConversationId(result.conversation_id);
			setActiveArtifact(artifact);
			setMessages((current) => [...current, { role: "assistant", text: result.message, artifact: artifact ?? undefined }]);
		} catch (caught) {
			setMessages((current) => [...current, { role: "assistant", text: caught instanceof Error ? caught.message : "선택한 방향을 적용하지 못했어요." }]);
		} finally {
			setSaving(false);
		}
	};
	const runDeepResearchQuery = async (query: string) => {
		if (!liveBrandId || !query.trim()) return;
		setResearchBusy(true);
		try {
			const plan = await api<{ title: string; objective: string; questions: string[]; scope: string[]; output_type: string }>("/api/research/plan", { method: "POST", body: JSON.stringify({ brand_id: liveBrandId, query: query.trim() }) });
			const job = await api<{ id: string }>("/api/research/jobs", { method: "POST", body: JSON.stringify({ brand_id: liveBrandId, query: query.trim(), plan }) });
			await api(`/api/research/jobs/${job.id}/approve`, { method: "POST" });
			await api(`/api/research/jobs/${job.id}/start`, { method: "POST" });
			let jobStatus = "queued";
			for (let attempt = 0; attempt < 60 && jobStatus !== "completed"; attempt += 1) {
				await new Promise((resolve) => setTimeout(resolve, 1000));
				const status = await api<{ status: string }>(`/api/research/jobs/${job.id}`);
				jobStatus = status.status;
				if (jobStatus === "failed" || jobStatus === "cancelled") throw new Error(`Deep Research ${jobStatus}`);
			}
			if (jobStatus !== "completed") throw new Error("Deep Research timed out");
			const report = await api<ResearchReport>(`/api/research/jobs/${job.id}/report`);
			setResearchReport(report);
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
		await api(`/api/research/reports/${researchReport.id}/findings/${findingId}/propose`, { method: "POST" });
		setProposedFindingIds((current) => [...current, findingId]);
	};
	const exportBrand = async () => {
		if (!liveBrandId) return;
		const payload = await api<Record<string, unknown>>(`/api/brands/${liveBrandId}/export`, { method: "POST", body: JSON.stringify({ format: "json" }) });
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
		setLiveState({ business: { service: String(state.business?.service ?? ""), problem: String(state.business?.problem ?? "") }, market: { trend: String(state.market?.trends ?? ""), competitors: String(state.market?.competitors ?? "") }, customer: { target: String(state.customer?.target ?? ""), need: String(state.customer?.needs ?? "") }, brand: { name: String(state.brand?.name ?? ""), positioning: String(state.brand?.positioning ?? ""), tone: String(state.brand?.tone ?? "") }, visual: { mood: String(state.visual?.mood ?? ""), palette: [] } });
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
					<section className="welcome-row"><div><p className="eyebrow">MONDAY, OCTOBER 01</p><h1>좋은 시작이에요,<br /><em>{user.email.split("@")[0]}.</em></h1></div></section>
					{section === "Overview" ? <Overview state={liveState} /> : section === "Research" ? <ResearchView query={researchQuery} setQuery={setResearchQuery} report={researchReport} busy={researchBusy} proposedFindingIds={proposedFindingIds} onProposeFinding={proposeResearchFinding} onRun={runDeepResearch} /> : section === "Assets" ? <AssetsView assets={assets} onCreate={createAsset} onDelete={deleteAsset} /> : section === "Documents" ? <DocumentsView documents={documents} onCreate={createDocument} /> : section === "History" ? <HistoryView entries={historyEntries} snapshots={snapshots} onRestore={restoreSnapshot} /> : <SectionView section={section} state={liveState} />}
				</div>
			</main>
			<aside className="consultant-panel legacy-consultant"><div className="consultant-head"><div><span className="ai-orb"><img src={theme === "dark" ? "/brand/symbol-white.png" : "/brand/symbol-black.png"} alt="" /></span><div><strong>AI Consultant</strong><small>Brand context aware</small></div></div><div className="consultant-actions"><button onClick={() => deleteCurrentChat().catch(() => undefined)} disabled={!conversationId} title="현재 대화 삭제"><Trash2 size={15} /></button><span className="online-dot" /></div></div><div className="conversation" ref={conversationRef} onScroll={(event) => { const target = event.currentTarget; shouldStickToBottom.current = target.scrollHeight - target.scrollTop - target.clientHeight < 80; }}>{messages.length === 0 && <div className="chat-empty"><MessageSquare size={19} /><strong>새 대화를 시작하세요</strong><span>사업, 고객, 시장에 대해 자유롭게 물어보세요.</span></div>}{messages.map((message, index) => <div key={`${message.role}-${index}`} className={`chat-message ${message.role}`}>{message.role === "assistant" && <span className="message-avatar"><img src={theme === "dark" ? "/brand/symbol-white.png" : "/brand/symbol-black.png"} alt="NAME TAG AI" /></span>}<div className="message-body"><span className="message-label">{message.role === "assistant" ? "AI CONSULTANT" : "YOU"}</span><div className="message-content"><ReactMarkdown remarkPlugins={[remarkGfm]}>{message.text}</ReactMarkdown></div>{message.role === "assistant" && index === 0 && <div className="suggestion"><Lightbulb size={15} /><span>Positioning을 더 구체화해볼까요?</span><ArrowUpRight size={14} /></div>}</div></div>)}{saving && <div className="typing"><i /><i /><i /></div>}<div ref={messagesEndRef} /></div><form className="composer" onSubmit={sendMessage}><textarea ref={composerInputRef} value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} rows={1} placeholder="무엇을 만들고 싶나요?" aria-label="AI Consultant 메시지" /><button type="submit" aria-label="메시지 보내기"><Send size={17} /></button></form><div className="composer-hint"><span>⌘/Ctrl Enter</span> to send <span className="hint-right">Context: {section}</span></div></aside>
			<aside className="consultant-panel"><div className="consultant-head"><div><span className="ai-orb"><img src={theme === "dark" ? "/brand/symbol-white.png" : "/brand/symbol-black.png"} alt="" /></span><div><strong>AI Consultant</strong><small>Brand context aware</small></div></div><div className="consultant-actions"><button onClick={() => deleteCurrentChat().catch(() => undefined)} disabled={!conversationId} title="현재 대화 삭제"><Trash2 size={15} /></button><span className="online-dot" /></div></div><div className="conversation" ref={conversationRef} onScroll={(event) => { const target = event.currentTarget; shouldStickToBottom.current = target.scrollHeight - target.scrollTop - target.clientHeight < 80; }}>{messages.length === 0 && <div className="chat-empty"><MessageSquare size={19} /><strong>새 대화를 시작하세요</strong><span>사업, 고객, 시장에 대해 자유롭게 물어보세요.</span></div>}{messages.map((message, index) => <div key={`${message.role}-${index}`} className={`chat-message ${message.role}`}>{message.role === "assistant" && <span className="message-avatar"><img src={theme === "dark" ? "/brand/symbol-white.png" : "/brand/symbol-black.png"} alt="NAME TAG AI" /></span>}<div className="message-body"><span className="message-label">{message.role === "assistant" ? "AI CONSULTANT" : "YOU"}</span><div className="message-content"><ReactMarkdown remarkPlugins={[remarkGfm]}>{message.text}</ReactMarkdown></div>{message.role === "assistant" && index === 0 && <div className="suggestion"><Lightbulb size={15} /><span>Positioning을 더 구체화해볼까요?</span><ArrowUpRight size={14} /></div>}</div></div>)}{saving && <div className="typing"><i /><i /><i /></div>}<div ref={messagesEndRef} /></div><form className="composer" onSubmit={sendMessage}><textarea ref={composerInputRef} value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.metaKey && !event.ctrlKey) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} rows={1} placeholder="무엇을 만들고 싶나요?" aria-label="AI Consultant 메시지" /><button type="submit" aria-label="메시지 보내기"><Send size={17} /></button></form><div className="composer-hint"><span>Enter</span> to send · <span>⌘/Ctrl Enter</span> for line break <span className="hint-right">Context: {section}</span></div></aside>
			{activeArtifact && <div className="artifact-toast"><ArtifactCard artifact={activeArtifact} onOptionContinue={continueWithOption} onResearch={runDeepResearchQuery} onDismiss={() => setActiveArtifact(null)} onStatusChange={async (status) => { await updateArtifactStatus(activeArtifact, status); setActiveArtifact((current) => current ? { ...current, status: status === "approve" ? "approved" : "rejected" } : current); }} /></div>}
		</div>
	);
}

function Overview({ state }: { state: typeof demoState }) {
	const hasContent = Boolean(state.brand.positioning || state.customer.target || state.visual.mood || state.business.service || state.market.trend);
	if (!hasContent) return <section className="overview-empty"><div className="empty-icon"><Sparkles size={20} /></div><p className="eyebrow">YOUR WORKSPACE STARTS HERE</p><h3>아직 정리된 내용이 없어요.</h3><p>오른쪽 AI Consultant와 대화를 시작하면<br />사업과 브랜드 정보가 이곳에 하나씩 쌓입니다.</p></section>;
	return <div className="overview-grid">
		{state.brand.positioning && <article className="hero-card"><div className="card-kicker"><span className="accent-line" /> BRAND POSITIONING</div><h3>{state.brand.positioning}</h3><p>사업의 방향과 고객의 언어가 만나 만들어진 현재의 중심 문장입니다.</p><div className="card-footer"><span>BrandState</span><button>열어보기 <ArrowUpRight size={15} /></button></div></article>}
		{(state.customer.target || state.customer.need) && <article className="metric-card sage"><div className="card-kicker">CUSTOMER</div><h4>{state.customer.target || "고객 정보"}</h4><p>{state.customer.need}</p><div className="metric-icon"><Users size={19} /></div></article>}
		{state.visual.mood && <article className="metric-card dark"><div className="card-kicker">VISUAL MOOD</div><h4>{state.visual.mood}</h4><div className="swatches">{state.visual.palette.map((color) => <i key={color} style={{ background: color }} />)}</div><p>현재 Visual 방향</p></article>}
		{(state.business.service || state.business.problem) && <article className="metric-card paper"><div className="card-kicker">BUSINESS</div><h4>{state.business.service || "사업 방향"}</h4><p>{state.business.problem}</p><div className="metric-icon"><BriefcaseBusiness size={19} /></div></article>}
		{state.market.trend && <article className="metric-card sand"><div className="card-kicker">MARKET</div><h4>{state.market.trend}</h4><p>{state.market.competitors}</p><div className="metric-icon"><BarChart3 size={19} /></div></article>}
	</div>;
}

function AssetsView({ assets, onCreate, onDelete }: { assets: Asset[]; onCreate: (filename: string) => Promise<void>; onDelete: (assetId: string) => Promise<void> }) {
	const [filename, setFilename] = useState("");
	return <section className="section-view"><div className="section-title"><span className="eyebrow">ASSET LIBRARY</span><h3>{assets.length ? `${assets.length}개의 브랜드 자산` : "아직 저장된 자산이 없어요."}</h3><p>업로드된 파일과 생성된 브랜드 자료를 한 곳에서 확인합니다.</p><div className="asset-create-row"><input value={filename} onChange={(event) => setFilename(event.target.value)} placeholder="파일 이름" /><button className="dark-button" type="button" disabled={!filename.trim()} onClick={() => { onCreate(filename).catch(() => undefined); setFilename(""); }}><Plus size={15} /> 자산 저장</button></div></div>{assets.length ? <div className="overview-grid">{assets.map((asset) => <article className="metric-card paper" key={asset.id}><div className="card-kicker">{asset.type}</div><h4>{asset.filename}</h4><p>{asset.mime_type}</p><small>{new Date(asset.created_at).toLocaleDateString("ko-KR")}</small><button className="icon-button" type="button" title="자산 삭제" onClick={() => onDelete(asset.id).catch(() => undefined)}><Trash2 size={14} /></button></article>)}</div> : <div className="empty-action"><div className="empty-icon"><FolderOpen size={22} /></div><h4>첫 번째 브랜드 자산을 저장해보세요.</h4><p>AI Consultant가 만든 결과물이나 브랜드 파일이 이곳에 쌓입니다.</p></div>}</section>;
}

function DocumentsView({ documents, onCreate }: { documents: DocumentRecord[]; onCreate: () => Promise<void> }) {
	return <section className="section-view"><div className="section-title"><span className="eyebrow">DOCUMENTS</span><h3>{documents.length ? `${documents.length}개의 Brand 문서` : "아직 Brand 문서가 없어요."}</h3><p>AI가 만든 전략과 리서치 결과를 편집 가능한 문서로 관리합니다.</p><button className="dark-button" type="button" onClick={() => onCreate().catch(() => undefined)}><Plus size={15} /> 새 문서 만들기</button></div>{documents.length > 0 && <div className="overview-grid">{documents.map((document) => <article className="metric-card paper" key={document.id}><div className="card-kicker">DOCUMENT · {document.blocks.length} BLOCKS</div><h4>{document.title}</h4><p>마지막 수정 {new Date(document.updated_at).toLocaleDateString("ko-KR")}</p></article>)}</div>}</section>;
}

function HistoryView({ entries, snapshots, onRestore }: { entries: HistoryEntry[]; snapshots: Snapshot[]; onRestore: (snapshotId: string) => Promise<void> }) {
	return <section className="section-view"><div className="section-title"><span className="eyebrow">BRANDSTATE HISTORY</span><h3>{entries.length ? "브랜드가 이렇게 발전했어요." : "아직 변경 기록이 없어요."}</h3><p>승인된 제안과 Snapshot 복구 기록을 시간순으로 확인합니다.</p></div>{entries.length ? <div className="history-list">{entries.map((entry) => <article className="history-item" key={entry.id}><div><span className="card-kicker">{entry.action.replaceAll("_", " ")}</span><strong>{String(entry.details?.to_version ?? entry.details?.snapshot_version ?? "변경 기록")}</strong></div><time>{new Date(entry.created_at).toLocaleString("ko-KR")}</time></article>)}{snapshots.length > 0 && <div className="empty-action"><h4>이전 상태로 되돌리기</h4>{snapshots.slice(0, 3).map((snapshot) => <button className="dark-button" type="button" key={snapshot.id} onClick={() => onRestore(snapshot.id).catch(() => undefined)}>Version {snapshot.version} 복구</button>)}</div>}</div> : <div className="empty-action"><div className="empty-icon"><HistoryIcon size={22} /></div><h4>첫 번째 제안을 승인하면 기록이 시작됩니다.</h4><p>BrandState에 적용된 변화는 모두 이곳에서 추적할 수 있어요.</p></div>}</section>;
}

function SectionView({ section, state }: { section: Section; state: typeof demoState }) {
	const values: Record<Section, [string, string, string]> = { Overview: ["", "", ""], Business: ["Problem / Solution", state.business.problem, state.business.service], Market: ["Market direction", state.market.trend, state.market.competitors], Customer: ["Primary audience", state.customer.target, state.customer.need], Brand: ["Positioning", state.brand.positioning, state.brand.tone], Visual: ["Visual direction", state.visual.mood, state.visual.palette.join("  ")], Research: ["Research workspace", "아직 저장된 Deep Research가 없습니다.", "AI Consultant에게 시장 조사를 요청해보세요."], Assets: ["Asset library", "", ""], Documents: ["Document library", "", ""], History: ["BrandState history", "", ""] };
	const [label, title, detail] = values[section];
	return <section className="section-view"><div className="section-title"><span className="eyebrow">{label}</span><h3>{title}</h3><p>{detail}</p></div><div className="empty-action"><div className="empty-icon"><BookOpen size={22} /></div><h4>{section}를 더 선명하게 만들까요?</h4><p>AI Consultant가 현재 Brand context를 읽고 다음 제안을 준비할 수 있어요.</p><button className="dark-button"><MessageCircle size={15} /> Consultant에게 요청</button></div></section>;
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
