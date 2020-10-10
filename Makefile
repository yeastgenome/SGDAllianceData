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
		. env.sh && python ./run_bgi.py 
		. env.sh && python ./run_nongene.py

run-disease:
		. env.sh && python ./run_disease_association.py

run-htpdatasamples:
#		. env.sh && python ./run_datasets.py
		. env.sh && python ./run_htp_sample_metadata.py

run-htpdatasets:
		. env.sh && python ./run_htp_datasets.py

run-agm:
		. env.sh && python ./run_agm.py

run-allele:
		. env.sh && python ./run_alleles.py

build-all:
		. env.sh && pip install -r requirements.txt

run-all:
		#npm run disease-json
		#npm run panther-json
		. env.sh && python ./run_agm.py
		. env.sh && python ./run_htp_datasets.py
		. env.sh && python ./run_disease_association.py
		. env.sh && python ./run_expression.py
		. env.sh && python ./run_phenotype.py
		. env.sh && python ./run_htp_sample_metadata.py
		. env.sh && python ./run_bgi.py
#upload-all:
	# run script
	# uploads all files to AWS for Alliance to ferret out