
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

This is a web application for answering questions about the [Polars](https://pola.rs/) Python library. 

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* Qdrant
* Langchain
* Llama-index
* Ollama
* Shiny
* Litestar

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

Install Docker

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/mikytron123/rag-shiny-chat
   ```
2. Run QDrant vector db
   ```sh
   docker compose up qdrant
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

