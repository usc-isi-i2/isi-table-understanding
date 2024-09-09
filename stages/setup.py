import os.path
import gdown

from stages.stage import Stage

DIR = 'dir'
SOURCE = 'source'
FILENAME = 'filename'
COMPRESSED = 'compressed'


class SetupStage(Stage):
    """Stage for setting up data and models required for further stages in the pipeline

    Attributes:
        params: List of files to be downloaded from google drive. Example: params = [{dir: 'temp', filename:'ce.model', source: 'google.drive.url'}]
    """

    def __init__(self, params):
        super().__init__('Setup', params)

    def run(self):
        """Run setup stage."""

        for param in self.params:
            dirname = param[DIR]
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            path = os.path.join(dirname, param[FILENAME])
            if not os.path.exists(path):
                gdown.download(param[SOURCE], path, False)
                if param[COMPRESSED]:
                    gdown.extractall(path)
