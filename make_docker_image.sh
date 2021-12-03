#!/bin/bash
cd disturbance/frontend/disturbance/ &&
npm run build &&
cd ../../../ &&
source venv/bin/activate &&
./manage_ds.py collectstatic --no-input &&
#git log --pretty=medium -30 > ./das_git_history &&
docker image build --no-cache --tag $1 .
