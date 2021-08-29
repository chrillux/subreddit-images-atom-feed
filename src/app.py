import asyncio
import json
import os

import aiohttp
import feedparser
from feedgen.feed import FeedGenerator

import boto3


def lambda_handler(event, context):

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Feed saved to S3 bucket.",
        }),
    }


async def main():
    reddit_sub = os.environ['REDDIT_SUB']
    feed = feedparser.parse(
        "https://www.reddit.com/r/{}.rss".format(reddit_sub))

    fg = FeedGenerator()
    fg.id('https://www.reddit.com/r/{}'.format(reddit_sub))
    fg.title('{} with large images.'.format(reddit_sub))
    fg.link(href='https://www.reddit.com/r/{}'.format(reddit_sub))
    fg.description('Reddit {} with large images.'.format(reddit_sub))

    async with aiohttp.ClientSession() as session:
        coroutines = [
            fetch_entry_data(session, entry, fg) for entry in feed.entries
        ]
        completed, pending = await asyncio.wait(coroutines)

    list_of_result = []
    for complete_coroutine in completed:
        if complete_coroutine.result() is None:
            continue
        list_of_result.append(complete_coroutine.result())
    list_of_result.sort(key=lambda entry: entry['pubDate'])
    add_entries_to_feed(fg, list_of_result)

    s3 = boto3.resource("s3")
    s3.Bucket(os.environ['BUCKET_NAME']).put_object(
        Key='index.html',
        CacheControl='max-age=1800',
        ContentType="application/atom+xml",
        Body=fg.atom_str(pretty=True))


def add_entries_to_feed(fg, list_of_result):

    for result in list_of_result:
        fe = fg.add_entry()

        fe.id(result['id'])
        fe.link(href=result['id'])
        fe.pubDate(result['pubDate'])
        fe.title(result['title'])
        fe.author({'name': result['author']})
        fe.description(result['description'])


async def fetch_entry_data(session, entry, fg):
    article_title = entry.title
    article_link = entry.link
    json_link = '{}/.json'.format(article_link)
    async with session.get(json_link, headers={'User-agent':
                                               'Mozilla/5.0'}) as response:
        json_data = await response.json()
    post_data = json_data[0]['data']['children'][0]['data']
    if not post_data.get('post_hint') == 'image':
        return

    image_fullsize_url = post_data['url']
    imgsrc = '<img src="{}">'.format(image_fullsize_url)
    author = post_data['author']
    description = "{} <br/> {}".format(imgsrc, author)
    article_published_at = entry.updated

    entry_data = {
        'id': article_link,
        'pubDate': article_published_at,
        'title': article_title,
        'author': author,
        'description': description,
    }

    return entry_data
