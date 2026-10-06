class BrandStateVersionConflictError(Exception):
	def __init__(self, brand_id: str, expected_version: int, actual_version: int) -> None:
		self.brand_id = brand_id
		self.expected_version = expected_version
		self.actual_version = actual_version
		super().__init__(
			"Brand state has changed since this proposal was created."
		)
