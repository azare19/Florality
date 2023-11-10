from flask import Flask
from flask import render_template
from flask import Response, request, jsonify
app = Flask(__name__)


#for gpt
import os
import openai

import secrets
import secret_key

openai.api_key = secret_key.SECRET_KEY

#for dalle
import json
from base64 import b64decode
from pathlib import Path

# client = OpenAI(
#     # defaults to os.environ.get("OPENAI_API_KEY")
#     api_key=secret_key.SECRET_KEY,
# )

# data
form_data = {
    'colors':[],
    'shape': "",
    'vibe': "",
    'season': "",
    'extras': "",
    'flowers':[],
    'flower_images': [],
    'flower_colors': {},
    'generations': [],
    'flower_info': {}
}

# INIT with example data
sample_form_data_1 = {
    'colors': ['oranges','neutrals'],
    'shape': 'round',
    'vibe': 'vintage',
    'extras': 'tiger lillies',
    'flowers': ['Tiger Lilies', 'Cream Roses', 'Peach Dahlias', 'Apricot Ranunculus', 'Dusty Miller', 'Beige Peonies', 'Neutral Spray Roses'],
    'flower_info': {}
}

# prompt construction
def generate_bouquet_req(data):
    req = "give me a simple list of flowers to use in a "

    req = req + data['shape'] + " shaped bouquet with a color scheme of "

    for color in data['colors']:
        req = req + color + ', '

    req = req + " with a " + data['vibe']  + " theme and make sure to include " + data['extras'] + " in the following format flower1, flower2, flower3, etc. with no other text. Ensure the flowers are in season in the " + data['season'] 
    
    print(req)
    return req

def generate_bouquet_desc(data):
    desc = "realistic bouqet with "

    for flower in data['flowers']:
        desc = desc + flower['color'] + flower['flower'] + ", "

    desc = desc + "in a " + data['shape'] + " shape with a " + data['vibe'] + " theme"

    print(desc)
    return desc

def generate_flower_colors(data):

    color_scheme = ''
    for color in data['colors']:
        color_scheme = color_scheme + ", " + color

    flower_list = ''
    i = 0
    for flower in data['flowers']:
        flower_list = flower_list + ', ' + flower
        i+=1
        if i == 4: break

    req = "Generate a list of 12 possible colors for the following flowers" + flower_list + " in the following format : " \
            + "flower1, color1, color2, color3, flower2, color4, color5, color6, flower3, color7, color8, color9, flower4, color10, color11, color12 " \
            + "Try to follow a " + color_scheme + " color scheme. However, if that flower does not come in that color only suggest colors the flower exists in. Make sure you follow the format exactly."
    
    print(req)
    return req

def generate_flower_images(flowers):
    flower_images = {}
    max_no = 5
    i = 0
    for flower in flowers:
        if (i > 3):
            break
        images = generate_images(prompt = "single stem of  " + flower + "with white background") 

         # Create a list to store image URLs
        image_urls = []

        for image in images:
            # Store the URL of each generated image

            image_urls.append(image['url'])
        
        i+=1
        flower_images[flower] = image_urls

    return flower_images

def generate_flower_info():
    global form_data

    req_frag_1 = "write a paragraph about the "
    req_frag_2 = "including plant type, size, typical flower colors, foliage color, use in a bouquet, what bouquet shape it typically fits, and meaning of the flower."

    for flower in form_data['flowers']:
        if not flower in form_data['flower_info'].keys():
            response = openai.Completion.create(engine="text-davinci-003", prompt=req_frag_1 + flower + req_frag_2, max_tokens=256)["choices"][0]["text"]
            form_data['flower_info'][flower] = response

@app.route('/submit_form', methods=['GET', 'POST'])
def submit_form():
    global form_data
    data = request.get_json()  

    if request.method == 'POST':

        form_data['colors'] = data['colors']
        form_data['shape'] = data['shape']
        form_data['vibe'] = data['vibe']
        form_data['season'] = data['season']
        form_data['extras'] = data['extras']

        req = generate_bouquet_req(form_data)

        response = openai.Completion.create(engine="text-davinci-003", prompt=req, max_tokens=256)["choices"][0]["text"]

        #response = 'Sunflower, Marigold, Chrysanthemum, Button Pompom, Statice, Solidago'

        print(response)

        flowers = list(response.split(','))
        flowers = list([flower.strip() for flower in response.split(',')])[:4]

        form_data['flowers'] = flowers

        req = generate_flower_colors(form_data)
        response = openai.Completion.create(engine="text-davinci-003", prompt=req, max_tokens=256)["choices"][0]["text"]
        print(response)

        flower_colors = list([token.strip() for token in response.split(',')])
        form_data['flower_colors'][flower_colors[0]] = flower_colors[1:4]
        form_data['flower_colors'][flower_colors[4]] = flower_colors[5:8]
        form_data['flower_colors'][flower_colors[8]] = flower_colors[9:12]
        form_data['flower_colors'][flower_colors[12]] = flower_colors[13:]

        print(form_data['flower_colors'])

        # Generate images for the flowers
        flower_images = generate_flower_images(flowers)  # Implement this function
        '''flower_images = {'Sunflower':'/static/sunflower.jpg',
                         ' Marigold': '/static/marigold.jpg', 
                         ' Chrysanthemum': '/static/chrys.jpg', 
                         ' Button Pompom': '/static/button.jpg', 
                         ' Statice': '/static/statice.jpeg'}'''

        form_data['flower_images'] = flower_images  # Add the flower images to the form_data

        generate_flower_info() # Generate flower information
        
        return jsonify(form_data)
    
@app.route('/req_img', methods=['GET', 'POST'])
def req_img():
    global form_data
    data = request.get_json() 
    copy = form_data

    if request.method == 'POST':

        selected_flowers = data['selected_flowers']

        copy['flowers'] = selected_flowers

        desc = generate_bouquet_desc(copy)

        images = generate_images(desc)

         # Create a list to store image URLs
        image_urls = []

        for image in images:
            # Store the URL of each generated image
            image_urls.append(image['url'])

        # Update form_data with the first image URL
        form_data["generations"] = image_urls  # Get only the first image URL'''

        #form_data["generations"] = ['static/generated_images/reali-1694574007/reali-1694574007-0.png']
        
        return jsonify(form_data)

def generate_images(prompt):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="256x256",
        response_format="b64_json",
    )

    #create json file for image
    DATA_DIR = Path.cwd() / "responses"
    DATA_DIR.mkdir(exist_ok=True)
    JSON_FILE = DATA_DIR / f"{prompt[:5]}-{response['created']}.json"
    with open(JSON_FILE, mode="w", encoding="utf-8") as file:
        json.dump(response, file)  


    #convert json image data file to png
    IMAGE_DIR = Path.cwd() / "static/generated_images" / JSON_FILE.stem

    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    with open(JSON_FILE, mode="r", encoding="utf-8") as file:
        response = json.load(file)

    for index, image_dict in enumerate(response["data"]):
        image_data = b64decode(image_dict["b64_json"])
        image_file = IMAGE_DIR / f"{JSON_FILE.stem}-{index}.png"
        with open(image_file, mode="wb") as png:
            png.write(image_data)    

    full_path_to_image = image_file.as_posix()
    url_for_flask = full_path_to_image[full_path_to_image.find('static'):]

    print("url_for_flask")
    print(url_for_flask)

    images = [
        {
            "prompt": prompt,
            "url": url_for_flask, #image_file.as_posix(),
        }
    ]
    print(url_for_flask)
    return images



@app.route('/')
def home():
    # you can pass in an existing article or a blank one.
    return render_template('home.html', data=form_data)   


if __name__ == '__main__':
    # app.run(debug = True, port = 4000)    
    app.run(debug = True)




