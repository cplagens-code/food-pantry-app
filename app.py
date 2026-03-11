from flask import Flask, render_template, request
import requests

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    ingredients = request.form["ingredients"]
    ingredient_list = [item.strip().lower() for item in ingredients.split(",") if item.strip()]

    recipes = []
    seen_meals = set()

    for ingredient in ingredient_list:
        url = f"https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}"
        response = requests.get(url)
        data = response.json()

        if data.get("meals"):
            for meal in data["meals"]:
                meal_id = meal["idMeal"]

                if meal_id not in seen_meals:
                    seen_meals.add(meal_id)

                    detail_url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"
                    detail_response = requests.get(detail_url)
                    detail_data = detail_response.json()

                    if detail_data.get("meals"):
                        detailed_meal = detail_data["meals"][0]
                        recipes.append({
                            "name": detailed_meal["strMeal"],
                            "link": detailed_meal["strSource"] if detailed_meal["strSource"] else detailed_meal["strYoutube"],
                            "category": detailed_meal["strCategory"],
                            "area": detailed_meal["strArea"],
                            "image": detailed_meal["strMealThumb"]
                        })

                if len(recipes) >= 6:
                    break

        if len(recipes) >= 6:
            break

    return render_template("results.html", recipes=recipes, ingredients=ingredients)


if __name__ == "__main__":
    app.run(debug=True)
