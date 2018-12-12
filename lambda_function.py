
import re
import json
from os import environ

import requests
import lxml.html


def lambda_hundler(event, context):
    # ここにGoole検索URLを設定
    target_urls = ['https://www.google.co.jp/search?q=site%3Ahttps%3A%2F%2Fwww.uniqlo.com%2Fjp%2Fnews%2Ftopics%2F&as_qdr=d2',
     'https://www.google.co.jp/search?q=site%3Ahttps%3A%2F%2Fwww.gu-japan.com%2Fapp%2Fmobilemembers%2Farticle%2F&as_qdr=d2']
    for url in target_urls:
        scrape_lists = google_search(url)
        if len(scrape_lists) > 0:
            post_slack(scrape_lists)


def post_slack(posts):
    message = ''
    for post in posts:
        message += '<{}|{}> \n\n'.format(post['url'], post['title'])
    slack_message = {
        'username': environ['SLACK_BOT_NAME'],
        'channel': environ['SLACK_CHANNEL'],
        'text': "%s" % (message)
    }
    requests.post(environ['SLACK_WEBHOOK_URL'],
                json.dumps(slack_message).encode('utf-8'))


def google_search(url):
    detail_page_urls = []
    scrape_lists = []
    list_page_root = lxml.html.fromstring(requests.get(url).content)
    for a in list_page_root.cssselect('h3 a'):
        detail_page_urls.append(re.match(r'/url\?q=(https://.*)&sa=U.*', a.get('href'))[1])
    for url in detail_page_urls:
        detail_page_root = lxml.html.fromstring(requests.get(url).content)
        item = {
            'title': detail_page_root.cssselect('title')[0].text_content(),
            'url': url
        }
        scrape_lists.append(item)
    return scrape_lists
