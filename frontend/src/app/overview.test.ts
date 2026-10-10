import { describe, expect, it } from "vitest";
import { compactValue } from "./App";

describe("Overview data summaries", () => {
	it("renders object arrays as readable names instead of object coercion", () => {
		expect(compactValue([{ name: "MakinaRocks" }, { name: "TreeSoop" }])).toBe("MakinaRocks · TreeSoop");
		expect(compactValue([{ name: "MakinaRocks" }])).not.toContain("[object Object]");
	});

	it("uses an explicit fallback for missing optional fields", () => {
		expect(compactValue(null, "컬러 미정")).toBe("컬러 미정");
		expect(compactValue([])).toBe("미정");
	});

	it("does not invent visual colors when no tokens exist", () => {
		expect(compactValue([], "컬러 미정")).toBe("컬러 미정");
	});
});