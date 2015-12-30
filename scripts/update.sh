./scripts/run.sh
s3cmd sync $PWD/img/ --preserve --skip-existing $BUCKET_URI

