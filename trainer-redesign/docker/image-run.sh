## https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-training-algo-dockerfile.html#your-algorithms-training-algo-dockerfile-api-pass-ep


echo "Docker Image Option 1 - DOES NOT WORK - Cannot use enviornment variables in arguments"
docker run --entrypoint python -e SM_CHANNEL_CODE=/opt/ml/input/data/code -v $(pwd):/opt/ml/input/data/code python:3.10.14-slim \$SM_CHANNEL_CODE/main.py 

echo "Docker Image Option 2 - DOES WORK - Can use enviornment variables in arguments"
docker run --entrypoint /bin/sh -e SM_CHANNEL_CODE=/opt/ml/input/data/code -v $(pwd):/opt/ml/input/data/code python:3.10.14-slim -c "python \$SM_CHANNEL_CODE/main.py"
