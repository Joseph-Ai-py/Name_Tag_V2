export class ApiError extends Error {
	status: number;
	detail: unknown;

	constructor(status: number, detail: unknown) {
		const code = typeof detail === "object" && detail !== null && "code" in detail ? detail.code : null;
		super(
			code === "BRAND_STATE_VERSION_CONFLICT"
				? "이 제안이 생성된 이후 브랜드 정보가 변경되었습니다. 최신 상태를 확인한 후 다시 시도해주세요."
				: typeof detail === "string" ? detail : "요청을 완료하지 못했어요.",
		);
		this.name = "ApiError";
		this.status = status;
		this.detail = detail;
	}
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
	const response = await fetch(path, {
		credentials: "include",
		headers: { "Content-Type": "application/json", ...(options.headers ?? {}) },
		...options,
	});
	if (!response.ok) {
		const payload = await response.json().catch(() => null) as { detail?: unknown } | null;
		throw new ApiError(response.status, payload?.detail ?? "요청을 완료하지 못했어요.");
	}
	return response.status === 204 ? (undefined as T) : response.json();
}
