import { useQuery } from "@tanstack/react-query";
import { brandStateQueryKey, getBrandState } from "../api/brands";

export function useBrandState(brandId: string | null) {
	return useQuery({
		queryKey: brandId ? brandStateQueryKey(brandId) : ["brand", "anonymous", "state"],
		queryFn: () => getBrandState(brandId as string),
		enabled: Boolean(brandId),
		staleTime: 15_000,
	});
}