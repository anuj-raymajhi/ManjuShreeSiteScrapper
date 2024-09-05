# ManjuShree Web Scraper

This project is a web scraping application built with Scrapy to extract data from the ManjuShree website.

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/nbitOverflow/Cust_Scrape_manjushree
   cd Cust_Scrape_manjushree
   ```

2. (Recommended) Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install scrapy
   ```

## Usage

To run the scraper and save the data to a CSV file:

```
scrapy crawl manjuscraper -o ManjuShreeData.csv -t csv
```

This command will execute the `manjuscraper` spider and save the scraped data to `ManjuShreeData.csv` in the project directory.

## Output

After running the scraper, you'll find the `ManjuShreeData.csv` file in the project directory containing the extracted data.

## Customization

To modify the scraper's behavior or target different data, edit the spider file located in `spiders/manjuscraper.py`.


