## Scraper

Scrape datasets from various sources

## Dependencies

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Spotipy.
numpy, pandas, sklearn are other packages that are used in the final-project.py

```bash
pip install spotipy --upgrade
```

## Usage

```bash
# Return the complete scraped datasets
python3 scraper.py

# This will scrape the data but return only 5 entries of each dataset
python3 scraper.py --scrape

# This will return the static dataset scraped from the web and stored in database or CSV file
python3 scraper.py --static datasets/billboard_hot_100.csv
```