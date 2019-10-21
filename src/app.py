import json
import os

import requests

import boto3
import feedparser
from feedgen.feed import FeedGenerator


def lambda_handler(event, context):

    feed = feedparser.parse("https://www.reddit.com/r/ProgrammerHumor.rss")

    fg = FeedGenerator()
    fg.id('https://www.reddit.com/r/ProgrammerHumor')
    fg.title('ProgrammerHumor with large images.')
    fg.link(href='https://www.reddit.com/r/ProgrammerHumor')
    fg.description('Reddit Progr>ammerHumor with large images.')

    headers = {'User-agent': 'Mozilla/5.0'}

    for entry in feed.entries:
        article_title = entry.title
        article_link = entry.link
        json_link = '{}/.json'.format(article_link)
        json_data = requests.get(json_link, headers=headers).json()
        post_data = json_data[0]['data']['children'][0]['data']
        if not post_data['post_hint'] == 'image':
            continue

        image_fullsize_url = post_data['url']
        imgsrc = '<img src="{}">'.format(image_fullsize_url)
        author = post_data['author']
        article_published_at = entry.updated

        fe = fg.add_entry()

        fe.id(article_link)
        fe.link(href=article_link)
        fe.pubDate(article_published_at)
        fe.title(article_title)
        fe.author({'name': author})
        description = "{} <br/> {}".format(imgsrc, author)
        fe.description(description)

    s3 = boto3.resource("s3")
    s3.Bucket(os.environ['BUCKET_NAME']).put_object(
        Key='index.html', Body=fg.atom_str(pretty=True))

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Feed saved to S3 bucket.",
        }),
    }
