# Company Researcher

**Candidate:** Surya Bhosale

**Date of submission:** 11 June 2025

---

## 📊 LangGraph-Based Company Researcher

This project is a modular company research agent built using **LangGraph** and the modern **LangChain** ecosystem. It orchestrates structured AI workflows for tasks like data extraction, transformation, and synthesis using a declarative, graph-based runtime.



### ⚙️ Key Technology Stack

* **LangGraph + LangChain**: For stateful, graph-driven AI pipelines and LLM orchestration
* **OpenAI + Tiktoken**: Efficient LLM integration with token-aware processing
* **Pydantic v2 + Annotated-types**: Strongly typed state and config validation
* **BeautifulSoup + regex + soupsieve**: Robust HTML parsing and content filtering
* **Pandas + NumPy**: Structured data manipulation and tabular inference

### 🧾 Attribution
No external repositories were directly used—this is original work. However, the LangGraph Deep Research blog series served as a conceptual and technical reference, particularly in shaping the state modeling and multi-node orchestration strategies.

Additionally, AI tools were used to support development efficiency:
 - Cursor (with Claude): Assisted in scaffolding the initial structure and refining key logic flows
 - GPT-mini: Used for auto-generating docstrings and improving inline documentation


### ✍️ Author’s Note

Due to current professional obligations, I was only able to dedicate around **3.5 hours** to this project. However, I would love to expand and refine it further when time permits. Planned improvements include:

* A lightweight backend (API interface to call the agent or upload a link)
* A simple frontend interface to visualize or interact with results
* A custom **MCP server** for modular tool management
* Much more refined prompting strategies and graph orchestration logic
* Leverage async processing


---

## Steps to Run the Project

Follow the steps below to get the project up and running on your local machine or server:

### 1. Clone the Repository

First, clone the repository to your desired server or local machine using one of the following methods.

**Using SSH:**
```bash
git@github.com:suryajirajebhosale/thinkbridge-tha.git
```

**Using HTTPS:**
```bash
https://github.com/suryajirajebhosale/thinkbridge-tha.git
```

### 2. Install Docker

Ensure Docker is installed on your system. If you do not have Docker installed, you can download and install Docker Desktop by following the link below:

- [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)

### 3. Set Up Environment Variables

To run the project locally, you need to create a `.env` file in the **root directory** of the repository. This file should contain the required environment variables for the application.

- Create a file named `.env` in the root directory.
- Add the necessary environment variables inside the `.env` file. You can find the list of required variables in the project documentation or by contacting the repository admin.
- **NOTE**: I have shared the variables and credentials via email

Example `.env` format:
```bash
# .env

OPENAI_API_KEY = "KEY"
SERP_API_KEY = "KEY"
MODEL_NAME = "gpt-4o"
```


### 3. Current Data
The **companies.csv** holds the following data:

| URL                                 | Industry                     |
|-------------------------------------|------------------------------|
| https://dreeshomes.com/            | Construction                 |
| https://www.good2grow.com/         | Retail                       |
| https://silkroadmed.com/           | Manufacturing & Production   |
| https://nationalcareadvisors.com/  | Healthcare                   |
| https://www.drinktractor.com/      | Manufacturing & Production   |
| https://www.darkhorse.cpa/         | Financial Services & Insurance |



### 4. Run the research agent:

Once the repository is cloned and environment variables are set, you can run simply run the core researcher as follows

BASE: Defaults to only the company on the first row of the companies.csv
```bash
docker-compose -f docker-compose-dev.yml up --build
```

USER DRIVEN COUNT: Apply any number from 1 - 6 to company counts to get a list of company research reports 
```bash
COMPANY_COUNT=2 docker compose -f docker-compose.yaml up --build
```