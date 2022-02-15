setup:
		pip install -r requirements.txt
		npm install
clean-packages:
		pip unistall -r requirements.txt

pretty-json:
		python -m json.tool ./src/data_dump/output.json
#cat src/data_dump/SGD_1.0.1.4_phenotype.json | python -m json.tool > src/data_dump/SGD_1.0.1.4_phenotype-pretty.json

disease-json:
		npm run disease-json

build-disease:
		npm run disease-json

build-panther:
		npm run panther-json

run-expression:	
		source /data/envs/sgd3/bin/activate && . env.sh && python ./run_expression.py
run-phenotype:
		source /data/envs/sgd3/bin/activate && . env.sh && python ./run_phenotype.py
run-bgi:
#		npm run panther-json
		source /data/envs/sgd3/bin/activate && . env.sh && python ./run_bgi.py 
		source /data/envs/sgd3/bin/activate && . env.sh && python ./run_nongene.py

run-disease:
		source /data/envs/sgd3/bin/activate && . env.sh && python ./run_disease_association.py

run-htpdatasamples:
#		. env.sh && python ./run_datasets.py
		source /data/envs/sgd3/bin/activate && . env.sh && python ./run_htp_sample_metadata.py

run-htpdatasets:
		source /data/envs/sgd3/bin/activate && . env.sh && python ./run_htp_datasets.py

run-agm:
		source /data/envs/sgd3/bin/activate && . env.sh && python ./run_agm.py

run-allele:
		source /data/envs/sgd3/bin/activate && . env.sh && python ./run_alleles.py

run-refs:
		. env.sh && python ./run_references.py

run-resources:
		source /data/envs/sgd3/bin/activate && . env.sh && python ./run_resources.py

build-all:
		source /data/envs/sgd3/bin/activate && . env.sh && pip install -r requirements.txt

run-all:
		#npm run disease-json
		#npm run panther-json
		source /data/envs/sgd3/bin/activate && . env.sh && python ./run_agm.py
		source /data/envs/sgd3/bin/activate && . env.sh && python ./run_htp_datasets.py
		source /data/envs/sgd3/bin/activate && . env.sh && python ./run_disease_association.py
		source /data/envs/sgd3/bin/activate && . env.sh && python ./run_expression.py
		source /data/envs/sgd3/bin/activate && . env.sh && python ./run_phenotype.py
		source /data/envs/sgd3/bin/activate && . env.sh && python ./run_htp_sample_metadata.py
		source /data/envs/sgd3/bin/activate && . env.sh && python ./run_bgi.py
		source /data/envs/sgd3/bin/activate && . env.sh && python ./run_references.py
		source /data/envs/sgd3/bin/activate && . env.sh && python ./run_resources.py
#upload-all:
	# run script
	# uploads all files to AWS for Alliance to ferret out
