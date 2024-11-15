from flask import Flask, request, render_template 
import os 
import openai
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import requests

#get the api key from the .env file and create am openai clinet 
_ = load_dotenv(find_dotenv())
client = OpenAI(api_key=os.getenv('OPEN_API_KEY'))
  
# Flask constructor
app = Flask(__name__, template_folder=os.getcwd())  

#variables to store generated images 
image_dir_name = "static/images"
image_name = "generated_image.jpg"
image_dir = os.path.join(os.curdir, image_dir_name)
#save image path
image_path = os.path.join(image_dir, image_name)
#if directory does not exist, make one 
if not os.path.isdir(image_dir):
   os.mkdir(image_dir)

#check to see if there is an image in dir, remove if there is
#only want to display current image, if there is an image in the 
#folder from a previous run, delete it 
if os.path.exists(image_path):
   os.remove(image_path)

#function that uses the dalle 3 model for image generation 
def get_image(num, model='dall-e-2'):
   #make call to dalle3 api to generate image based on prompt 
   response = client.images.generate(
      model=model,
      prompt = f"Please create a photorealistic image of {num} trees in a field with green grass and rolling hills. Do not add any extra features to the image, I want you to follow this prompt directly and depict only what is described in the prompt."
   )
   #get image url 
   image_url = response.data[0].url
   #download image 
   image = requests.get(image_url).content
   #write image to image_path
   with open(image_path, "wb") as image_file:
      image_file.write(image)
   

#we will define a function to get teh completion from a given prompt 
def get_completion(num1, num2, model='gpt-4o-mini'):
   prompt = f"Please add the two following values: {num1} and {num2}"
   messages = [{"role": "user", "content": prompt}]
   response = client.chat.completions.create(
      model=model,
      messages=messages,
      temperature=0, # this is the degree of randomness of the model's output
   )
   return response.choices[0].message.content
  
# A decorator used to tell the application
# which URL is associated function
@app.route('/main', methods =["GET", "POST"])
def home():
   if request.method == "POST":
      width = request.form.get("width")
      height = request.form.get("height")
      print(f"Width: {width} \n Height: {height}")
      #make call to get_image which will generate image and save it to images dir
      get_image(width)
   return render_template("index.html")

if __name__=='__main__':
   app.run(debug=True)