# Import the poe package, the Flask framework, the python-dotenv package and the os module
import poe
from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os

# Load the environment variables from a .env file
load_dotenv()

# Create a list of p-b cookies from the environment variables
pb_cookies = []
for i in range(1, 60): # Change 3 to the number of p-b cookies you have + 1
  pb_cookie = os.getenv(f"PBCOOKIE{i}")
  if pb_cookie:
    pb_cookies.append(pb_cookie)

# Create a function to switch to another p-b cookie
def switch_pb_cookie(pb_cookies, index):
  # Check if the index is valid and if there is another p-b cookie available in the list
  if index is not None and index < len(pb_cookies) - 1:
    # Increment the index and create a new poe.Client instance with the next p-b cookie
    index += 1
    client = poe.Client(pb_cookies[index])
    return index, client
  else:
    # Return None and None if there is no other p-b cookie available
    return None, None

# Create a Flask app and define a route for the API endpoint
app = Flask(__name__)

# Implement a rate limit using the Flask-Limiter extension
limiter = Limiter(key_func=get_remote_address, app=app, default_limits=["10 per minute"])

@app.route("/")
@limiter.limit("10 per minute")
def api():
  # Parse the query parameters from the request and validate them
  q = request.args.get("q")
  id = request.args.get("id")
  mode = request.args.get("mode")

  if not q or not id or not mode:
    return "Missing query parameters", 400

  # Use the client.send_message function to send a message to the chatbot specified by the mode parameter, and store the final response in a variable
  chatbot = {
    "normal": "normalguy1",
    "standup": "standupcom",
    "cowboy": "cowboyguy"
  }.get(mode, "beaver") # Use "a2" as the default chatbot if mode is not valid

  response = ""
  index = 0 # Initialize an index for the list of p-b cookies
  client = poe.Client(pb_cookies[index]) # Create an initial poe.Client instance with the first p-b cookie

  while True: # Use a while loop to keep trying different p-b cookies until there are none left or until there is no error
    try:
      for chunk in client.send_message(chatbot, q):
        response = chunk["text"]
      break # Break the loop if there is no error
    except Exception as e: # Catch any exception as e
      if "Daily limit reached" in str(e): # Check if the exception message contains "Daily limit reached"
        index, client = switch_pb_cookie(pb_cookies, index) # Call the switch_pb_cookie function with the list of p-b cookies and the index
        if index is None or client is None: # Check if there is no other p-b cookie available
          response = "Sorry, can't help ya right now. *pretends to chuckle* Hate to say this but I may have to pull the lever off to turn off this thing for a lil' bit. See ya later! *power turns off*" # Set the response to an apology message
          break # Break the loop
      else: # If the exception message does not contain "Daily limit reached"
        response = "*accidentaly drop a screw* Oh no, sorry kids, can't respond right now, have to get the screw. I guess, goodbye for now." # Set the response to an apology message
        break # Break the loop

  # Return the response as a plain text string with the status code 200, and print the id parameter to the console
  print(id)
  return response, 200

# Run the app on a port of my choice
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080)
