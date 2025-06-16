from app import app
from flask import render_template, request, redirect, url_for, Response, send_file
from app.models import ProductManager, OpinionManager, ChartManager
import io
import os

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

@app.route("/product/<product_id>")
def product(product_id):
    product_name = request.args.get('product_name')
    opinions = OpinionManager.all(product_id)
    return render_template("product.html", product_id=product_id, product_name=product_name, opinions=opinions)

@app.route("/charts/<product_id>")
def charts(product_id):
    ChartManager.generate_charts(product_id)
    stats = ProductManager.get_stats(product_id)
    return render_template("charts.html", product_id=product_id, product_name=stats['product_name'])

@app.route("/download/<product_id>/<filetype>")
def download(product_id, filetype):
    df = OpinionManager.to_dataframe(product_id)
    if filetype == "json":
        path = os.path.join(app.root_path, "data", "opinions", f"{product_id}.json")
        return send_file(
            path,
            mimetype="application/json",
            as_attachment=True,
            download_name=f"{product_id}.json"
        )
    elif filetype == "csv":
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename={product_id}.csv"}
        )
    elif filetype == "xlsx":
        output = io.BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment;filename={product_id}.xlsx"}
        )
    else:
        return "Nieobsługiwany format", 400

from flask.views import MethodView

class AuthorView(MethodView):
    def get(self):
        return render_template("author.html")

app.add_url_rule("/author", view_func=AuthorView.as_view("author"))