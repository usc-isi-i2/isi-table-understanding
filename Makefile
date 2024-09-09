NAME=table-understanding
SHELL=/bin/sh
PYTHON_VERSION=3.8

CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

.PHONY:
setup-conda-env:
	@[ "${ENVIRONMENT}" ] || ( echo ">> Error: ENVIRONMENT is not set"; exit 1 )
	@conda env create --file ./envs/$(ENVIRONMENT).yml python=$(PYTHON_VERSION);

.PHONY:
destroy-conda-env:
	@conda remove --name $(NAME)-venv --all -y

.PHONY:
run:
	@[ "${PIPELINE}" ] || ( echo ">> Error: PIPELINE is not set"; exit 1 )
	@$(CONDA_ACTIVATE) $(NAME)-venv && PYTHONPATH=./ python ./pipelines/$(PIPELINE).py

.PHONY:
clean:
	@rm -rf ./tmp

.PHONY:
upload:
	@[ "${USER}" ] || ( echo ">> Error: USER is not set"; exit 1 )
	@[ "${HOST}" ] || ( echo ">> Error: HOST is not set"; exit 1 )
	@[ "${DIR}" ] || ( echo ">> Error: Destination DIR is not set"; exit 1 )
	scp -r . ${USER}@${HOST}:${DIR}
