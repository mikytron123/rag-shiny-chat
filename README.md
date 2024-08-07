
<a name="readme-top"></a>

<h3 align="center">RAG Shiny chat</h3>

  <p align="center">
    A RAG bot for question answer with the Polars documentation
    <br />
    <br />
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project
[screen-capture_new.webm](https://github.com/user-attachments/assets/30f8fb30-f7b1-44fd-b4fe-3ebff2ba20ea)

This is a RAG application for answering questions about the [Polars](https://pola.rs/) Python library. This project uses the Weaviate vector database for storing document embeddings, Ollama for interacting with local LLMs, Litestar for the backend API, Shiny for the frontend ui. 

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Weaviate]][Weaviate-url]
* [![Langchain][Langchain-logo]][Langchain-url]
* [![Llama-index]][Llama-index-url]
* [![Ollama]][Ollama-url]
* [![Shiny]][Shiny-url]
* [![Litestar]][Litestar-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

Install Docker.
Create a `.env` file using `env.example` as an example.
LLM environment variable should be set to any ollama model.

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/mikytron123/rag-shiny-chat
   ```
2. Run Weaviate vector db
   ```sh
   docker compose up weaviate
   ```
3. Run Ollama
   ```sh
   docker compose up ollama
   ```
4. Run backend server
   ```sh
   docker compose up server
   ```
5. Run shiny ui
   ```sh
   docker compose up ui
   ```
<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Navigate to `http://localhost:8080` in your browser and start asking questions.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->

[Weaviate]: https://img.shields.io/badge/Weaviate-black?style=for-the-badge
[Weaviate-url]: https://weaviate.io
[Langchain-url]: https://www.langchain.com/
[Langchain-logo]: https://img.shields.io/badge/langchain-1C3C3C?style=for-the-badge&logo=langchain
[Llama-index]: https://img.shields.io/badge/Llamaindex-black?style=for-the-badge
[Llama-index-url]: https://www.llamaindex.ai/
[Ollama]: https://img.shields.io/badge/Ollama-black?style=for-the-badge
[Ollama-url]: https://www.ollama.com/
[Shiny]: https://img.shields.io/badge/Shiny-black?style=for-the-badge
[Shiny-url]: https://shiny.posit.co/py/
[Litestar]: https://img.shields.io/badge/Litestar-black?style=for-the-badge
[Litestar-url]: https://litestar.dev/
