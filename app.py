from flask import Flask, render_template, request
import requests

app = Flask(__name__)


def get_meal_details(meal_id):
    detail_url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"
    response = requests.get(detail_url, timeout=10)
    data = response.json()
    if data.get("meals"):
        return data["meals"][0]
    return None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    ingredients = request.form.get("ingredients", "")
    keyword = request.form.get("keyword", "").strip().lower()

    ingredient_list = [item.strip().lower() for item in ingredients.split(",") if item.strip()]

    meal_scores = {}

    for ingredient in ingredient_list:
        url = f"https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}"
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get("meals"):
            for meal in data["meals"]:
                meal_id = meal["idMeal"]
                meal_scores[meal_id] = meal_scores.get(meal_id, 0) + 1

    if keyword:
        keyword_url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={keyword}"
        response = requests.get(keyword_url, timeout=10)
        data = response.json()

        if data.get("meals"):
            for meal in data["meals"]:
                meal_id = meal["idMeal"]
                meal_scores[meal_id] = meal_scores.get(meal_id, 0) + 2

    recipes = []
    for meal_id, score in meal_scores.items():
        details = get_meal_details(meal_id)
        if not details:
            continue

        name = (details.get("strMeal") or "").lower()
        category = (details.get("strCategory") or "").lower()
        area = (details.get("strArea") or "").lower()
        instructions = (details.get("strInstructions") or "").lower()

        if keyword and (
            keyword in name
            or keyword in category
            or keyword in area
            or keyword in instructions
        ):
            score += 2

        recipes.append({
            "name": details.get("strMeal"),
            "link": details.get("strSource") or details.get("strYoutube") or "#",
            "category": details.get("strCategory"),
            "area": details.get("strArea"),
            "image": details.get("strMealThumb"),
            "score": score,
        })

    recipes.sort(key=lambda x: x["score"], reverse=True)

    return render_template(
        "results.html",
        recipes=recipes[:12],
        ingredients=ingredients,
        keyword=keyword,
    )


if __name__ == "__main__":
    app.run(debug=True)
