import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import logging
from typing import List, Dict, Optional
import re
import random

# Set up logging with more detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_headers() -> Dict[str, str]:
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
    }
    logger.info(f"Using User-Agent: {headers['User-Agent']}")
    return headers

def extract_specs(soup: BeautifulSoup, source: str, product_type: str) -> Dict[str, str]:
    specs = {}
    try:
        if source == 'flipkart':
            # Common specs for all products
            specs_elem = (
                soup.select_one('div._1AtVbE div._3Djpdu') or
                soup.select_one('div._1AtVbE div._3khuHA') or
                soup.select_one('div._1AtVbE div._3Djpdu')
            )
            if specs_elem:
                specs_text = specs_elem.text.strip()
                specs['general'] = specs_text

            # Product-specific specs
            if product_type == 'mobile':
                # Mobile specific specs
                specs.update({
                    'camera': extract_flipkart_mobile_spec(soup, 'Camera'),
                    'battery': extract_flipkart_mobile_spec(soup, 'Battery'),
                    'processor': extract_flipkart_mobile_spec(soup, 'Processor'),
                    'display': extract_flipkart_mobile_spec(soup, 'Display'),
                    'storage': extract_flipkart_mobile_spec(soup, 'Storage'),
                    'ram': extract_flipkart_mobile_spec(soup, 'RAM'),
                    'weight': extract_flipkart_mobile_spec(soup, 'Weight'),
                    'dimensions': extract_flipkart_mobile_spec(soup, 'Dimensions')
                })
            elif product_type == 'laptop':
                # Laptop specific specs
                specs.update({
                    'processor': extract_flipkart_laptop_spec(soup, 'Processor'),
                    'ram': extract_flipkart_laptop_spec(soup, 'RAM'),
                    'storage': extract_flipkart_laptop_spec(soup, 'Storage'),
                    'display': extract_flipkart_laptop_spec(soup, 'Display'),
                    'graphics': extract_flipkart_laptop_spec(soup, 'Graphics'),
                    'battery': extract_flipkart_laptop_spec(soup, 'Battery'),
                    'weight': extract_flipkart_laptop_spec(soup, 'Weight'),
                    'dimensions': extract_flipkart_laptop_spec(soup, 'Dimensions')
                })
            elif product_type == 'tv':
                # TV specific specs
                specs.update({
                    'screen_size': extract_flipkart_tv_spec(soup, 'Screen Size'),
                    'resolution': extract_flipkart_tv_spec(soup, 'Resolution'),
                    'display_type': extract_flipkart_tv_spec(soup, 'Display Type'),
                    'smart_tv': extract_flipkart_tv_spec(soup, 'Smart TV'),
                    'hdmi_ports': extract_flipkart_tv_spec(soup, 'HDMI Ports'),
                    'usb_ports': extract_flipkart_tv_spec(soup, 'USB Ports'),
                    'weight': extract_flipkart_tv_spec(soup, 'Weight'),
                    'dimensions': extract_flipkart_tv_spec(soup, 'Dimensions')
                })

        elif source == 'amazon':
            # Common specs for all products
            specs_elem = (
                soup.select_one('div.s-result-item div.a-row.a-size-small') or
                soup.select_one('div.s-result-item div.a-section.a-spacing-none') or
                soup.select_one('div.s-result-item div.a-section')
            )
            if specs_elem:
                specs_text = specs_elem.text.strip()
                specs['general'] = specs_text

            # Product-specific specs
            if product_type == 'mobile':
                # Mobile specific specs
                specs.update({
                    'camera': extract_amazon_mobile_spec(soup, 'Camera'),
                    'battery': extract_amazon_mobile_spec(soup, 'Battery'),
                    'processor': extract_amazon_mobile_spec(soup, 'Processor'),
                    'display': extract_amazon_mobile_spec(soup, 'Display'),
                    'storage': extract_amazon_mobile_spec(soup, 'Storage'),
                    'ram': extract_amazon_mobile_spec(soup, 'RAM'),
                    'weight': extract_amazon_mobile_spec(soup, 'Weight'),
                    'dimensions': extract_amazon_mobile_spec(soup, 'Dimensions')
                })
            elif product_type == 'laptop':
                # Laptop specific specs
                specs.update({
                    'processor': extract_amazon_laptop_spec(soup, 'Processor'),
                    'ram': extract_amazon_laptop_spec(soup, 'RAM'),
                    'storage': extract_amazon_laptop_spec(soup, 'Storage'),
                    'display': extract_amazon_laptop_spec(soup, 'Display'),
                    'graphics': extract_amazon_laptop_spec(soup, 'Graphics'),
                    'battery': extract_amazon_laptop_spec(soup, 'Battery'),
                    'weight': extract_amazon_laptop_spec(soup, 'Weight'),
                    'dimensions': extract_amazon_laptop_spec(soup, 'Dimensions')
                })
            elif product_type == 'tv':
                # TV specific specs
                specs.update({
                    'screen_size': extract_amazon_tv_spec(soup, 'Screen Size'),
                    'resolution': extract_amazon_tv_spec(soup, 'Resolution'),
                    'display_type': extract_amazon_tv_spec(soup, 'Display Type'),
                    'smart_tv': extract_amazon_tv_spec(soup, 'Smart TV'),
                    'hdmi_ports': extract_amazon_tv_spec(soup, 'HDMI Ports'),
                    'usb_ports': extract_amazon_tv_spec(soup, 'USB Ports'),
                    'weight': extract_amazon_tv_spec(soup, 'Weight'),
                    'dimensions': extract_amazon_tv_spec(soup, 'Dimensions')
                })

    except Exception as e:
        logger.error(f"Error extracting specs: {str(e)}")
    
    return specs

def extract_flipkart_mobile_spec(soup: BeautifulSoup, spec_name: str) -> str:
    try:
        spec_elem = soup.select_one(f'div[data-tab="{spec_name.lower()}"]')
        if spec_elem:
            return spec_elem.text.strip()
    except:
        pass
    return ''

def extract_flipkart_laptop_spec(soup: BeautifulSoup, spec_name: str) -> str:
    try:
        spec_elem = soup.select_one(f'div[data-tab="{spec_name.lower()}"]')
        if spec_elem:
            return spec_elem.text.strip()
    except:
        pass
    return ''

def extract_flipkart_tv_spec(soup: BeautifulSoup, spec_name: str) -> str:
    try:
        spec_elem = soup.select_one(f'div[data-tab="{spec_name.lower()}"]')
        if spec_elem:
            return spec_elem.text.strip()
    except:
        pass
    return ''

def extract_amazon_mobile_spec(soup: BeautifulSoup, spec_name: str) -> str:
    try:
        spec_elem = soup.select_one(f'div[data-cel-widget*="{spec_name.lower()}"]')
        if spec_elem:
            return spec_elem.text.strip()
    except:
        pass
    return ''

def extract_amazon_laptop_spec(soup: BeautifulSoup, spec_name: str) -> str:
    try:
        spec_elem = soup.select_one(f'div[data-cel-widget*="{spec_name.lower()}"]')
        if spec_elem:
            return spec_elem.text.strip()
    except:
        pass
    return ''

def extract_amazon_tv_spec(soup: BeautifulSoup, spec_name: str) -> str:
    try:
        spec_elem = soup.select_one(f'div[data-cel-widget*="{spec_name.lower()}"]')
        if spec_elem:
            return spec_elem.text.strip()
    except:
        pass
    return ''

def determine_product_type(query: str) -> str:
    query = query.lower()
    if any(word in query for word in ['mobile', 'phone', 'smartphone', 'iphone', 'samsung', 'xiaomi']):
        return 'mobile'
    elif any(word in query for word in ['laptop', 'notebook', 'macbook', 'dell', 'hp']):
        return 'laptop'
    elif any(word in query for word in ['tv', 'television', 'smart tv', 'led', 'oled']):
        return 'tv'
    return 'general'

def scrape_with_retry(url: str, max_retries: int = 3) -> Optional[BeautifulSoup]:
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to scrape {url} (Attempt {attempt + 1}/{max_retries})")
            response = requests.get(url, headers=get_headers(), timeout=10)
            response.raise_for_status()
            
            # Log response status and content length
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response content length: {len(response.text)}")
            
            # Save response content for debugging
            with open(f'debug_response_{attempt}.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            continue
    return None

def extract_flipkart_specs(soup: BeautifulSoup, item: BeautifulSoup) -> Dict[str, str]:
    specs = {}
    try:
        # Try to find the specifications section
        spec_section = item.select_one('div._3Djpdu') or item.select_one('div._3khuHA')
        if spec_section:
            # Extract all specification items
            spec_items = spec_section.select('li._21lJbe')
            for spec in spec_items:
                try:
                    key = spec.select_one('div._21lJbe')
                    value = spec.select_one('div._21lJbe + div')
                    if key and value:
                        specs[key.text.strip()] = value.text.strip()
                except:
                    continue
    except Exception as e:
        logger.error(f"Error extracting Flipkart specs: {str(e)}")
    return specs

def extract_amazon_specs(soup: BeautifulSoup, item: BeautifulSoup) -> Dict[str, str]:
    specs = {}
    try:
        # Try to find the specifications section
        spec_section = item.select_one('div.a-section') or item.select_one('div.a-spacing-small')
        if spec_section:
            # Extract all specification items
            spec_items = spec_section.select('div.a-row')
            for spec in spec_items:
                try:
                    key = spec.select_one('span.a-text-bold')
                    value = spec.select_one('span.a-text-bold + span')
                    if key and value:
                        specs[key.text.strip().replace(':', '')] = value.text.strip()
                except:
                    continue
    except Exception as e:
        logger.error(f"Error extracting Amazon specs: {str(e)}")
    return specs

def scrape_flipkart(query: str) -> List[Dict]:
    try:
        url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
        logger.info(f"Scraping Flipkart for query: {query}")
        
        soup = scrape_with_retry(url)
        if not soup:
            logger.error(f"Failed to scrape Flipkart for query: {query}")
            return []

        products = []
        product_type = determine_product_type(query)
        
        # Try different selectors for Flipkart
        selectors = [
            'div._1AtVbE',
            'div._2kHMtA',
            'div._1xHGtK',
            'div._4rR01T',
            'div._3liAhj',
            'div._1fQZEK'
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                logger.info(f"Found {len(items)} products with selector: {selector}")
                for item in items:
                    try:
                        # Try multiple selectors for each element
                        title = (
                            item.select_one('div._4rR01T') or
                            item.select_one('a.s1Q9rs') or
                            item.select_one('div._2WkVRV') or
                            item.select_one('div._3wU53n') or
                            item.select_one('div._3Djpdu')
                        )
                        price = (
                            item.select_one('div._30jeq3') or
                            item.select_one('div._1_WHN1') or
                            item.select_one('div._25b18c') or
                            item.select_one('div._1vC4OE')
                        )
                        link = (
                            item.select_one('a._1fQZEK') or
                            item.select_one('a.s1Q9rs') or
                            item.select_one('a._2UzuFa') or
                            item.select_one('a._31qSD5')
                        )
                        image = (
                            item.select_one('img._396cs4') or
                            item.select_one('img._2r_T1I') or
                            item.select_one('img._3exPp9') or
                            item.select_one('img._1Nyybr')
                        )
                        
                        if all([title, price, link, image]):
                            # Extract specifications based on product type
                            if product_type == 'mobile':
                                specs = extract_flipkart_mobile_specs(soup, item)
                            elif product_type == 'laptop':
                                specs = extract_flipkart_laptop_specs(soup, item)
                            elif product_type == 'tv':
                                specs = extract_flipkart_tv_specs(soup, item)
                            else:
                                specs = extract_flipkart_specs(soup, item)
                            
                            product = {
                                'title': title.text.strip(),
                                'price': price.text.strip(),
                                'link': 'https://www.flipkart.com' + link['href'],
                                'image': image['src'],
                                'source': 'flipkart',
                                'specs': specs
                            }
                            logger.info(f"Found Flipkart product: {product['title']}")
                            products.append(product)
                    except Exception as e:
                        logger.error(f"Error processing Flipkart product: {str(e)}")
                        continue
        
        logger.info(f"Total Flipkart products found: {len(products)}")
        time.sleep(random.uniform(1, 2))  # Random delay
        return products
    except Exception as e:
        logger.error(f"Error in Flipkart scraping: {str(e)}")
        return []

def scrape_amazon(query: str) -> List[Dict]:
    try:
        url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
        logger.info(f"Scraping Amazon for query: {query}")
        
        soup = scrape_with_retry(url)
        if not soup:
            logger.error(f"Failed to scrape Amazon for query: {query}")
            return []

        products = []
        product_type = determine_product_type(query)
        
        # Try different selectors for Amazon
        selectors = [
            'div.s-result-item',
            'div[data-component-type="s-search-result"]',
            'div.a-section',
            'div.s-include-content-margin',
            'div.a-spacing-base'
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                logger.info(f"Found {len(items)} products with selector: {selector}")
                for item in items:
                    try:
                        # Try multiple selectors for each element
                        title = (
                            item.select_one('span.a-text-normal') or
                            item.select_one('h2 a span') or
                            item.select_one('a.a-link-normal') or
                            item.select_one('div.a-section h2')
                        )
                        price = (
                            item.select_one('span.a-price-whole') or
                            item.select_one('span.a-price') or
                            item.select_one('span.a-offscreen') or
                            item.select_one('span.a-color-base')
                        )
                        link = (
                            item.select_one('a.a-link-normal') or
                            item.select_one('h2 a') or
                            item.select_one('a.a-link-normal.s-underline-text') or
                            item.select_one('div.a-section a')
                        )
                        image = (
                            item.select_one('img.s-image') or
                            item.select_one('img.a-dynamic-image') or
                            item.select_one('img[data-image-latency="s-product-image"]') or
                            item.select_one('img.a-section img')
                        )
                        
                        if all([title, price, link, image]):
                            # Extract specifications based on product type
                            if product_type == 'mobile':
                                specs = extract_amazon_mobile_specs(soup, item)
                            elif product_type == 'laptop':
                                specs = extract_amazon_laptop_specs(soup, item)
                            elif product_type == 'tv':
                                specs = extract_amazon_tv_specs(soup, item)
                            else:
                                specs = extract_amazon_specs(soup, item)
                            
                            product = {
                                'title': title.text.strip(),
                                'price': price.text.strip(),
                                'link': 'https://www.amazon.in' + link['href'],
                                'image': image['src'],
                                'source': 'amazon',
                                'specs': specs
                            }
                            logger.info(f"Found Amazon product: {product['title']}")
                            products.append(product)
                    except Exception as e:
                        logger.error(f"Error processing Amazon product: {str(e)}")
                        continue
        
        logger.info(f"Total Amazon products found: {len(products)}")
        time.sleep(random.uniform(1, 2))  # Random delay
        return products
    except Exception as e:
        logger.error(f"Error in Amazon scraping: {str(e)}")
        return []

def extract_spec_value(section: BeautifulSoup, possible_keys: List[str]) -> str:
    try:
        for key in possible_keys:
            # Try different patterns to find the specification
            patterns = [
                f"{key}:",
                f"{key} -",
                f"{key}=",
                f"{key}",
            ]
            for pattern in patterns:
                # Look for the key in text
                elem = section.find(string=re.compile(pattern, re.IGNORECASE))
                if elem:
                    # Try to get the value from different possible locations
                    value = None
                    # Try next sibling
                    if elem.next_sibling:
                        value = elem.next_sibling.strip()
                    # Try parent's next sibling
                    elif elem.parent and elem.parent.next_sibling:
                        value = elem.parent.next_sibling.strip()
                    # Try next element
                    elif elem.find_next(string=True):
                        value = elem.find_next(string=True).strip()
                    
                    if value and value != key:
                        return value
    except Exception as e:
        logger.error(f"Error extracting spec value: {str(e)}")
    return ''

def extract_flipkart_mobile_specs(soup: BeautifulSoup, item: BeautifulSoup) -> Dict[str, str]:
    specs = {}
    try:
        # Try to find the specifications section
        spec_section = item.select_one('div._3Djpdu') or item.select_one('div._3khuHA')
        if spec_section:
            # Extract all specification items
            spec_items = spec_section.select('li._21lJbe')
            for spec in spec_items:
                try:
                    key = spec.select_one('div._21lJbe')
                    value = spec.select_one('div._21lJbe + div')
                    if key and value:
                        specs[key.text.strip()] = value.text.strip()
                except:
                    continue

        # Additional mobile-specific specs with improved extraction
        mobile_specs = {
            'camera': extract_spec_value(spec_section, ['Camera', 'Primary Camera', 'Rear Camera', 'Main Camera']),
            'front_camera': extract_spec_value(spec_section, ['Front Camera', 'Selfie Camera', 'Secondary Camera']),
            'processor': extract_spec_value(spec_section, ['Processor', 'CPU', 'Chipset', 'SoC']),
            'ram': extract_spec_value(spec_section, ['RAM', 'Memory', 'System Memory']),
            'storage': extract_spec_value(spec_section, ['Storage', 'Internal Storage', 'ROM']),
            'battery': extract_spec_value(spec_section, ['Battery', 'Battery Capacity', 'Battery Power']),
            'display': extract_spec_value(spec_section, ['Display', 'Screen Size', 'Screen']),
            'resolution': extract_spec_value(spec_section, ['Resolution', 'Display Resolution', 'Screen Resolution']),
            'weight': extract_spec_value(spec_section, ['Weight', 'Body Weight', 'Product Weight']),
            'dimensions': extract_spec_value(spec_section, ['Dimensions', 'Size', 'Product Dimensions']),
            'os': extract_spec_value(spec_section, ['Operating System', 'OS', 'Android Version']),
            'colors': extract_spec_value(spec_section, ['Color', 'Colors', 'Available Colors']),
            'sim': extract_spec_value(spec_section, ['SIM', 'SIM Type', 'SIM Slot']),
            'network': extract_spec_value(spec_section, ['Network', 'Network Type', 'Connectivity']),
            'warranty': extract_spec_value(spec_section, ['Warranty', 'Warranty Period', 'Warranty Information'])
        }
        specs.update(mobile_specs)
    except Exception as e:
        logger.error(f"Error extracting Flipkart mobile specs: {str(e)}")
    return specs

def extract_flipkart_laptop_specs(soup: BeautifulSoup, item: BeautifulSoup) -> Dict[str, str]:
    specs = {}
    try:
        # Try to find the specifications section
        spec_section = item.select_one('div._3Djpdu') or item.select_one('div._3khuHA')
        if spec_section:
            # Extract all specification items
            spec_items = spec_section.select('li._21lJbe')
            for spec in spec_items:
                try:
                    key = spec.select_one('div._21lJbe')
                    value = spec.select_one('div._21lJbe + div')
                    if key and value:
                        specs[key.text.strip()] = value.text.strip()
                except:
                    continue

        # Additional laptop-specific specs with improved extraction
        laptop_specs = {
            'processor': extract_spec_value(spec_section, ['Processor', 'CPU', 'Processor Type']),
            'ram': extract_spec_value(spec_section, ['RAM', 'Memory', 'System Memory']),
            'storage': extract_spec_value(spec_section, ['Storage', 'Hard Drive', 'SSD', 'HDD']),
            'display': extract_spec_value(spec_section, ['Display', 'Screen Size', 'Screen']),
            'resolution': extract_spec_value(spec_section, ['Resolution', 'Display Resolution', 'Screen Resolution']),
            'graphics': extract_spec_value(spec_section, ['Graphics', 'GPU', 'Graphics Card']),
            'battery': extract_spec_value(spec_section, ['Battery', 'Battery Life', 'Battery Capacity']),
            'weight': extract_spec_value(spec_section, ['Weight', 'Product Weight']),
            'dimensions': extract_spec_value(spec_section, ['Dimensions', 'Size', 'Product Dimensions']),
            'os': extract_spec_value(spec_section, ['Operating System', 'OS', 'Windows Version']),
            'ports': extract_spec_value(spec_section, ['Ports', 'Connectivity', 'I/O Ports']),
            'warranty': extract_spec_value(spec_section, ['Warranty', 'Warranty Period', 'Warranty Information'])
        }
        specs.update(laptop_specs)
    except Exception as e:
        logger.error(f"Error extracting Flipkart laptop specs: {str(e)}")
    return specs

def extract_flipkart_tv_specs(soup: BeautifulSoup, item: BeautifulSoup) -> Dict[str, str]:
    specs = {}
    try:
        # Try to find the specifications section
        spec_section = item.select_one('div._3Djpdu') or item.select_one('div._3khuHA')
        if spec_section:
            # Extract all specification items
            spec_items = spec_section.select('li._21lJbe')
            for spec in spec_items:
                try:
                    key = spec.select_one('div._21lJbe')
                    value = spec.select_one('div._21lJbe + div')
                    if key and value:
                        specs[key.text.strip()] = value.text.strip()
                except:
                    continue

        # Additional TV-specific specs with improved extraction
        tv_specs = {
            'screen_size': extract_spec_value(spec_section, ['Screen Size', 'Display Size', 'Screen']),
            'resolution': extract_spec_value(spec_section, ['Resolution', 'Display Resolution', 'Screen Resolution']),
            'display_type': extract_spec_value(spec_section, ['Display Type', 'Panel Type', 'Screen Type']),
            'smart_tv': extract_spec_value(spec_section, ['Smart TV', 'Smart Features', 'Operating System']),
            'hdmi_ports': extract_spec_value(spec_section, ['HDMI Ports', 'HDMI', 'HDMI Inputs']),
            'usb_ports': extract_spec_value(spec_section, ['USB Ports', 'USB', 'USB Inputs']),
            'weight': extract_spec_value(spec_section, ['Weight', 'Product Weight']),
            'dimensions': extract_spec_value(spec_section, ['Dimensions', 'Size', 'Product Dimensions']),
            'refresh_rate': extract_spec_value(spec_section, ['Refresh Rate', 'Motion Rate']),
            'hdr': extract_spec_value(spec_section, ['HDR', 'HDR Support', 'High Dynamic Range']),
            'warranty': extract_spec_value(spec_section, ['Warranty', 'Warranty Period', 'Warranty Information'])
        }
        specs.update(tv_specs)
    except Exception as e:
        logger.error(f"Error extracting Flipkart TV specs: {str(e)}")
    return specs

def extract_amazon_mobile_specs(soup: BeautifulSoup, item: BeautifulSoup) -> Dict[str, str]:
    specs = {}
    try:
        # Try to find the specifications section
        spec_section = item.select_one('div.a-section') or item.select_one('div.a-spacing-small')
        if spec_section:
            # Extract all specification items
            spec_items = spec_section.select('div.a-row')
            for spec in spec_items:
                try:
                    key = spec.select_one('span.a-text-bold')
                    value = spec.select_one('span.a-text-bold + span')
                    if key and value:
                        specs[key.text.strip().replace(':', '')] = value.text.strip()
                except:
                    continue

        # Additional mobile-specific specs with improved extraction
        mobile_specs = {
            'camera': extract_spec_value(spec_section, ['Camera', 'Primary Camera', 'Rear Camera', 'Main Camera']),
            'front_camera': extract_spec_value(spec_section, ['Front Camera', 'Selfie Camera', 'Secondary Camera']),
            'processor': extract_spec_value(spec_section, ['Processor', 'CPU', 'Chipset', 'SoC']),
            'ram': extract_spec_value(spec_section, ['RAM', 'Memory', 'System Memory']),
            'storage': extract_spec_value(spec_section, ['Storage', 'Internal Storage', 'ROM']),
            'battery': extract_spec_value(spec_section, ['Battery', 'Battery Capacity', 'Battery Power']),
            'display': extract_spec_value(spec_section, ['Display', 'Screen Size', 'Screen']),
            'resolution': extract_spec_value(spec_section, ['Resolution', 'Display Resolution', 'Screen Resolution']),
            'weight': extract_spec_value(spec_section, ['Weight', 'Body Weight', 'Product Weight']),
            'dimensions': extract_spec_value(spec_section, ['Dimensions', 'Size', 'Product Dimensions']),
            'os': extract_spec_value(spec_section, ['Operating System', 'OS', 'Android Version']),
            'colors': extract_spec_value(spec_section, ['Color', 'Colors', 'Available Colors']),
            'sim': extract_spec_value(spec_section, ['SIM', 'SIM Type', 'SIM Slot']),
            'network': extract_spec_value(spec_section, ['Network', 'Network Type', 'Connectivity']),
            'warranty': extract_spec_value(spec_section, ['Warranty', 'Warranty Period', 'Warranty Information'])
        }
        specs.update(mobile_specs)
    except Exception as e:
        logger.error(f"Error extracting Amazon mobile specs: {str(e)}")
    return specs

def extract_amazon_laptop_specs(soup: BeautifulSoup, item: BeautifulSoup) -> Dict[str, str]:
    specs = {}
    try:
        # Try to find the specifications section
        spec_section = item.select_one('div.a-section') or item.select_one('div.a-spacing-small')
        if spec_section:
            # Extract all specification items
            spec_items = spec_section.select('div.a-row')
            for spec in spec_items:
                try:
                    key = spec.select_one('span.a-text-bold')
                    value = spec.select_one('span.a-text-bold + span')
                    if key and value:
                        specs[key.text.strip().replace(':', '')] = value.text.strip()
                except:
                    continue

        # Additional laptop-specific specs with improved extraction
        laptop_specs = {
            'processor': extract_spec_value(spec_section, ['Processor', 'CPU', 'Processor Type']),
            'ram': extract_spec_value(spec_section, ['RAM', 'Memory', 'System Memory']),
            'storage': extract_spec_value(spec_section, ['Storage', 'Hard Drive', 'SSD', 'HDD']),
            'display': extract_spec_value(spec_section, ['Display', 'Screen Size', 'Screen']),
            'resolution': extract_spec_value(spec_section, ['Resolution', 'Display Resolution', 'Screen Resolution']),
            'graphics': extract_spec_value(spec_section, ['Graphics', 'GPU', 'Graphics Card']),
            'battery': extract_spec_value(spec_section, ['Battery', 'Battery Life', 'Battery Capacity']),
            'weight': extract_spec_value(spec_section, ['Weight', 'Product Weight']),
            'dimensions': extract_spec_value(spec_section, ['Dimensions', 'Size', 'Product Dimensions']),
            'os': extract_spec_value(spec_section, ['Operating System', 'OS', 'Windows Version']),
            'ports': extract_spec_value(spec_section, ['Ports', 'Connectivity', 'I/O Ports']),
            'warranty': extract_spec_value(spec_section, ['Warranty', 'Warranty Period', 'Warranty Information'])
        }
        specs.update(laptop_specs)
    except Exception as e:
        logger.error(f"Error extracting Amazon laptop specs: {str(e)}")
    return specs

def extract_amazon_tv_specs(soup: BeautifulSoup, item: BeautifulSoup) -> Dict[str, str]:
    specs = {}
    try:
        # Try to find the specifications section
        spec_section = item.select_one('div.a-section') or item.select_one('div.a-spacing-small')
        if spec_section:
            # Extract all specification items
            spec_items = spec_section.select('div.a-row')
            for spec in spec_items:
                try:
                    key = spec.select_one('span.a-text-bold')
                    value = spec.select_one('span.a-text-bold + span')
                    if key and value:
                        specs[key.text.strip().replace(':', '')] = value.text.strip()
                except:
                    continue

        # Additional TV-specific specs with improved extraction
        tv_specs = {
            'screen_size': extract_spec_value(spec_section, ['Screen Size', 'Display Size', 'Screen']),
            'resolution': extract_spec_value(spec_section, ['Resolution', 'Display Resolution', 'Screen Resolution']),
            'display_type': extract_spec_value(spec_section, ['Display Type', 'Panel Type', 'Screen Type']),
            'smart_tv': extract_spec_value(spec_section, ['Smart TV', 'Smart Features', 'Operating System']),
            'hdmi_ports': extract_spec_value(spec_section, ['HDMI Ports', 'HDMI', 'HDMI Inputs']),
            'usb_ports': extract_spec_value(spec_section, ['USB Ports', 'USB', 'USB Inputs']),
            'weight': extract_spec_value(spec_section, ['Weight', 'Product Weight']),
            'dimensions': extract_spec_value(spec_section, ['Dimensions', 'Size', 'Product Dimensions']),
            'refresh_rate': extract_spec_value(spec_section, ['Refresh Rate', 'Motion Rate']),
            'hdr': extract_spec_value(spec_section, ['HDR', 'HDR Support', 'High Dynamic Range']),
            'warranty': extract_spec_value(spec_section, ['Warranty', 'Warranty Period', 'Warranty Information'])
        }
        specs.update(tv_specs)
    except Exception as e:
        logger.error(f"Error extracting Amazon TV specs: {str(e)}")
    return specs