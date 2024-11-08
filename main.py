from flask import Flask, request, render_template 
import os 
import openai
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

#get the api key from the .env file and create am openai clinet 
_ = load_dotenv(find_dotenv())
client = OpenAI(api_key=os.getenv('OPEN_API_KEY'))
  
# Flask constructor
app = Flask(__name__, template_folder=os.getcwd())  

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
def get_val():
    if request.method == "POST":
       # getting input with freq = set_freq in HTML form
       width = request.form.get("width")
       height = request.form.get("height")
       prompt_result = get_completion(width, height)
       return render_template("index.html", result=prompt_result)
    return render_template("index.html")

if __name__=='__main__':
   app.run(debug=True)