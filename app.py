from flask import Flask, render_template

import database
import config
from routes import routes

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH
config.UPLOAD_FOLDER.mkdir(exist_ok=True)

app.register_blueprint(routes)

''' Cleanup function: To register a callback, whenever the application is torn down, call database.close_db() '''
app.teardown_appcontext(database.close_db)      

with app.app_context():
    database.init_db()

'''Error handlers'''

@app.errorhandler(404)
def page_not_found(error):
    return render_template(
         "errors/error.html",
         error_code = 404,
         error_type = "File Not Found",
         message = "The requested file could not be found."
    ), 404

@app.errorhandler(413)
def request_too_large(error):
     return render_template(
          "errors/error.html",
          error_code = 413,
          error_type = "File size too large",
          message = "The maximum upload size is 100 MB."
     ), 413

@app.errorhandler(500)
def internal_server_error(error):
     return render_template(
          "errors/error.html",
          error_code = 500,
          error_type = "Internal Server Error",
          message = "Something went wrong while processing your request."
     ), 500


if __name__ == "__main__":
    app.run(debug=True)