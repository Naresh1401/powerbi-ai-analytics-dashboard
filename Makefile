.PHONY: install generate-data analyze export-powerbi all clean

install:
	pip install -r requirements.txt

generate-data:
	python -m src.data.generate_all_data

analyze:
	python -m src.analysis.mlops_analysis
	python -m src.analysis.genai_ops_analysis
	python -m src.analysis.data_quality_analysis
	python -m src.analysis.business_impact_analysis
	python -m src.analysis.product_analysis
	python -m src.analysis.risk_analysis
	python -m src.analysis.manufacturing_analysis

export-powerbi:
	python -m src.export_powerbi_ready

all: install generate-data analyze export-powerbi

clean:
	rm -rf data/*.csv
	rm -rf data/analysis/
	rm -rf data/powerbi_ready/
	find . -type d -name __pycache__ -exec rm -rf {} +
