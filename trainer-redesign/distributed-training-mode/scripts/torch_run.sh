#!/bin/bash

MODEL_ID=$1
ACCESS_TOKEN=$2

# Start with right hostname - https://github.com/aws/sagemaker-pytorch-training-toolkit/blob/master/lib/start_with_right_hostname.sh
#/usr/local/bin/start_with_right_hostname.sh "train"

# Install requirements
echo "Installing requirements"
pip install -r $SM_CHANNEL_CODE/requirements.txt

# Print resourceconfig.json
echo "Resourceconfig:"
cat /opt/ml/input/config/resourceconfig.json

# Print hyperparameters.json
echo "Hyperparameters:"
cat /opt/ml/input/config/hyperparameters.json

# Print inputdataconfig.json
echo "Inputdataconfig:"
cat /opt/ml/input/config/inputdataconfig.json

# Print envionment variables
echo "Environment:"
env

# Get current hostf from /opt/ml/input/config/resourceconfig.json
# Can we set this as ENV_VARIABLE on platform side? like $SM_CURRENT_HOST
current_host=$(jq -r '.current_host' /opt/ml/input/config/resourceconfig.json)

host_list=$(jq -r '.hosts' /opt/ml/input/config/resourceconfig.json)

# determine node rank
# Can we set this as ENV_VARIABLE on platform side? like $SM_NODE_RANK
if [ $current_host == "algo-1" ]; then
    export SM_NODE_RANK=0 
else
    export SM_NODE_RANK=1
fi

echo "Running torchrun on host: $current_host, rank: $SM_NODE_RANK"

# Run distributed training
# Can we set some of this as ENV_VARIABLE on platform side? like $SM_GPU_COUNT, $SM_MASTER_ADDR
export SM_GPU_COUNT=8
export SM_MASTER_ADDR=algo-1

# This only works when --node_rank is set appropriately
CMD="torchrun --nnodes 2 \
            --nproc_per_node $SM_GPU_COUNT \
            --master_addr $SM_MASTER_ADDR \
            --master_port 7777 \
            --node_rank $SM_NODE_RANK \
            $SM_CHANNEL_CODE/run_clm_no_trainer.py \
            --bf16 True \
            --dataset_path $SM_CHANNEL_DATASET \
            --epochs 1 \
            --max_steps 100 \
            --fsdp \"full_shard auto_wrap\" \
            --fsdp_transformer_layer_cls_to_wrap LlamaDecoderLayer \
            --gradient_checkpointing True \
            --optimizer adamw_torch \
            --per_device_train_batch_size 1 \
            --model_id $MODEL_ID \
            --access_token $ACCESS_TOKEN"

echo "Running command: $CMD"

eval $CMD