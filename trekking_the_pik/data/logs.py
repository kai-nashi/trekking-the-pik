import logging


stream_handler = logging.StreamHandler()

logger = logging.Logger('flats_update')
logger.setLevel("DEBUG")
logger.addHandler(stream_handler)
