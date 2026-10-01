ROUTE_KEYWORDS = {
	"research": ("조사", "리서치", "시장", "경쟁사", "트렌드"),
	"customer": ("타겟", "고객", "페르소나", "사용자", "pain point"),
	"brand": ("브랜드", "포지셔닝", "스토리", "미션", "톤"),
	"business": ("사업", "문제", "솔루션", "수익", "가격"),
	"visual": ("로고", "색상", "비주얼", "디자인", "타이포"),
}


def classify_message(message: str) -> str:
	normalized = message.casefold()
	for route, keywords in ROUTE_KEYWORDS.items():
		if any(keyword.casefold() in normalized for keyword in keywords):
			return route
	return "conversation"
