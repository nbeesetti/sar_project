# Search and Rescue (SAR) Agent Framework - CSC 581

## Insights

I learned that the asset manager V1 implementation was good at performing the proposed CRUD operations with assets but could use improvement with the design choices of the implementation and with syntax or logic choices of the code. I realized that before I narrowed down on the functionality of the asset manager and knowledge base implementation, I should have taken a step back and assessed my design choices were the best given the time. For example, I forgot to remove the points that weren't implemented in the system message and also to narrow down the tuple containing None and False to avoid redundancy, neither didn't adversely affect anything. I also realized that using uuid looks simple to implement in terms of code but makes it IDs too complicated for the user, so I should've taken a step back and justified to myself when and why I would be using UUIDs. A few suggestions had an issue with the uniqueness of asset id and asset name, which is understandable since making elements unique adds complexity for the user but I wanted to keep it this way for V1 as it makes sense for an Asset to have an associate ID for querying and a name for the user to lookup and use. Another useful insight was that I should have considered using a database for my knowledge base as it would resolve many of my consistency-related design choice issues, but given the context of this project and the amount of work I put in, I wanted to stick with using a simple dictionary based knowledge base. 

## Modifications

I fixed the system message to only include the points that I actually implemented since I forgot to clean it up before. I also removed the UUIDs to not overcomplicate the values and instead opt for having the user input their preferred ID and Name (also an area for improvement for V2). I removed the default arguments for the ID and Name of an Asset so that the user is required to enter these values. I changed the .allocated parameter of the Asset class (and its uses) to be a simple None or string value instead of redundant tuple. I also modifed all of my return statements which return a tuple containing the success boolean and the associated message to be an Exception for cases where success if False. Essentially, replacing the error paths to be Exceptions with messages and then changing the function calls to be inside try except blocks to make it idiomatically clear that the function was not successful. 
 

## Introduction

This framework is for CSC 581 students to develop intelligent agents supporting the AI4S&R project. Students can create specialized agents for various SAR roles such as those listed in this spreadsheet:

https://docs.google.com/spreadsheets/d/1QZK5HAdDC-_XNui6S0JZTbJH5_PbYJTp8_gyhXmz8Ek/edit?usp=sharing
https://docs.google.com/spreadsheets/d/11rBV9CbKNeQbWbaks8TF6GO7WcSUDS_-hAoH75UEkgQ/edit?usp=sharing

Each student or team will choose a specific role within the SAR ecosystem and implement an agent that provides decision support and automation for that role.

## How to Submit
Please submit a link to your clone of the repository to Canvas. 


## V1.2 Documentation for AssetManager Agent
Latest version: V1.2 (last updated: 03/10/25)

Author: Neeraja Beesetti

The asset manager agent is responsible for maintaining an inventory of all assets, supporting CRUD (Create, Read, Update, Delete) operations on assets, and allowing teams to allocate and return a certain quantity of assets. 

Examples on how to use this agent can be inferred from the documentation below as well as the pytests under /tests/test_asset_agent.py

### Creating and Initializing the Asset Manager
```python
agent = AssetManagerAgent(populate=True) # default is populate False
```
Automatically initializes its AssetKnowledgeBase.
"populate" is an optional field, setting it as True will populate its AssetKnowledgeBase with some test data

### Requests
Making requests = asset_agent.process_request({...})

All responses contain a boolean field "success" indicating whether the request was carried out successfully.
If success is False, there will be an additional field "error" with an appropriate error message. 

```bash
All responses are python dictionaries, not JSON. See examples below.
```

Supported message requests:
```python
# 1. find_asset_id --- Users can find the asset_id if they provide the asset name (V1.2 assumes 1 to 1 relation)
agent.process_request({"message_type": "find_asset_id", "name": "Drone"}) 
# example output = {"success": True, "asset_id": "A001"}

-----------
# 2. get_all_assets --- Users can list out all assets in KB (in readable format)
agent.process_request({"message_type": "get_all_assets"})
# example output = {'all_assets': dict_items([('A001', Asset Drone (A001) of {'Aerial', 'UAV', 'Camera'} at SAR Base ((0, 0)) with 5 total units, 5 available, allocation status: (False, None)), ('A002', Asset Helicopter (A002) of {'Aerial', 'Vehicle'} at SAR Base ((0, 0)) with 1 total units, 1 available, allocation status: (False, None))])}

-----------
# !!! Important Note: Asset ID and Name must be uniquely entered by user (in V1.2)
# 3. add_asset --- Users can add new assets. id, name, and types are required params, rest are optional
agent.process_request({"message_type": "add_asset", "asset": {"id": "G001", "name": "Flashlight", "types": {"Tool", "Light", "Ground"}, "quantity": 2, "location_name": "SAR Base"} })
# example output = {'success': True, 'asset_added': "{'id': 'G001', 'name': 'Flashlight', 'types': {'Ground', 'Light', 'Tool'}, 'quantity': 2, 'location_name': 'SAR Base'}"}

-----------
# 4. update_asset --- Users can update the location, quantity, and types of existing assets
agent.process_request({"message_type": "update_asset", "update_field": "location", "name": "Drone", "location": "Donner Pass"})
# example output = {'success': True, 'asset_updated': "Asset Drone (A001) of {'Surveillance', 'UAV', 'Camera', 'Aerial'} at Donner Pass ((0, 0)) with 6 total units, 5 available, allocation status: (False, None)"}

-----------
# 5. remove_asset --- Users can remove assets entirely
agent.process_request({"message_type": "remove_asset", "id": "G002"})
# example output = {"success": True, "asset_removed": "G002"}

-----------
# 6. allocate --- Users can allocate certain quantities of an asset to a certain team
# V1.2 assumes an asset can only be allocated to one team
agent.process_request({"message_type": "allocate", "asset_id": "G003", "team_id": "GroundTroop1", "quantity": 2})
# example output = {'success': True, 'message': 'Asset G003 allocated to team GroundTroop1, 4 units remaining'}

-----------
# 7. return --- Users place a request that a certain quantity of an asset has been returned by a certain team
# In V1.2, returning more than the original quantity updates the original quantity value
agent.process_request({"message_type": "return", "asset_id": "G003", "team_id": "GroundTroop1", "quantity": 1})
# example output = {'success': True, 'message': 'Returned 1 units, 1 units still in use'}

-----------
# If the request is not successful, response output will look something like this:
# example output = {'success': False, 'error': 'actual error message will be written here'}
```


## Prerequisites

- Python 3.8 or higher
- pyenv (recommended for Python version management)
- pip (for dependency management)

## Setup and Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd sar-project
```

2. Set up Python environment:
```bash
# Using pyenv (recommended)
pyenv install 3.9.6  # or your preferred version
pyenv local 3.9.6

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -e .
```

4. Configure environment variables:

#### OpenAI:
- Obtain required API keys:
  1. OpenAI API key: Sign up at https://platform.openai.com/signup
- Update your `.env` file with the following:
    ```
    OPENAI_API_KEY=your_openai_api_key_here
    ```
#### Google Gemini:
- Obtain required API keys:
  1. ``` pip install google-generativeai ```
  2. ``` import google.generativeai as genai ```
  3. Google Gemini API Key: Obtain at https://aistudio.google.com/apikey
- Configure with the following:
  ```
  genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
  ```

Make sure to keep your `.env` file private and never commit it to version control.

## Project Structure

```
sar-project/
├── src/
│   └── sar_project/         # Main package directory
│       └── agents/          # Agent implementations
│       └── config/          # Configuration and settings
│       └── knowledge/       # Knowledge base implementations
├── tests/                   # Test directory
├── pyproject.toml           # Project metadata and build configuration
├── requirements.txt         # Project dependencies
└── .env                     # Environment configuration
```

## Development

This project follows modern Python development practices:

1. Source code is organized in the `src/sar_project` layout
2. Use `pip install -e .` for development installation
3. Run tests with `pytest tests/`
4. Follow the existing code style and structure
5. Make sure to update requirements.txt when adding dependencies


## FAQ

### Assignment Questions

**Q: How do I choose a role for my agent?**

**A:** Review the list of SAR roles above and consider which aspects interest you most. Your agent should provide clear value to SAR operations through automation, decision support, or information processing.

**Q: What capabilities should my agent have?**

**A:** Your agent should handle tasks relevant to its role such as: data processing, decision making, communication with other agents, and providing actionable information to human operators.

**Q: Can I add new dependencies?**

**A:** Yes, you can add new Python packages to requirements.txt as needed for your implementation.


### Technical Questions

**Q: Why am I getting API key errors?**

**A:** Ensure you've properly set up your .env file and obtained valid API keys from the services listed above.

**Q: How do I test my agent?**

**A:** Use the provided test framework in the tests/ directory. Write tests that verify your agent's core functionality.

**Q: Can I use external libraries for my agent?**

**A:** Yes, you can use external libraries as long as they are compatible.
