# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY train.py .


# Build the Image
# docker build -t local-train-example  .

# Use image to train in local container
#  https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-training-algo-dockerfile.html
# docker run --entrypoint <ContainerEntrypoint> image <ContainerArguments>
# docker run --entrypoint python local-train-example train.py --n_estimators 100 --random_state 42