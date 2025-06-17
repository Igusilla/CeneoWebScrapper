import os
import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
from app.managers.opinion_manager import OpinionManager
from app.managers.product_manager import ProductManager
matplotlib.use('Agg')

class ChartGenerator:
    @staticmethod
    def generate_charts(product_id):
        os.makedirs("./app/static/images/charts", exist_ok=True)
        stats = ProductManager.get_stats(product_id)
        # Pie chart
        recommendations = pd.Series(stats['recommendations'])
        recommendations.plot.pie(
            label="",
            title=f"Rozkład rekomendacji w opiniach o produkcie {product_id}",
            labels=["Nie polecam", "Polecam", "Nie mam zdania"],
            colors=["#C05757", "#548A33", "#575757"],
            textprops={'fontsize': 12, 'color': '#B3B3B3'},
            autopct="%1.1f%%"
        )
        plt.title(f"Rozkład rekomendacji w opiniach o produkcie {product_id}",
                  color='#B3B3B3', fontsize=14, pad=20)
        plt.gcf().patch.set_facecolor('#36312B')
        plt.savefig(f"./app/static/images/charts/{stats['product_id']}_pie.png")
        plt.close()
        # Bar chart
        df = OpinionManager.to_dataframe(product_id)
        stars = df["stars"].value_counts().sort_index()
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