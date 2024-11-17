from flask import Flask, request, render_template 
import os 
import openai
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import requests
import base64

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

def save_image(image_url):
   #download image 
   image = requests.get(image_url).content
   #write image to image_path (static/images/generated_image.jpg)
   with open(image_path, "wb") as image_file:
      image_file.write(image)

#function to generate image based on text input
def generate_image_text_input(num):
   if os.path.exists(image_path):
      os.remove(image_path)
   #make call to dalle3 api to generate image based on prompt 
   response = client.images.generate(
      model='dall-e-2',
      prompt = f"Please create a photorealistic image of {num} trees in a field with green grass and rolling hills. Do not add any extra features to the image, I want you to follow this prompt directly and depict only what is described in the prompt.",
      size="512x512"
   )
   #get image url 
   image_url = response.data[0].url
   #save image
   save_image(image_url)

#function to generated image based on uploaded image input 
#use a combination of chatgpt's vision capabilities and dall-e model to generate an image
def generate_image_uploaded_input(image):
   #encode image 
   with open(image, "rb") as image_file:
      b64_image = base64.b64encode(image_file.read()).decode('utf-8')
   #make call to openai api with decoded image and prompt as input 
   response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
         {
            "role": "user",
            "content": [
               {
                  "type": "text",
                  "text": "What is in this image?",
               },
               {
                  "type": "image_url",
                  "image_url": {
                     "url": f"data:image/jpeg;base64,{b64_image}"
                  },
               },
            ],
         },
      ],
   )
   return (response.choices[0].message.content)

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
      input_img = request.form.get("imgInput")
      #if image is uploaded call uploaded_image function
      if input_img is not None:
         #get uploaded image from HTML form 
         uploaded_image = request.form.get("imgInput")
         #output is description of input image 
         img_descriptopn = generate_image_uploaded_input(uploaded_image)

         return render_template("index.html", description=img_descriptopn)
      #if no uploaded image, make call to get_image which will generate image and save it to images dir
      else:
         generate_image_text_input(width)
   return render_template("index.html")

if __name__=='__main__':
   app.run(debug=True)