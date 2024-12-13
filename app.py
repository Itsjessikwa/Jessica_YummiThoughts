from flask import Flask render_template, request, redirect, url_for, abort
import requests

#Flask application
app = Flask(__name__)

# Joplin API Configuration
JOPLIN_API_BASE_URL = "https://jessica_yummithoughts.glitch.jessica"
JOPLIN_API_TOKEN = "ba8905ebec7a304f37f3388b4941b203fa1b5d0748cb77a9f07454119b77f1e814f080e632ee892c0e50d90f63c221793a9d9de4079f6dc82b55cc5d06400256s"

# Stored recipes dictionary
recipes = {}

#This is the search function where you can search for you recipes either by ingredient or title of recipe.
def search_recipes(query):
    #This part returns the recipe information stored in the dictionary if the user search query matches. Also I included a ".lower()" so that the user can type in caps as well and still be able to get the desired returned information
    return {name: info for name, info in recipes.items() if query.lower() in name.lower() or query.lower() in info.lower()}


#This is the route that is in charge of the recipe search function/query
#This works by first getting the search query from the request.form.get
#Then searches for a recipe match
#Next rendering the search results onto the html page
@app.route("/search_recipe", methods=["POST"])
def search_recipe():
    search_query = request.form.get("search_query")
    results = {}
    if search_query:
        results = search_recipes(search_query)
    return render_template("search_results.html", results=results)

#This is the route for the home page
@app.route("/", methods=["GET"])
def home():
    # This gets the notes from the Joplin API 
    try:
        response = requests.get(
            f"{JOPLIN_API_BASE_URL}/notes",
            params={"token": JOPLIN_API_TOKEN}
        )
        # If the request fails then it raises an error
        response.raise_for_status()
        notes = response.json()
    except requests.exceptions.RequestException:
        notes = []
    return render_template("index.html", notes=notes, recipes=recipes)

# This is the route for the user to create a new recipe!
@app.route("/create_recipe", methods=["POST"])
def create_recipe():
#This part gets the recipe name and recipe info from the request.form.get
    recipe_name = request.form.get('name')
    recipe_info = request.form.get('recipe_info')
    if recipe_name and recipe_info:

#Then adding the new recipe to the dictionary
        recipes[recipe_name] = recipe_info
# This will redirect the user to another page where it will display their newly created recipe!
#IF else such as if the user did not input anything then it will redirect the user to an error message.
        return redirect(url_for('recipe_detail', recipe_name=recipe_name))
    else:
        return render_template("create_recipe.html", error="Please provide both name and info for the recipe.")

#This is the route to display the details of a certain recipe
@app.route("/recipe/<recipe_name>")
def recipe_detail(recipe_name):
#This helps to get the recipe information from the dictionary
    recipe_info = recipes.get(recipe_name)
    if recipe_info:
    #Renders the recipe details onto the html page and if not it will produce an error. 
        return render_template("recipe_detail.html", name=recipe_name, info=recipe_info)
    else:
        abort(404)

#This is the route to modify the user's recipes.
@app.route("/modify_recipe", methods=["POST"])
def modify_recipe():
#This part helps to get the recipe name and new_info through the request.form.get.
    recipe_name = request.form.get('recipe_name')
    new_info = request.form.get('new_info')
#If the recipe is found in recipes, then the recipe will equal to the new_info.
    if recipe_name in recipes and new_info:
        recipes[recipe_name] = new_info
    #Redirects the user to the home page and IF else, such as if the recipe cannot be found or is missing information, the user will get an error message.
        return redirect(url_for('home'))
    else:
        return render_template("modify_recipe.html", error="Recipe not found or missing information.")

#This is the app route for the user to delete their recipe
@app.route("/delete_recipe", methods=["POST"])
def delete_recipe():
#This gets the recipe name from the request.form.get
    recipe_name = request.form.get('recipe_name')
#If the recipe is found, then the "del" deletes it from the dictionary
    if recipe_name in recipes:
        del recipes[recipe_name]
#Returns the user back home and if the user is trying to delete a recipe that is not found then it will show an error message.
        return redirect(url_for('home'))
    else:
        return render_template("delete_recipe.html", error=f"Recipe '{recipe_name}' not found.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
