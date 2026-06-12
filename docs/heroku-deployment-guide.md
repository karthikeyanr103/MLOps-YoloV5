# Heroku Deployment Guide

The project supports Heroku's Container Registry for a Cedar-generation app.
Heroku documents this container workflow as an advanced deployment option; it
is useful here because the Docker image is also the artifact stored in ECR.

## Prerequisites

- Docker and the Heroku CLI
- A Heroku account with an app plan
- An `x86_64`/`linux/amd64` image
- `HEROKU_APP_NAME` and an API key stored outside Git

## Create the App

```bash
heroku login
heroku create YOUR_APP_NAME --stack container
heroku stack:set container --app YOUR_APP_NAME
```

## Manual Container Release

```bash
export HEROKU_APP_NAME=YOUR_APP_NAME
export HEROKU_API_KEY="$(heroku auth:token)"
bash scripts/deploy_to_heroku.sh
```

The web process must listen on the dynamic `$PORT`. Both Dockerfiles in this
repository use that value.

## Release from CodeBuild

Set `ENABLE_HEROKU_DEPLOY=true`, provide `HEROKU_APP_NAME`, and inject
`HEROKU_API_KEY` from a secret store. The build tags the already-created image
as `registry.heroku.com/<app>/web`, pushes it, and releases the `web` process.

CodeBuild should run on an x86_64 environment. If the builder can produce more
than one architecture, add `--platform linux/amd64` to the Docker build.

## Verify

```bash
heroku open --app YOUR_APP_NAME
heroku logs --tail --app YOUR_APP_NAME
curl "https://YOUR_APP_NAME.herokuapp.com/health"
```

The Heroku filesystem is ephemeral. Package model files into the image or
download them during startup from secure object storage; do not rely on files
written by a previous dyno.

Official reference:
[Heroku Container Registry and Runtime](https://devcenter.heroku.com/articles/container-registry-and-runtime).
