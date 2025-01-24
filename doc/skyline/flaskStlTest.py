# A Simple flask example to integrate the github skyline stl file in a web page.
from flask import Flask
app = Flask(__name__)

# For example your github stl file is at:
#https://github.com/LiuYuancheng/LiuYuancheng/blob/main/doc/skyline/LiuYuancheng-2024-github-skyline.stl
# Then you need to change your embed URL to
stl_link = 'https://embed.github.com/view/3d/LiuYuancheng/LiuYuancheng/main/doc/skyline/LiuYuancheng-2024-github-skyline.stl'
# The size of the skyline 
module_size='?height=600&width=800'
stl_link += module_size

HTML_CONTENT = """<!doctype html>
<html>
    <head>
        <title> Web example to show the skyline stl file </title>
    </head>
    <body>
        <h1> Web example to show the skyline stl file </h1>
        <script src="%s"></script>
        <hr>
    <body>
</html>
""" %str(stl_link)

@app.route('/')
def index():
    return HTML_CONTENT

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)