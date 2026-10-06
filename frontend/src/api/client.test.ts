import { describe, expect, it, vi } from "vitest";
import { api } from "./client";
import { brandStateQueryKey } from "./brands";

describe("frontend API contracts", () => {
	it("uses the scoped BrandState query key", () => {
		expect(brandStateQueryKey("brand-1")).toEqual(["brand", "brand-1", "state"]);
	});

	it("preserves structured backend errors", async () => {
		vi.stubGlobal("fetch", vi.fn().mockResolvedValue(
			new Response(JSON.stringify({ detail: {
				code: "BRAND_STATE_VERSION_CONFLICT",
				expected_version: 3,
				actual_version: 4,
			} }), { status: 409 }),
		));

		await expect(api("/api/brands/brand-1/state")).rejects.toMatchObject({
			status: 409,
			detail: { code: "BRAND_STATE_VERSION_CONFLICT", actual_version: 4 },
		});
	});
});
