import json
from pathlib import Path
from flask import Flask, render_template, jsonify, request
import pandas as pd
import plotly.graph_objs as go
import plotly.utils

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


def load_data():
    data_file = Path('output/items.json')
    if not data_file.exists():
        return []
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def get_stats(data):
    if not data:
        return {}
    df = pd.DataFrame(data)
    return {
        'total_books': len(df),
        'categories': df['category'].nunique() if 'category' in df.columns else 0,
        'avg_price': df['price_inr'].mean() if 'price_inr' in df.columns else 0,
        'price_range': {
            'min': df['price_inr'].min() if 'price_inr' in df.columns else 0,
            'max': df['price_inr'].max() if 'price_inr' in df.columns else 0,
        }
    }


def price_chart(data):
    if not data:
        return None
    df = pd.DataFrame(data)
    if 'price_inr' not in df.columns:
        return None
    fig = go.Figure(data=[go.Histogram(
        x=df['price_inr'].dropna().tolist(),
        nbinsx=15,
        marker_color='#0ea5e9',
        opacity=0.85,
    )])
    fig.update_layout(
        xaxis_title='Price (INR)',
        yaxis_title='Number of Books',
        template='plotly_white',
        margin=dict(l=40, r=20, t=20, b=40),
        bargap=0.05,
    )
    fig.update_xaxes(tickprefix='₹', tickformat=',')
    d = fig.to_dict()
    return json.dumps({'data': d['data'], 'layout': d['layout']}, cls=plotly.utils.PlotlyJSONEncoder)


def category_chart(data):
    if not data:
        return None
    df = pd.DataFrame(data)
    if 'category' not in df.columns:
        return None
    counts = df['category'].value_counts().sort_values(ascending=True)
    counts.index = [c if c != 'Default' else 'General' for c in counts.index]
    palette = [
        '#6366f1', '#0ea5e9', '#10b981', '#f59e0b', '#ef4444',
        '#8b5cf6', '#14b8a6', '#f97316', '#ec4899', '#84cc16',
        '#06b6d4', '#a855f7', '#22c55e', '#eab308', '#3b82f6',
    ]
    colors = [palette[i % len(palette)] for i in range(len(counts))]
    fig = go.Figure(data=[go.Bar(
        x=counts.values.tolist(),
        y=counts.index.tolist(),
        orientation='h',
        marker_color=colors,
        opacity=0.9,
        text=counts.values.tolist(),
        textposition='outside',
    )])
    fig.update_layout(
        xaxis_title='Number of Books',
        yaxis_title='',
        template='plotly_white',
        margin=dict(l=120, r=40, t=20, b=40),
        height=max(400, len(counts) * 28),
    )
    d = fig.to_dict()
    return json.dumps({'data': d['data'], 'layout': d['layout']}, cls=plotly.utils.PlotlyJSONEncoder)


@app.route('/')
def dashboard():
    data = load_data()
    return render_template('dashboard.html',
                           data=data,
                           stats=get_stats(data),
                           price_chart=price_chart(data),
                           category_chart=category_chart(data))


@app.route('/api/data')
def api_data():
    data = load_data()
    category = request.args.get('category', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    search = request.args.get('search', '').lower()

    if category:
        data = [i for i in data if (i.get('category', '') or 'Default').replace('Default', 'General').lower() == category.lower()]
    if min_price is not None:
        data = [i for i in data if i.get('price_inr', 0) >= min_price]
    if max_price is not None:
        data = [i for i in data if i.get('price_inr', float('inf')) <= max_price]
    if search:
        data = [i for i in data if search in i.get('title', '').lower()
                or search in i.get('description', '').lower()]
    return jsonify(data)


@app.route('/api/stats')
def api_stats():
    return jsonify(get_stats(load_data()))


@app.route('/api/categories')
def api_categories():
    data = load_data()
    cats = sorted(set((i.get('category', '') or 'Default').replace('Default', 'General') for i in data if i.get('category')))
    return jsonify(cats)


@app.route('/refresh')
def refresh():
    data = load_data()
    return jsonify({'stats': get_stats(data), 'data_count': len(data)})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
