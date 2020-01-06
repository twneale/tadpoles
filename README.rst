Tadpoles.com Scraper
==============================

OLD BROKEN RUBBISH REPLACED
+++++++++++++++++++++++++++++

This repo has been broken for several years--my apologies to all denizens of the Interwebs who found this repo and were horribly confused.

The repo previously used dockerized Selinium browser automation, with a hideous login flow that didn't work for 90% of users. 

Over the years, many unfortunate people have emailed me in a panic a day or two before their tadpoles accounts were about to be disabled. Probably tending to an exploding diaper of my own, I was never really able to help.

I have replaced this garbage with three janky little scripts that work, but require some annoying fiddling. Some code was cribbed from other Github repos by more able minds; attribution leaves something to be desired. Just search for Tadpoles on Github and you will find their stuff. 


How to Use
++++++++++++++

* Create an SQS Queue and S3 bucket to hold your images.
* Grep this repo for 'TADPOLES_' and define the required environment variables. S3 bucket name, SQS queue url, etc. 
* Install requests and boto3. 
* Pour yourself a beverage
* This step sucks: using mitmproxy or similar, log into Tadpoles and get the Cookie header from one of your http requests once the auth flow completes.
* Set the value of the Cookie as an environment variable. Also set it to the secret named TADPOLES_COOKIE_AWS_SECRET_NAME environment variable (or pro tip: copy/paste the secret into your checkout of the script and be done with it). 
* Run the get_events.py script. It will output zillions of JSON objects to stdout. Pipe this into a file and proceed to the next step. 
* Run the extent_queue.py script. This just pumps all this JSON objects into the TADPOLES_SQS_QUEUE_URL queue in your AWS accounts (note: create that thing first). 
* Create a Lambda function and set the fetcher.py code as the body of the function. 
* Add the lambda function as a handler for your SQS queue. 
* Watch an episode of the Simpons and your photos should be sitting in S3 when the script is done. 





