source ~/.nvm/nvm.sh

nvm use 18

n8n export:credentials --all --decrypted --output=./ProAgent/n8n_tester/credentials/c.json

n8n export:workflow --all --output=./ProAgent/n8n_tester/credentials/w.json
