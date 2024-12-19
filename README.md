# Barlamane Graph Database

This project implements a graph database to track interactions and relationships in the Moroccan Parliament using Python and Dgraph. The data has been scraped using [moroccan_parliament_scraper](https://github.com/MariemAa3/moroccan_parliament_scraper).


## Installation

1. Install the required Python packages:
   ```bash
   pip install pydgraph tqdm
   ```

2. Start Docker service:
   ```bash
   systemctl start docker
   ```

3. Launch Dgraph services:
   ```bash
   sudo docker-compose up
   ```
   Note: You can modify the ports by editing the `docker-compose.yml` file.


## Usage

1. Initialize the database with scraped data:
   ```bash
   python3 main.py
   ```

2. Access the Dgraph interface:
   - Open Ratel UI at `http://localhost:8000/` (default port)
   - Use the query examples provided in `query_examples.txt`

3. Watch the [tutorial video](https://www.youtube.com/watch?v=u73ovhDCPQQ&t=251s) for a detailed guide on using the interface.

## Query Examples

For detailed query examples, check `query_examples.txt`. Here are some basic queries:

```graphql
# Query Deputy from one mandat 

{
  deputy(func: has(name)) @cascade{
    uid
    name
    party
    work_at @filter(eq(term,"2016_2021")) {
      commission {
        uid
        name
      }
      uid
      term
    }
  }
}
```

## Data Model

The database schema includes:
- Deputies with party affiliations and commission memberships
- Ministries
- Parliamentary commissions and their members
- Laws with their current states and associated metadata, and commission
- Deputies question to Ministries and their state

More details in the [presentation](report.pdf).

## To do

- Replace some string with @lang to manage more complex queries in long texts (like laws and questions) like a search engine.

- Manage homonyms.
- 

## Related Projects

- [moroccan_parliament_scraper](https://github.com/MariemAa3/moroccan_parliament_scraper) : Data scraping tool for this project
