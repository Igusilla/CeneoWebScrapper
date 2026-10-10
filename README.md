# Ceneo Web Scrapper

A Flask web application for downloading, browsing, and analyzing product reviews from [Ceneo.pl](https://www.ceneo.pl/). The user provides a product ID, and the application downloads the available reviews, stores them locally as JSON files, calculates statistics, and generates charts.

## Features

- download all available review pages for a product by its ID,
- save reviews and statistics directly in `app/data/`,
- browse reviews in a sortable and filterable table,
- view the details of an individual review,
- display product summaries including review count, average rating, pros, cons, and recommendations,
- generate recommendation and star-rating distribution charts,
- export reviews to JSON, CSV, and XLSX.

## Requirements

- Python 3.10 or newer,
- internet access when downloading reviews,
- a Ceneo.pl page structure compatible with the selectors in `app/utils.py`.

Python dependencies are listed in `requirements.txt`. The interface also uses JavaScript libraries loaded from CDNs: Bootstrap, Bootstrap Icons, jQuery, and DataTables.

## Installation and Usage

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install openpyxl
python run.py
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install openpyxl
python run.py
```

Then open `http://127.0.0.1:5000/` in a browser.

`run.py` imports the application, while `app/__init__.py` starts Flask's built-in development server in debug mode. This configuration is intended for local development, not production deployment.

## Using the Application

1. Open the **Review Extraction** page.
2. Enter a product ID from Ceneo, for example `111261978`.
3. After the download finishes, open the product's review list.
4. View review details, generate charts, or download the data in the selected format.

### Available Routes

| Route | Description |
| --- | --- |
| `/` | Home page and project description |
| `/extract` | Review extraction form; a `POST` request starts scraping |
| `/products` | List of locally stored products |
| `/product/<product_id>` | Review table for a product |
| `/charts/<product_id>` | Generate and display charts |
| `/download/<product_id>/<filetype>` | Download data as `json`, `csv`, or `xlsx` |
| `/author` | Project author information |

## Data Storage

The application does not use a relational database. Its local data store consists of JSON files:

```text
app/data/
├── opinions/
│   └── <product_id>.json   # list of individual reviews
└── products/
    └── <product_id>.json   # product statistics
```

Each review contains the following fields:

- `opinion_id` - review identifier,
- `author` - review author,
- `recommendation` - `Polecam`, `Nie polecam`, or no recommendation,
- `stars` - star rating in the format returned by Ceneo,
- `content` - review text,
- `pros` and `cons` - lists of advantages and disadvantages,
- `useful` and `unuseful` - helpful and unhelpful vote counts,
- `post_date` and `purchase_date` - review and purchase dates.

The product statistics file includes `product_id`, `product_name`, `opinions_count`, `pros_count`, `cons_count`, `pros_cons_count`, `average_stars`, and the `pros`, `cons`, and `recommendations` dictionaries.

## Included Dataset

The repository currently contains 9 saved products and 1,168 reviews:

| ID | Product |
| --- | --- |
| `111261978` | Konsola Nintendo Switch OLED White |
| `167193465` | Motorola Edge 50 Ultra 16GB/1TB Szary |
| `172806503` | Apple iPhone 16 128GB Berylowa zieleń |
| `31054121` | Thule EuroWay G2 920 |
| `39562616` | Samsung Galaxy S5 Neo SM-G903 Czarny |
| `42421902` | Router TP-Link TL-MR6400 |
| `44279953` | Brother DCP-1622WE |
| `58319264` | Zolux Neo Panas Klatka Ze Szklaną Kuwetą Czarna |
| `84514582` | Urządzenie wielofunkcyjne HP Smart Tank 515 AiO (1TJ09A) |

These figures describe the files currently included in the repository and may change after additional extractions.

## Project Structure

```text
.
├── app/
│   ├── __init__.py              # Flask application creation
│   ├── views_object.py          # active application routes
│   ├── views.py                 # older structural route implementation
│   ├── utils.py                 # HTML selectors and extraction helpers
│   ├── managers/                # scraping, statistics, and data exports
│   ├── models/                  # Opinion and Product models
│   ├── utilities/               # chart generator
│   ├── templates/               # Jinja2 templates
│   ├── static/                  # CSS and generated charts
│   └── data/                    # local JSON data
├── config.py                    # Ceneo request headers
├── requirements.txt             # Python dependencies
└── run.py                       # entry point
```

The active flow uses `views_object.py` and the `OpinionManager`, `ProductManager`, `DownloadManager`, and `ChartGenerator` classes. `views.py` contains an earlier structural implementation and is not imported by the current application initializer.

## Configuration and Limitations

- Request headers are defined in `config.py`. The file contains a saved Cookie header; before using or publishing the project, remove it or replace it with your own current configuration, and never publish session data.
- The scraper makes requests to Ceneo without a configured timeout. Network problems may therefore delay or interrupt extraction.
- HTML selectors are defined in `app/utils.py`. Changes to Ceneo's page structure may require updating them.
- XLSX export uses `openpyxl`, so the package is installed separately in the setup instructions; it is not currently listed in `requirements.txt`.
- Charts are created when `/charts/<product_id>` is opened and saved as PNG files in `app/static/images/charts/`.

## Technologies

- Python, Flask, and Jinja2,
- Requests and BeautifulSoup4 for downloading and parsing pages,
- Pandas for review and statistics processing,
- Matplotlib for chart generation,
- Bootstrap, jQuery, and DataTables for the user interface.