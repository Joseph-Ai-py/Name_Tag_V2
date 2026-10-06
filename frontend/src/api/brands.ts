import { api } from "./client";

export type BrandState = {
	business: Record<string, unknown>;
	market: Record<string, unknown>;
	customer: Record<string, unknown>;
	brand: Record<string, unknown>;
	visual: Record<string, unknown>;
};

export type BrandStateResponse = {
	id: string;
	brand_id: string;
	state: BrandState;
	version: number;
	created_at: string;
	updated_at: string;
};

export const brandStateQueryKey = (brandId: string) => ["brand", brandId, "state"] as const;

export function getBrandState(brandId: string) {
	return api<BrandStateResponse>(`/api/brands/${brandId}/state`);
}
