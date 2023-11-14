source ~/.nvm/nvm.sh

nvm use 18

# set your env variable
source ./scripts/env_var.sh

echo $OPENAI_API_KEY
echo $OPENAI_API_BASE

export HYDRA_FULL_ERROR=1

python main.py