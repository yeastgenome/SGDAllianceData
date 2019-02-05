setup:
		pip install -r requirements.txt
clean-packages:
		pip unistall -r requirements.txt

pretty-json:
		python -m json.tool ./src/data_dump/output.json
disease-json:
		npm run disease-json

build-disease:
		npm run disease-json
build-panther:
		npm run panther-json
run:
		. env.sh && python src/sgd_alliance_data.py
