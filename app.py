#imports 
from flask import Flask, request, render_template 
import os 
import openai
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import requests
import base64
import pandas as pd

#function that will search throgh furniture csv and return filtered dataframe based on list of keywords 
def piece_df(csv_file, keywords):
   #read in csv file
   df = pd.read_csv(csv_file)
   #create a new dataframe that only contains the rows where any of the keywords is in the image_title column
   new_df = df[df['image_title'].str.contains('|'.join(keywords), case=False, na=False)]
   return new_df


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

#lists of key words for each piece the user could select for later suggestions and csv file
furniture_csv = 'furniture.csv'
coffee_table_keywords = ['coffee table']
side_table_keywords = ['side table', 'end table', 'accent table']
couch_keywords = ['couch', 'sofa', 'futon', 'sectional'] 
entertainment_center_keywords = ['entertainment center', 'media', 'tv stand']
rug_keywords = ['rug', 'area']
bed_keywords = ['headboard', 'bed']
shelves_keywords = ['shelves', 'bookshelves', 'bookcase']
lamp_keywords = ['lamp']
dresser_keywords = ['dresser', 'chest', 'wardrobe']
nightstand_keywords = ['nightstand']
desk_keywords = ['desk', 'desk chair']
armchair_keywords = ['armchair', 'recliner', 'loveseat', 'chair']

#check to see if there is an image in dir, remove if there is
#only want to display current image, if there is an image in the 
#folder from a previous run, delete it 
if os.path.exists(image_path):
   os.remove(image_path)

#function to save generated image for display 
def save_image(image_url):
   #download image 
   image = requests.get(image_url).content
   #write image to image_path (static/images/generated_image.jpg)
   with open(image_path, "wb") as image_file:
      image_file.write(image)

#function to generate image based on text input
def generate_image(prompt):
   if os.path.exists(image_path):
      os.remove(image_path)
   #make call to dalle3 api to generate image based on prompt 
   response = client.images.generate(
      model='dall-e-3',
      prompt = f"You will be given a description of a room. That description will include the contents of the room, colors, ambiance, and other factors of the room. Your job will be to take the role of an interior designer and based on the given description, output an image of the designed room to give the user visualization and inspiration for the room they are wanting to design. Utilize the factors given in the description and make sure to include the items given in the description and stay on theme with regards to color, ambiance, etc., Nikon D810 | ISO 64 | focal length 20mm (Voigtlander 20mm f3.5) | Aperature f/9 | Exposure Time 1/40 Sec (DRI). Here is the description of the room: {prompt}",
      size="1024x1024"
   )
   #get image url 
   image_url = response.data[0].url
   #save image
   save_image(image_url)

#function to generated image based on uploaded image input 
#use a combination of chatgpt's vision capabilities and dall-e model to generate an image
def generate_description_uploaded_input(image):
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
                  "text": "Analyze this image and provide a detailed description of the room, including the furniture, decor, colors, and any notable objects. Describe the layout, the style of the room (e.g., modern, rustic), and how the objects contribute to its functionality and ambiance. Include any inferences about how this room might be used or what it reveals about its occupants.",
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
   #extract text output from response 
   img_description = (response.choices[0].message.content)

   #after description is producted, call generate_image function to generate image using dalle-3 based on description 
   generate_image(img_description)

# A decorator used to tell the application
# which URL is associated function
@app.route('/main', methods =["GET", "POST"])
def home():
   if request.method == "POST":
      input_description = request.form.get("txtInput")
      input_img = request.form.get("imgInput")
      #dictionary that get the status of the checkbox items (checked or unchecked)
      #on = checked None = unchecked
      furniture_items = {
         "coffee_table": request.form.get("coffeeTable"),
         "side_table": request.form.get("sideTable"),
         "couch": request.form.get("couch"),
         "entertainment_center": request.form.get("entertainmentCenter"),
         "rug": request.form.get("rug"),
         "bed": request.form.get("bed"),
         "shelves": request.form.get("shelves"),
         "lamp": request.form.get("lamp"),
         "dresser": request.form.get("dresser"),
         "nightstand": request.form.get("nightstand"),
         "desk": request.form.get("desk"),
         "armchair": request.form.get("armchair")
      }
      for piece in furniture_items:
         print(furniture_items[piece])
      #if image is uploaded call uploaded_image function
      if input_img != "":
         #get uploaded image from HTML form 
         uploaded_image = request.form.get("imgInput")
         generate_description_uploaded_input(uploaded_image)
      #if no uploaded image, make call to get_image which will generate image and save it to images dir
      else:
         generate_image(input_description)
   return render_template("index.html")

if __name__=='__main__':
   app.run(debug=True)