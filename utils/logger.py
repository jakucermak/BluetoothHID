import logging


class Logger:

    logging.basicConfig(filename='logger.log', filemode='w' ,format='%(asctime)s - %(message)s',
                        level=logging.info)

    @property
    def log(msg):
        logging.info(msg)
