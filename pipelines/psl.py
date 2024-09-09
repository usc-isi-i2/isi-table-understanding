import yaml

from main import v1
from pipelines.pipeline import Pipeline
from stages.setup import SetupStage, DIR, FILENAME, SOURCE, COMPRESSED
from stages.stage import Stage

CONFIG_FILE = 'config_file'
OUTPUT_DIR = 'output_dir'
FILENAMES = 'filenames'


class PSLStage(Stage):
    def __init__(self, params):
        super().__init__('PSL', params)

    def run(self):
        file_list = yaml.load(open(params[FILENAMES]))

        for filename in file_list:
            v1(filename, params[CONFIG_FILE], params[OUTPUT_DIR])


class PSLPipeline(Pipeline):
    def trigger(self):
        self.logger.info(f'Trigger PSL pipeline')
        for stage in self.stages:
            self.logger.info(f'Starting {stage.name} stage')
            stage.run()
            self.logger.info(f'Completed {stage.name} stage')


if __name__ == '__main__':
    psl = {DIR: 'tmp/psl', FILENAME: 'psl.tar.gz', SOURCE: 'https://drive.google.com/uc?id=1ndVTP3WSG8OLoDjYnePvuVZ5fxXBCyRz', COMPRESSED: True}
    glove = {DIR: 'tmp/glove', FILENAME: 'glove.840B.300d.zip', SOURCE: 'http://nlp.stanford.edu/data/glove.840B.300d.zip', COMPRESSED: True}
    infersent = {DIR: 'tmp/infersent', FILENAME: 'infersent1.pkl', SOURCE: 'https://dl.fbaipublicfiles.com/infersent/infersent1.pkl', COMPRESSED: False}
    ce_model = {DIR: 'tmp/models', FILENAME: 'ce.model', SOURCE: 'https://drive.google.com/uc?id=1DJfEgqoHzfQYBllzey21zS39ui_kwId-', COMPRESSED: False}
    cl_model = {DIR: 'tmp/models', FILENAME: 'cl.model', SOURCE: 'https://drive.google.com/uc?id=1f2R-xQVAJBInf8t4gQ6Yj1OHX8_XNwB6', COMPRESSED: False}
    fe_model = {DIR: 'tmp/models', FILENAME: 'fe.model', SOURCE: 'https://drive.google.com/uc?id=1zIPd7E34VgDmbpfPKfsyYdr1eGvW7hHz', COMPRESSED: False}
    output_dir = {DIR: 'tmp/output', FILENAME: '', SOURCE: '', COMPRESSED: False}
    setup_stage = SetupStage([psl, glove, infersent, ce_model, cl_model, fe_model, output_dir])

    params = {
        FILENAMES: './cfg/files.yaml',
        CONFIG_FILE: './cfg/psl_sample.yaml',
        OUTPUT_DIR: './tmp/output'
    }
    psl_stage = PSLStage(params)

    pipeline = PSLPipeline([setup_stage, psl_stage])
    pipeline.trigger()
