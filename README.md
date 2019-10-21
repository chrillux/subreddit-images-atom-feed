# Reddit Subreddit images feed SAM template and code

## About

Reddit is a popular website that has an RSS feed for their subs. The images that are shown in their feed are only thumbnails and some readers have no ability to zoom in. This project will take an arbitrary Reddit sub and generate a new atom feed with LARGE images, so it is possible to see them properly in your reader without clicking in to Reddit, which is not convenient while browsing your feed.

This project will setup a Lambda function, a S3 bucket, an AWS event for triggering the Lambda every 30 minutes and needed policies and roles. You are supposed to setup Cloudflare to front the S3 static website, which makes your feed more secure and possibly cheaper.

## Prerequisites

* AWS account
* AWS SAM
* Cloudflare account
* A domain hosted by Cloudflare

This setup will basically cost nothing to run. Cloudflare should cache the site for 30 minutes, so it goes back to the origin only every 30 minutes. All requests will be cached and users will never hit the S3 bucket.

## How to

* Deploy the application with AWS SAM.
* Setup a CNAME on Cloudflare pointing at the website FQDN (See Cloudformation outputs key "SubredditImagesFeedFunctionWebsiteURL")

## Todo

Rewrite the HTTP requests to Reddit API to run asynchronously, the performance will be huge.
