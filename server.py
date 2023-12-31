from flask import Flask
from flask import render_template
from flask import Response, request, jsonify
app = Flask(__name__)

#for gpt
import os
import openai
from openai import OpenAI

import secrets
import secret_key

openai.api_key = secret_key.SECRET_KEY

#for dalle
import json
from base64 import b64decode
from pathlib import Path

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=secret_key.SECRET_KEY,
)

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

saved = {}

sample_saved = {
    "id": {
        "url": "", 
        "colors": [], 
        "shape": "", 
        "vibe": "", 
        "season":"", 
        "selected flowers":[]
    }
}

sample_form_data_1 = {
    'colors': ['oranges','neutrals'],
    'shape': 'round',
    'vibe': 'vintage',
    'extras': 'tiger lillies',
    'flowers': ['Tiger Lilies', 'Cream Roses', 'Peach Dahlias', 'Apricot Ranunculus', 'Dusty Miller', 'Beige Peonies', 'Neutral Spray Roses'],
    'flower_info': {}
}

def is_valid_flowers_dict(obj):
    # Check if obj is a dictionary
    if not isinstance(obj, dict):
        return False

    # Check if obj has exactly one key
    if len(obj) != 1:
        return False

    # Check if the key is "flowers"
    key = list(obj.keys())[0]
    if key != "flowers":
        return False

    # Check if the value associated with "flowers" is a list of strings
    value = obj[key]
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return False

    return True

def is_valid_flower_colors_dict(input_dict, flower_list):
    # Check if input_dict is a dictionary
    if not isinstance(input_dict, dict):
        return False

    # Check if input_dict has exactly four keys
    if len(input_dict) != 4:
        return False

    # Check if keys in input_dict match the flower_list
    if set(input_dict.keys()) != set(flower_list):
        return False

    # Check if values associated with keys are lists of three strings
    for flower, colors in input_dict.items():
        if not isinstance(colors, list) or len(colors) != 3 or not all(isinstance(color, str) for color in colors):
            return False

    return True

# prompt construction
def generate_bouquet_req(data):
    req = "give me a simple list of flower names to use in a "

    req = req + data['shape'] + " shaped bouquet with a color scheme of "

    for color in data['colors']:
        req = req + color + ', '

    req = req + " with a " + data['vibe']  + " theme and make sure to include " + data['extras'] + "Ensure the flowers are in season in the " + data['season'] + ". Only give names of flowers, nothing else."
    
    print(req)
    return req

def generate_bouquet_desc(data):
    desc = "realistic bouqet with "

    for flower in data['flowers']:
        desc = desc + flower['color'] + " " + flower['flower'] + ", "

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

    req = "Generate a list of 3 possible colors for each of the following flowers" + flower_list
    
    print(req)
    return req

def generate_flower_images(flowers):
    flower_images = {}
    
    i = 0
    for flower in flowers:
        print(flower)
        if (i > 3):
            break
        image = generate_images(prompt = "single  " + flower + "centered on a white background") 

        image_urls = []
        image_urls.append(image['url'])
        
        i+=1
        flower_images[flower] = image_urls

    return flower_images

def generate_flower_info():
    global form_data

    req_frag_1 = "write a two sentence blurb about the "
    req_frag_2 = "including plant type, size, use in a bouquet, what bouquet shape it typically fits, and meaning of the flower."

    for flower in form_data['flowers'][:4]:
        if not flower in form_data['flower_info'].keys():
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful floral assistant."},
                    {"role": "user", "content": req_frag_1 + flower + req_frag_2},
                    ]
                )
            
            print(response.choices[0].message.content)
            form_data['flower_info'][flower] = response.choices[0].message.content

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

        print("Generating flower selections...")
        req = generate_bouquet_req(form_data)

        valid = False
        while valid is False:
            response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": "You are a helpful floral assistant designed to output JSON in the format {'flowers':[]}."},
                {"role": "user", "content": req},
            ],
            response_format={"type": "json_object"}
            )
            response = response.choices[0].message.content
            response = json.loads(response)
            print(response)
            valid = is_valid_flowers_dict(response)

        form_data['flowers'] = response['flowers']

        print("Generating flower colors...")
        req = generate_flower_colors(form_data)

        valid = False
        while valid is False:
            response = client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    messages=[
                        {"role": "system", "content": "You are a helpful floral assistant designed to output JSON in the format {'flowername':[], ...}"},
                        {"role": "user", "content": req},
                        ],
                    response_format={ "type": "json_object" }
                    )

            response = response.choices[0].message.content
            response = json.loads(response)
            print(response)
            valid = is_valid_flower_colors_dict(response, form_data['flowers'][:4])

        form_data['flower_colors'] = response

        # Generate images for the flowers
        print("Generating flower images...")
        flower_images = generate_flower_images(form_data['flowers'])  

        form_data['flower_images'] = flower_images  # Add the flower images to the form_data
        # print(form_data['flower_images'])

        print("Generating flower info...")
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

        form_data["generations"] = [images['url']]

        # Update the image path to use the local path
        # image_path = os.path.join(IMAGE_FOLDER, f"{images['path']}.png")
        # form_data["generations"] = [image_path]

        # Create a list to store image URLs
        # form_data["generations"] = [images['url']]
        
        return jsonify(form_data)
    
@app.route('/save_img', methods=['GET', 'POST'])
def save_img():
    data = request.get_json() 

    print(data)
    print(data["form_data"])
    print(data["selected_flowers"])
    print(data['genURL'])

    if request.method == 'POST':
        generation_key = data['genURL']
        saved[generation_key] = {
            'selected_flowers': data['selected_flowers'],
            'url': data['genURL'],
            'colors': data["form_data"]['colors'],
            'shape': data["form_data"]['shape'],
            'vibe': data["form_data"]['vibe'],
            'season': data["form_data"]['season']
        }

    return jsonify({"status": "success"})

def generate_images(prompt):
    response = client.images.generate(
        model="dall-e-2",
        prompt=prompt,
        size="256x256",
        quality="standard",
        n=1,
        response_format="b64_json"
    )

    #create json file for image
    DATA_DIR = Path.cwd() / "responses"
    DATA_DIR.mkdir(exist_ok=True)
    JSON_FILE = DATA_DIR / f"{prompt[:5]}-{response.created}.json"
    with open(JSON_FILE, mode="w", encoding="utf-8") as file:
        json.dump(response, file, default=lambda x: x.__dict__)  

    #convert json image data file to png
    IMAGE_DIR = Path.cwd() / "static/generated_images" / JSON_FILE.stem

    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    with open(JSON_FILE, mode="r", encoding="utf-8") as file:
        json_data = json.load(file)

    for index, image_dict in enumerate(json_data["data"]):
        image_data = b64decode(image_dict["b64_json"])
        image_file = IMAGE_DIR / f"{JSON_FILE.stem}-{index}.png"
        with open(image_file, mode="wb") as png:
            png.write(image_data)    

    full_path_to_image = image_file.as_posix()
    url_for_flask = full_path_to_image[full_path_to_image.find('static'):]

    image_data = {
        "prompt": prompt,
        "url": url_for_flask,
    }

    return image_data

@app.route('/')
def home():
    return render_template('home2.html', data=form_data)   

@app.route('/bouquet')
def bouquet_designer():
    return render_template('bouquet.html', data=form_data)

@app.route('/saved')
def save():
    return render_template('saved.html', data=saved)


if __name__ == '__main__':
    # app.run(debug = True, port = 4000)    
    app.run(debug = True)




