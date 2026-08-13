[1mdiff --git a/app.py b/app.py[m
[1mindex 7e6cb5d..e8ebfa8 100644[m
[1m--- a/app.py[m
[1m+++ b/app.py[m
[36m@@ -8,6 +8,33 @@[m [mfrom datetime import datetime[m
 app = Flask(__name__)[m
 app.config["MAX_CONTENT_LENGTH"] = 100*1024*1024[m
 [m
[32m+[m[32m@app.errorhandler(404)[m
[32m+[m[32mdef page_not_found(error):[m
[32m+[m[32m    return render_template([m
[32m+[m[32m         "errors/error.html",[m
[32m+[m[32m         error_code = 404,[m
[32m+[m[32m         error_type = "File Not Found",[m
[32m+[m[32m         message = "The requested file could not be found."[m
[32m+[m[32m    ), 404[m
[32m+[m
[32m+[m[32m@app.errorhandler(413)[m
[32m+[m[32mdef request_too_large(error):[m
[32m+[m[32m     return render_template([m
[32m+[m[32m          "errors/error.html",[m
[32m+[m[32m          error_code = 413,[m
[32m+[m[32m          error_type = "File size too large",[m
[32m+[m[32m          message = "The maximum upload size is 100 MB."[m
[32m+[m[32m     ), 413[m
[32m+[m
[32m+[m[32m@app.errorhandler(500)[m
[32m+[m[32mdef internal_server_error(error):[m
[32m+[m[32m     return render_template([m
[32m+[m[32m          "errors/error.html",[m
[32m+[m[32m          error_code = 500,[m
[32m+[m[32m          error_type = "Internal Server Error",[m
[32m+[m[32m          message = "Something went wrong while processing your request."[m
[32m+[m[32m     ), 500[m
[32m+[m
 UPLOAD_FOLDER = Path("uploads")[m
 UPLOAD_FOLDER.mkdir(exist_ok=True)[m
 [m
[36m@@ -83,22 +110,11 @@[m [mdef download(stored_filename):[m
 [m
     file = database.get_file(stored_filename)[m
     if file is None:[m
[31m-        return render_template([m
[31m-            "errors/error.html",[m
[31m-            error_code=404,[m
[31m-            error_type="Upload Failed, File Not Found",[m
[31m-            message=f"The requested file, {stored_filename}, was not found in the Database."[m
[31m-        ), 404[m
[32m+[m[32m        abort(404)[m
 [m
     destination = UPLOAD_FOLDER / file["stored_filename"][m
     if not destination.is_file():[m
[31m-            return render_template([m
[31m-                "errors/error.html",[m
[31m-                error_code=404,[m
[31m-                error_type="File Not Found",[m
[31m-                message=f"The requested file, {stored_filename}, was not found in the system."[m
[31m-            ), 404[m
[31m-[m
[32m+[m[32m            abort(404)[m
 [m
     return send_file(destination,[m
                      as_attachment=True,[m
[36m@@ -110,33 +126,18 @@[m [mdef delete(stored_filename):[m
 [m
     file = database.get_file(stored_filename)[m
     if file is None:[m
[31m-            return render_template([m
[31m-                "errors/error.html",[m
[31m-                error_code=404,[m
[31m-                error_type="Deletion Failed",[m
[31m-                message=f"The requested file, {stored_filename}, was not found in the system."[m
[31m-            ), 404[m
[32m+[m[32m            abort(404)[m
 [m
     [m
     destination = UPLOAD_FOLDER / file["stored_filename"][m
     if not destination.is_file():[m
[31m-            return render_template([m
[31m-                "errors/error.html",[m
[31m-                error_code=404,[m
[31m-                error_type="Deletion failed, destination invalid",[m
[31m-                message=f"The requested file, {stored_filename}, was not found in the system."[m
[31m-            ), 404[m
[32m+[m[32m            abort(404)[m
 [m
     try:[m
         destination.unlink()[m
         database.delete_file(stored_filename)[m
     except Exception:[m
[31m-            return render_template([m
[31m-                "errors/error.html",[m
[31m-                error_code=500  ,[m
[31m-                error_type="Some Error Occured",[m
[31m-                message=f"The requested file, {stored_filename}, could not be deleted"[m
[31m-            ), 500[m
[32m+[m[32m            abort(500)[m
 [m
     [m
     return render_template("deleted.html", f = file["original_filename"])[m
[1mdiff --git a/templates/errors/error.html b/templates/errors/error.html[m
[1mindex 22cb05a..e045816 100644[m
[1m--- a/templates/errors/error.html[m
[1m+++ b/templates/errors/error.html[m
[36m@@ -3,7 +3,7 @@[m
 <head>[m
     <meta charset="UTF-8">[m
     <meta name="viewport" content="width=device-width, initial-scale=1.0">[m
[31m-    <title>FileShare - {{error}}</title>[m
[32m+[m[32m    <title>FileShare - {{error_code}}</title>[m
     <link rel="stylesheet" href="{{ url_for('static', filename = 'css/error.css') }}">[m
 </head>[m
 <body>[m
