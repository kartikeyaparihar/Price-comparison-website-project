print("Starting Flask app...")
from flask import Flask, render_template, request, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from models import db, SearchQuery, Product
from scraper import scrape_flipkart, scrape_amazon
import logging
from datetime import datetime, timedelta
from functools import wraps
import json
import traceback

# Set up logging with more detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production
db.init_app(app)

# Cache configuration
CACHE_DURATION = timedelta(hours=1)

def cache_result(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
        cached_result = SearchQuery.query.filter_by(search_term=cache_key).first()
        
        if cached_result and (datetime.utcnow() - cached_result.timestamp) < CACHE_DURATION:
            return cached_result.products
        
        result = func(*args, **kwargs)
        return result
    return wrapper

with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        logger.error(traceback.format_exc())

CATEGORIES = {
    'mobiles': 'mobile phones',
    'laptops': 'laptops',
    'televisions': 'television'
}

@app.route('/')
def home():
    return render_template('templates.html', categories=CATEGORIES)

@app.route('/search', methods=['POST'])
def search():
    try:
        query = request.form['query'].strip().lower()
        logger.info(f"Search request received for query: {query}")
        
        if not query:
            flash('Please enter a search term', 'error')
            return render_template('templates.html', categories=CATEGORIES)

        # Check if query exists in DB and is recent
        search_query = SearchQuery.query.filter_by(search_term=query).first()
        if not search_query or (datetime.utcnow() - search_query.timestamp) > CACHE_DURATION:
            logger.info(f"Query not found in cache or expired, scraping new results")
            
            # Scrape and store
            flipkart_products = scrape_flipkart(query)
            amazon_products = scrape_amazon(query)
            all_products = flipkart_products + amazon_products
            
            logger.info(f"Found {len(all_products)} total products")
            
            if not all_products:
                flash('No products found. Please try a different search term.', 'error')
                return render_template('templates.html', categories=CATEGORIES)

            if search_query:
                # Update existing search
                search_query.timestamp = datetime.utcnow()
                # Delete old products
                Product.query.filter_by(search_term=query).delete()
            else:
                search_query = SearchQuery(search_term=query)
                db.session.add(search_query)
            
            db.session.commit()
            
            for p in all_products:
                product = Product(
                    search_term=query,
                    title=p['title'],
                    price=p['price'],
                    link=p['link'],
                    image=p['image'],
                    source=p['source'],
                    specs=json.dumps(p['specs'])  # Convert specs dict to JSON string
                )
                db.session.add(product)
            db.session.commit()
            logger.info(f"Saved {len(all_products)} products to database")

        # Fetch from DB
        products = Product.query.filter_by(search_term=query).all()
        logger.info(f"Retrieved {len(products)} products from database")
        
        return render_template('search_results.html', products=products, query=query)
    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        logger.error(traceback.format_exc())
        flash('An error occurred while searching. Please try again.', 'error')
        return render_template('templates.html', categories=CATEGORIES)

@app.route('/category/<cat>')
def category(cat):
    try:
        logger.info(f"Category request received for: {cat}")
        
        if cat not in CATEGORIES:
            flash('Category not found', 'error')
            return render_template('templates.html', categories=CATEGORIES)
        
        query = CATEGORIES[cat]
        return search()  # Reuse search logic
    except Exception as e:
        logger.error(f"Error in category view: {str(e)}")
        logger.error(traceback.format_exc())
        flash('An error occurred while loading the category.', 'error')
        return render_template('templates.html', categories=CATEGORIES)

@app.route('/compare', methods=['POST'])
def compare():
    try:
        ids = request.form.getlist('product_ids')
        logger.info(f"Compare request received for product IDs: {ids}")
        
        if len(ids) != 2:
            flash('Please select exactly two products to compare.', 'error')
            return render_template('templates.html', categories=CATEGORIES)
        
        products = Product.query.filter(Product.id.in_(ids)).all()
        if len(products) != 2:
            flash('One or more selected products could not be found.', 'error')
            return render_template('templates.html', categories=CATEGORIES)

        def parse_price(p):
            try:
                return float(p.price.replace(',', '').replace('₹', '').replace(' ', '') or '0')
            except:
                return float('inf')

        # Enhanced comparison logic
        prices = [parse_price(p) for p in products]
        price_diff = abs(prices[0] - prices[1])
        price_diff_percent = (price_diff / min(prices)) * 100 if min(prices) > 0 else 0
        
        # Determine the better deal
        if price_diff_percent > 10:  # If price difference is more than 10%
            suggestion = min(products, key=parse_price)
            reason = f"This product is {price_diff_percent:.1f}% cheaper than the other option."
        else:
            suggestion = None
            reason = "Both products are similarly priced. Consider other factors like specifications and reviews."

        logger.info(f"Comparison completed. Price difference: {price_diff_percent:.1f}%")
        
        return render_template('compare.html', 
                             products=products, 
                             suggestion=suggestion,
                             price_diff=price_diff,
                             price_diff_percent=price_diff_percent,
                             reason=reason)
    except Exception as e:
        logger.error(f"Error in comparison: {str(e)}")
        logger.error(traceback.format_exc())
        flash('An error occurred while comparing products.', 'error')
        return render_template('templates.html', categories=CATEGORIES)

@app.errorhandler(404)
def page_not_found(e):
    logger.error(f"404 error: {str(e)}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"500 error: {str(e)}")
    logger.error(traceback.format_exc())
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)