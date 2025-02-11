#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Component Search API...${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install or upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
python -m pip install --upgrade pip

# Install requirements
echo -e "${YELLOW}Installing requirements...${NC}"
pip install -r requirements.txt

# Check if models are downloaded
echo -e "${YELLOW}Checking for model files...${NC}"
if [ ! -d "models" ]; then
    mkdir -p models
    echo -e "${YELLOW}Downloading models (this may take a while)...${NC}"
    # Pre-download models to avoid first-request delay
    python -c "
from transformers import AutoTokenizer, AutoModel
print('Downloading CodeBERT...')
AutoTokenizer.from_pretrained('microsoft/codebert-base', cache_dir='./models')
AutoModel.from_pretrained('microsoft/codebert-base', cache_dir='./models')
print('Downloading BERT...')
AutoTokenizer.from_pretrained('bert-base-uncased', cache_dir='./models')
AutoModel.from_pretrained('bert-base-uncased', cache_dir='./models')
"
fi

# Run the FastAPI application
echo -e "${GREEN}Starting API server...${NC}"
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Trap SIGINT to properly deactivate virtual environment
trap 'echo -e "${YELLOW}\nShutting down...${NC}" && deactivate' SIGINT 