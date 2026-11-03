"""Performance comparisons used by benchmark reports and charts."""


def improvement_percentage(baseline, solver_score):
	if baseline <= 0:
		raise ValueError("Baseline score must be greater than zero")

	return ((baseline - solver_score) / baseline) * 100
