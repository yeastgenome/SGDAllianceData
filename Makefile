setup:
		pip install -r requirements.txt
		npm install
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

run-expression:	
		. env.sh && python ./run_expression.py
run-phenotype:
		. env.sh && python ./run_phenotype.py
run-bgi:
#		npm run panther-json
#		. env.sh && python ./run_bgi.py 
		. env.sh && python ./run_nongene.py

run-disease:
		. env.sh && python ./run_disease_association.py

build-all:
		. env.sh && pip install -r requirements.txt
		npm run disease-json
		npm run panther-json
		python ./run_expression.py
		python ./run_phenotype.py
		python ./run_bgi.py
		python ./run_disease_association.py

#upload-all:
	# run script
