import os
import json

from pipelines.pipeline import Pipeline
from stages.stage import Stage
from stages.setup import SetupStage, DIR, FILENAME, SOURCE, COMPRESSED
from tabular_cell_type_classification.deploy.predict_labels import main

FNAME = 'fname'
CE_MODEL_PATH = 'ce_model_path'
FE_MODEL_PATH = 'fe_model_path'
CL_MODEL_PATH = 'cl_model_path'
W2V_PATH = 'w2v_path'
VOCAB_SIZE = 'vocab_size'
INFERSENT_MODEL = 'infersent_model'
OUT = 'out'


class PredictLabelsStage(Stage):
    def __init__(self, params):
        super().__init__('PredictLabelsStage', params)

    def run(self):
        results = main(params[FNAME], params[CE_MODEL_PATH], params[FE_MODEL_PATH], params[CL_MODEL_PATH], params[W2V_PATH], params[VOCAB_SIZE], params[INFERSENT_MODEL])
        json.dump(results, open(params[OUT], 'w'))


class PredictLabelsPipeline(Pipeline):
    def trigger(self):
        self.logger.info(f'Trigger PredictLabelsPipeline pipeline')
        for stage in self.stages:
            self.logger.info(f'Starting {stage.name} stage')
            stage.run()
            self.logger.info(f'Completed {stage.name} stage')


if __name__ == '__main__':
    input_file = {DIR: 'tmp', FILENAME: 'input.xls', SOURCE: 'https://docs.google.com/uc?id=1_aXGxIaM-Cs-_PT9w0_GVog5dzSTr4w9', COMPRESSED: False}
    psl = {DIR: 'tmp/psl', FILENAME: 'psl.tar.gz', SOURCE: 'https://drive.google.com/uc?id=1ndVTP3WSG8OLoDjYnePvuVZ5fxXBCyRz', COMPRESSED: True}
    glove = {DIR: 'tmp/glove', FILENAME: 'glove.840B.300d.zip', SOURCE: 'http://nlp.stanford.edu/data/glove.840B.300d.zip', COMPRESSED: True}
    infersent = {DIR: 'tmp/infersent', FILENAME: 'infersent1.pkl', SOURCE: 'https://dl.fbaipublicfiles.com/infersent/infersent1.pkl', COMPRESSED: False}
    ce_model = {DIR: 'tmp/models', FILENAME: 'ce.model', SOURCE: 'https://drive.google.com/uc?id=1DJfEgqoHzfQYBllzey21zS39ui_kwId-', COMPRESSED: False}
    cl_model = {DIR: 'tmp/models', FILENAME: 'cl.model', SOURCE: 'https://drive.google.com/uc?id=1f2R-xQVAJBInf8t4gQ6Yj1OHX8_XNwB6', COMPRESSED: False}
    fe_model = {DIR: 'tmp/models', FILENAME: 'fe.model', SOURCE: 'https://drive.google.com/uc?id=1zIPd7E34VgDmbpfPKfsyYdr1eGvW7hHz', COMPRESSED: False}
    setup_stage = SetupStage([input_file, psl, glove, infersent, ce_model, cl_model, fe_model])

    params = {
        FNAME: os.path.join(input_file[DIR], input_file[FILENAME]),
        CE_MODEL_PATH: os.path.join(ce_model[DIR], ce_model[FILENAME]),
        FE_MODEL_PATH: os.path.join(fe_model[DIR], fe_model[FILENAME]),
        CL_MODEL_PATH: os.path.join(cl_model[DIR], cl_model[FILENAME]),
        W2V_PATH: os.path.join(glove[DIR], str(glove[FILENAME]).replace('.zip', '.txt')),
        VOCAB_SIZE: 60000,
        INFERSENT_MODEL: os.path.join(infersent[DIR], infersent[FILENAME]),
        OUT: 'tmp/results.json'
    }
    predict_labels_stage = PredictLabelsStage(params)

    pipeline = PredictLabelsPipeline([setup_stage, predict_labels_stage])
    pipeline.trigger()
