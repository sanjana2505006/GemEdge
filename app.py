"""Flask web dashboard for viewing scraped book data."""

import json
import os
from pathlib import Path
from flask import Flask, render_template, jsonify, request
import pandas as pd
import plotly.graph_objs as go
import plotly.utils
from scraper.utils import read_json

app = Flask(__name__)

# Configuration
app.config['JSON_SORT_KEYS'] = False

def load_scraped_data():
    """Load the most recent scraped data."""
    data_file = Path('output/items.json')
    if not data_file.exists():
        return []
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def get_data_stats(data):
    """Calculate statistics for the scraped data."""
    if not data:
        return {}
    
    df = pd.DataFrame(data)
    
    stats = {
        'total_books': len(df),
        'categories': df['category'].nunique() if 'category' in df.columns else 0,
        'avg_price': df['price_inr'].mean() if 'price_inr' in df.columns else 0,
        'price_range': {
            'min': df['price_inr'].min() if 'price_inr' in df.columns else 0,
            'max': df['price_inr'].max() if 'price_inr' in df.columns else 0
        }
    }
    
    return stats

def create_price_chart(data):
    """Create a price distribution chart."""
    if not data:
        return None

    df = pd.DataFrame(data)
    if 'price_inr' not in df.columns:
        return None

    prices = df['price_inr'].dropna().tolist()

    fig = go.Figure(data=[go.Histogram(
        x=prices,
        nbinsx=15,
        marker_color='#7c3aed',
        opacity=0.8
    )])
    fig.update_layout(
        xaxis_title='Price (INR)',
        yaxis_title='Number of Books',
        template='plotly_white',
        margin=dict(l=40, r=20, t=20, b=40),
        bargap=0.05,
    )
    fig.update_xaxes(tickprefix='₹', tickformat=',')

    return json.dumps({'data': fig.to_dict()['data'], 'layout': fig.to_dict()['layout']},
                      cls=plotly.utils.PlotlyJSONEncoder)

def create_category_chart(data):
    """Create a category distribution bar chart."""
    if not data:
        return None

    df = pd.DataFrame(data)
    if 'category' not in df.columns:
        return None

    category_counts = df['category'].value_counts().sort_values(ascending=True)

    fig = go.Figure(data=[go.Bar(
        x=category_counts.values.tolist(),
        y=category_counts.index.tolist(),
        orientation='h',
        marker_color='#7c3aed',
        opacity=0.8,
        text=category_counts.values.tolist(),
        textposition='outside',
    )])
    fig.update_layout(
        xaxis_title='Number of Books',
        yaxis_title='',
        template='plotly_white',
        margin=dict(l=120, r=40, t=20, b=40),
        height=max(300, len(category_counts) * 22),
    )

    return json.dumps({'data': fig.to_dict()['data'], 'layout': fig.to_dict()['layout']},
                      cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/')
def dashboard():
    """Main dashboard page."""
    data = load_scraped_data()
    stats = get_data_stats(data)
    price_chart = create_price_chart(data)
    category_chart = create_category_chart(data)
    
    return render_template('dashboard.html',
                         data=data,
                         stats=stats,
                         price_chart=price_chart,
                         category_chart=category_chart)

@app.route('/api/data')
def api_data():
    """API endpoint for filtered data."""
    data = load_scraped_data()
    
    # Get filter parameters
    category = request.args.get('category', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    search = request.args.get('search', '').lower()
    
    # Apply filters
    filtered_data = data
    
    if category:
        filtered_data = [item for item in filtered_data 
                        if item.get('category', '').lower() == category.lower()]
    
    if min_price is not None:
        filtered_data = [item for item in filtered_data 
                        if item.get('price_inr', 0) >= min_price]
    
    if max_price is not None:
        filtered_data = [item for item in filtered_data 
                        if item.get('price_inr', float('inf')) <= max_price]
    
    if search:
        filtered_data = [item for item in filtered_data 
                        if search in item.get('title', '').lower() or 
                           search in item.get('description', '').lower()]
    
    return jsonify(filtered_data)

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics."""
    data = load_scraped_data()
    stats = get_data_stats(data)
    return jsonify(stats)

@app.route('/api/categories')
def api_categories():
    """API endpoint for available categories."""
    data = load_scraped_data()
    if not data:
        return jsonify([])
    
    categories = list(set(item.get('category', '') for item in data if item.get('category')))
    categories.sort()
    return jsonify(categories)

@app.route('/refresh')
def refresh_data():
    """Trigger data refresh."""
    # This would trigger a new scrape
    # For now, just reload existing data
    data = load_scraped_data()
    stats = get_data_stats(data)
    
    return jsonify({
        'message': 'Data refreshed',
        'stats': stats,
        'data_count': len(data)
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5001)
