# E-Commerce Product Scraper

A Python-based web scraper that extracts product information from popular e-commerce websites like Flipkart and Amazon.

## Features

- Scrapes product information from Flipkart and Amazon
- Extracts detailed specifications for different product types (mobile phones, laptops, TVs)
- Handles rate limiting and retries
- Uses rotating user agents to avoid blocking
- Detailed logging for debugging

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ecommerce-scraper.git
cd ecommerce-scraper
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```python
from scraper import scrape_flipkart, scrape_amazon

# Search for products
flipkart_products = scrape_flipkart("iphone 13")
amazon_products = scrape_amazon("iphone 13")

# Process the results
for product in flipkart_products:
    print(f"Title: {product['title']}")
    print(f"Price: {product['price']}")
    print(f"Specifications: {product['specs']}")
    print("---")
```

## Project Structure

```
ecommerce-scraper/
├── README.md
├── requirements.txt
├── .gitignore
└── scraper.py
```

## Dependencies

- requests
- beautifulsoup4
- fake-useragent
- logging
- typing
- re
- random
- time

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This scraper is for educational purposes only. Please respect the websites' terms of service and robots.txt files. Use responsibly and at your own risk. 