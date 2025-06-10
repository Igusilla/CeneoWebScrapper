from app import app
import os
import json
import requests
import pandas as pd
from flask import render_template, request, redirect, url_for
from config import headers
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
from app import utils

import matplotlib
matplotlib.use('Agg')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/extract")
def display_form():
    return render_template("extract.html")

@app.route("/", methods=["POST"])
def extract():
    product_id = request.form.get("product_id")
    next_page = f"https://www.ceneo.pl/{product_id}#tab=reviews"
    response = requests.get(next_page,headers=headers)
    if response.status_code == 200:
        page_dom = BeautifulSoup(response.text, "html.parser")
        product_name = utils.extract_feature(page_dom, "h1")
        opinions_count = utils.extract_feature(page_dom, "a.product-review__link > span")
        if not opinions_count:
            error="Dla produktu o podanym id nie ma jeszcze żadnych opinii"
            return render_template("extract.html", error=error)
    else:
        error="Nie znaleziono produktu o podanym id"
        return render_template("extract.html", error=error)
    all_opinions = []
    while next_page:
        print(next_page)
        response = requests.get(next_page,headers=headers)
        if response.status_code == 200:
            page_dom = BeautifulSoup(response.text, "html.parser")
            opinions = page_dom.select("div.js_product-review:not(.user-post--highlight)")
            for opinion in opinions:
                single_opinion = {
                    key: utils.extract_feature(opinion,*value)
                    for key, value in utils.selectors.items()
                }
                all_opinions.append(single_opinion)
            try:
                next_page = "https://www.ceneo.pl" + utils.extract_feature(page_dom,"a.pagination__next","href")
            except TypeError:
                next_page = None
        else: print(response.status_code)
    if not os.path.exists("./app/data"):
        os.mkdir("./app/data")
    if not os.path.exists("./app/data/opinions"):
        os.mkdir("./app/data/opinions")
    with open(f"./app/data/opinions/{product_id}.json", "w", encoding="UTF-8") as jf:
        json.dump(all_opinions, jf, indent=4, ensure_ascii=False)
    opinions = pd.DataFrame.from_dict(all_opinions)
    opinions.stars = opinions.stars.apply(lambda s: s.split("/")[0].replace(",",".")).astype(float)
    opinions.useful = opinions.useful.astype(int)
    opinions.unuseful = opinions.unuseful.astype(int)
    stats = {
        'product_id': product_id,
        'product_name': product_name,
        "opinions_count": opinions.shape[0],
        "pros_count": int(opinions.pros.astype(bool).sum()),
        "cons_count": int(opinions.cons.astype(bool).sum()),
        "pros_cons_count": int(opinions.apply(lambda o: bool(o.pros) and bool(o.cons), axis=1).sum()),
        "average_stars": float(opinions.stars.mean()),
        "pros": opinions.pros.explode().dropna().value_counts().to_dict(),
        "cons": opinions.cons.explode().dropna().value_counts().to_dict(),
        "recommendations": opinions.recommendation.value_counts(dropna=False).reindex(['Nie polecam','Polecam', None], fill_value=0).to_dict(),
    }
    if not os.path.exists("./app/data"):
        os.mkdir("./app/data")
    if not os.path.exists("./app/data/products"):
        os.mkdir("./app/data/products")
    with open(f"./app/data/products/{product_id}.json", "w", encoding="UTF-8") as jf:
        json.dump(stats, jf, indent=4, ensure_ascii=False)
    return redirect(url_for('product', product_id=product_id, product_name=product_name))

@app.route("/products")
def products():
    products_files = os.listdir("./app/data/products")
    products_list = []
    for filename in products_files:
        with open(f"./app/data/products/{filename}","r", encoding="UTF-8") as jf:
            product = json.load(jf)
            products_list.append(product)
    return render_template("products.html", products=products_list)

@app.route("/author")
def author():
    return render_template("author.html")

@app.route("/product/<product_id>")
def product(product_id):
    product_name = request.args.get('product_name')
    with open(f"./app/data/opinions/{product_id}.json", "r", encoding="UTF-8") as jf:
        opinions = json.load(jf)
    return render_template("product.html", product_id=product_id, product_name=product_name, opinions=opinions) 

@app.route("/charts/<product_id>")
def charts(product_id):
    if not os.path.exists("./app/static/images"):
        os.mkdir("./app/static/images")
    if not os.path.exists("./app/static/images/charts"):
        os.mkdir("./app/static/images/charts")
    with open(f"./app/data/products/{product_id}.json", "r", encoding="UTF-8") as jf:
        stats = json.load(jf)
    recommendations = pd.Series(stats['recommendations'])
    #WYKRES KOŁOWY
    recommendations.plot.pie(
        label = "",
        title = f"Rozkład rekomendacji w opiniach o produkcie {product_id}",
        labels = ["Nie polecam", "Polecam", "Nie mam zdania"],
        colors = ["#C05757", "#548A33", "#575757"],
        textprops={'fontsize': 12, 'color': '#B3B3B3'},
        autopct = "%1.1f%%"
        )
    plt.title(f"Rozkład rekomendacji w opiniach o produkcie {product_id}", 
          color='#B3B3B3', fontsize=16, pad=20)
    plt.gcf().patch.set_facecolor('#36312B')
    plt.savefig(f"./app/static/images/charts/{stats['product_id']}_pie.png")
    plt.close()
    #WYKRES KOLUMNOWY
    with open(f"./app/data/opinions/{product_id}.json", "r", encoding="utf-8") as jf:
        opinions = pd.read_json(jf)
    stars = opinions["stars"].value_counts().sort_index()
    stars.plot.bar(
        title=f"Rozkład gwiazdek dla produktu {product_id}",            
        color="#548A33",
    )
    plt.gcf().patch.set_facecolor('#36312B')
    plt.gca().set_facecolor('#36312B')

    plt.title(f"Rozkład gwiazdek dla produktu {product_id}", 
            color='#B3B3B3', fontsize=16, pad=20)
    plt.xlabel("Liczba gwiazdek", color='#B3B3B3')
    plt.ylabel("Liczba opinii", color='#B3B3B3')

    plt.xticks(color='#B3B3B3')
    plt.yticks(color='#B3B3B3')

    plt.grid(True, alpha=0.3, color='#B3B3B3', axis='y')

    plt.savefig(f"./app/static/images/charts/{product_id}_bar.png", 
        facecolor='#36312B',
        bbox_inches='tight')
    plt.close()
    return render_template("charts.html", product_id=product_id, product_name=stats['product_name']) 

#TRZEBA DODAĆ FUNKCJONALNOŚĆ PRZYCISKÓW DO POBIERANIA W DANYCH FORMATACH