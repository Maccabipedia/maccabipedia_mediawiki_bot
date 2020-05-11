import os
from urllib import parse

import requests

import pywikibot as pw

site = pw.Site()

from maccabistats.parse.maccabipedia.maccabipedia_cargo_chunks_crawler import MaccabiPediaCargoChunksCrawler
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

_API = os.environ['YOUTUBE_API_KEY']


def youtube_link(link):
    return 'youtube.' in link or 'youtu.be' in link


def youtube_video_active_and_public(link):
    logging.info(f"Checking youtube link: {link}")
    if 'youtube.' in link:
        params = parse.parse_qs(parse.urlsplit(link).query)
        youtube_id = params['v'][0]
    elif 'youtu.be' in link:
        youtube_id = parse.urlsplit(link).path[1:]
    else:
        raise Exception("Not a familiar youtube format")

    query_youtube_video_api = f'https://www.googleapis.com/youtube/v3/videos?id={youtube_id}&key={_API}&part=status'
    answer = requests.get(query_youtube_video_api)
    if answer.status_code != 200:
        raise Exception(f"Bad answer from youtube api, code: {answer.status_code}, json: {answer.json()}")

    youtube_link_details = answer.json()
    if not youtube_link_details['items'] and youtube_link_details.get('pageInfo', {}).get('resultsPerPage') == 0:  # This link is private or deleted
        return False

    if youtube_link_details['items'][0].get('status', {}):
        return True

    raise Exception("Unknown state")


def report_bad_youtube_link(missing_youtube_links_maccabipedia_page, link, page_name):
    new_text = missing_youtube_links_maccabipedia_page.text
    new_text += f"\n# בעמוד [[{page_name}]] הלינק שבור: {link}, תייגתי את: {{{{משתמשי תקצירים}}}} , בתודה ~~~~"
    missing_youtube_links_maccabipedia_page.text = new_text
    missing_youtube_links_maccabipedia_page.save(botflag=True, summary="Found new broken youtube link")


def crawl_videos():
    maccabipedia_page_to_report_at = pw.Page(site, "מעקב אחרי תקצירים שנמחקו")
    videos = MaccabiPediaCargoChunksCrawler(
        tables_name="Games_Videos, Games_Catalog",
        tables_fields="Games_Videos._pageName, Games_Videos.FullGame, Games_Videos.Highlights, Games_Videos.Highlights2",
        join_tables_on="Games_Catalog._pageName=Games_Videos._pageName")

    for index, video in enumerate(videos):
        logging.info(f"Checking ({index}) page: {video['_pageName']}")

        try:
            if youtube_link(video['FullGame']) and not youtube_video_active_and_public(video['FullGame']):
                report_bad_youtube_link(maccabipedia_page_to_report_at, video['FullGame'], video['_pageName'])
            if youtube_link(video['Highlights']) and not youtube_video_active_and_public(video['Highlights']):
                report_bad_youtube_link(maccabipedia_page_to_report_at, video['Highlights'], video['_pageName'])
            if youtube_link(video['Highlights2']) and not youtube_video_active_and_public(video['Highlights2']):
                report_bad_youtube_link(maccabipedia_page_to_report_at, video['Highlights2'], video['_pageName'])
        except Exception:
            logging.exception(f"Error on video: {video}")


if __name__ == "__main__":
    crawl_videos()
