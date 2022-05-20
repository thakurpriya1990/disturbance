#!/bin/bash
## sole parameter is an integer indicating incremental daily version
## git branch --set-upstream-to=origin/das_dev das_dev	

if [ $# -lt 2 ]; then
    echo "ERROR: Must specify <github branch> and <integer indicating incremental daily version> e.g."
    echo "$0 das_dev 1 <optional: --no-cache>"
    exit 1
fi

if [ $# -eq 3 ]; then
    NO_CACHE=$3
fi

GIT_BRANCH=$1
BUILD_TAG=dbcawa/disturbance:v$(date +%Y.%m.%d).$2
git checkout $GIT_BRANCH &&
git pull &&
cd disturbance/frontend/disturbance/ &&
npm run build &&
cd ../../../ &&
source venv/bin/activate &&
./manage_ds.py collectstatic --no-input &&
docker image build $NO_CACHE --tag $BUILD_TAG . &&
echo $BUILD_TAG &&
docker push $BUILD_TAG
