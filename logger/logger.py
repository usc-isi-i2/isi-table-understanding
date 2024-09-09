import logging.config
import logging
import yaml
import os


class MyLogger:
    logger = None

    @staticmethod
    def get_logger(logger_name="test"):
        if MyLogger.logger is None:
            cur_dir = os.path.dirname(os.path.realpath(__file__))
            config_path = os.path.join(cur_dir, "../", "cfg/logging.yaml")
            with open(config_path, 'rt') as f:
                config = yaml.safe_load(f.read())
                f.close()

            logging.config.dictConfig(config)
            MyLogger.logger = logging.getLogger(logger_name)

        return MyLogger.logger
