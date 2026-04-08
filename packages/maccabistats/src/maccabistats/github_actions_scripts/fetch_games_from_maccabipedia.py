import logging

from maccabistats import run_maccabipedia_source

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


if __name__ == '__main__':
    logging.info('Starting to fetch Maccabi games from MaccabiPedia')
    _ = run_maccabipedia_source()
    logging.info('Finished to fetch Maccabi games from MaccabiPedia')
