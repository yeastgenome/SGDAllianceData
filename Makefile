setup:
		pip install -r requirements.txt
		npm install
clean-packages:
		pip uninstall --yes -r requirements.txt
		rm -rf node_modules/

pretty-json:
		python -m json.tool ./src/data_dump/output.json

build-disease:
		npm run disease-json
build-panther:
		npm run panther-json

run-expression:
		. env.sh && python ./run_expression.py
run-phenotype:
		. env.sh && python ./run_phenotype.py
run-disease:
		. env.sh && python ./run_disease_association.py
run-bgi:
		npm run panther-json
		. env.sh && python ./run_bgi.py 

build: clean-packages setup build-disease build-panther run-expression run-phenotype run-disease run_bgi
