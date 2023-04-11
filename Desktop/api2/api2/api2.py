from flask import Flask, request, render_template
from bot import botresp

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    text_input = ''
    if request.method == 'POST':
        text_input = request.form.get('text_input', '')
        processed_text = process_text(text_input)
        return render_template('index.html', text_input=text_input, processed_text=processed_text)
    return render_template('index.html', text_input=text_input)

def process_text(text):
    # Do some processing with the input text
    processed_text = botresp(text) # example processing
    return processed_text

if __name__=="__main__":
    app.run(port=12000,debug=True)