#!/bin/bash

echo "URL             : ${URL}"
echo "DEPLOY_URL      : ${DEPLOY_URL}"
echo "DEPLOY_PRIME_URL: ${DEPLOY_PRIME_URL}"

echo "url: ${DEPLOY_PRIME_URL}" > _config_netlify.yml
bundle exec jekyll build --drafts --unpublished --future --config _config.yml,_config_netlify.yml