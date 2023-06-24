#!/usr/bin/env sh

sh -c python3 /tests/functional/utils/wait_for_redis.py \
&& python3 /tests/functional/utils/wait_for_api.py \
&& pytest /tests/functional/src