Tadpoles.com Scraper
==============================

WHAT
++++

Tadpoles.com is a site where daycare centers sometimes post 
pics of kids if they use the tadpoles ipad app. They don't support
bulk downloads though...until now. 

Dependencies
+++++++++++++

Docker
s3cmd

Usage
+++++

    ./scripts/build.sh
    export BUCKET_URI=s3://awesome_bucket/tadpoles/
    ./scripts/update.sh

The images get saved to ./img/ in year/month subdirectories, then 
synced to s3 with s3cmd.
