#!/usr/bin/env bash
set -euo pipefail

# Deploy the current repository through Heroku's container registry.
: "${HEROKU_APP_NAME:?Set HEROKU_APP_NAME before running this script.}"
: "${HEROKU_API_KEY:?Set HEROKU_API_KEY before running this script.}"

echo "$HEROKU_API_KEY" | docker login --username=_ --password-stdin registry.heroku.com
docker build --platform linux/amd64 -f docker/Dockerfile \
  -t "registry.heroku.com/${HEROKU_APP_NAME}/web" .
docker push "registry.heroku.com/${HEROKU_APP_NAME}/web"
heroku container:release web --app "$HEROKU_APP_NAME"
heroku open --app "$HEROKU_APP_NAME"
