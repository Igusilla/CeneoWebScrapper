from app import app
from flask import render_template, request, redirect, url_for
from app.managers.opinion_manager import OpinionManager
from app.managers.product_manager import ProductManager
from app.utilities.chart_generator import ChartGenerator
from app.managers.download_manager import DownloadManager

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/extract")
def display_form():
    return render_template("extract.html")

@app.route("/extract", methods=["POST"])
def extract():
    product_id = request.form.get("product_id").strip()
    product_name, error = OpinionManager.from_scraping(product_id)
    if error:
        return render_template("extract.html", error=error)
    return redirect(url_for('product', product_id=product_id, product_name=product_name))

@app.route("/products")
def products():
    products = ProductManager.all()
    return render_template("products.html", products=products)

@app.route("/author")
def author():
    return render_template("author.html")

@app.route("/product/<product_id>")
def product(product_id):
    product_name = request.args.get('product_name')
    opinions = OpinionManager.all(product_id)
    return render_template("product.html", product_id=product_id, product_name=product_name, opinions=opinions)

@app.route("/charts/<product_id>")
def charts(product_id):
    ChartGenerator.generate_charts(product_id)
    stats = ProductManager.get_stats(product_id)
    return render_template("charts.html", product_id=product_id, product_name=stats['product_name'])

@app.route("/download/<product_id>/<filetype>")
def download(product_id, filetype):
    return DownloadManager.download(product_id, filetype, app.root_path)