# Barlamane Graph Database

This project implements a graph database to track interaction and relationships in Moroccan Parliament using Python and Dgraph. Data have been scrapped using this [https://github.com/MariemAa3/moroccan_parliament_scraper](repo)

## Installation

Install the required packages by running:

pip install pydgraph tqdm

You'll also need to start Dgraph services (you need [https://docs.docker.com/get-started/get-docker/](docker) installed):

systemctl start docker
sudo docker-compose up ## You can modify the ports by modifying the docker-compose.yml file


## Usage

To write the data in the database use the main.py :

python3 main.py

To use the database you can use the ratelUI in http://localhost:8000/ by default, examples of query are provided in query_examples.txt
