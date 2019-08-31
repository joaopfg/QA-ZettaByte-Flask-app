# InferSent

*InferSent* was used as a *sentence embedding* method that provides semantic representations for English sentences. It is trained on natural language inference data and generalizes well to many different tasks.
To run the project it is necessary having the GloVe vector embedding inside a folder named *GloVe* which must be inside the *flaskr* folder. It's also necessary having the pre-trained model (*infersent1.pkl*) in a folder named *encoder* which must be inside the *flaskr* folder. To check how to get those files, please check the [original InferSent repository](https://github.com/facebookresearch/InferSent) .
  

# Tika

*Tika* was used to grab text from .pdf files. It also gives a support to many others files formats.
For more informations, see the [original Tika repository](https://github.com/chrismattmann/tika-python) .

# Running the app

You can run your application using the flask command. From the terminal, tell Flask where to find your application, then run it in development mode. Remember, you should still be in the top-level flask-tutorial directory, not the flaskr package.

Development mode shows an interactive debugger whenever a page raises an exception, and restarts the server whenever you make changes to the code. You can leave it running and just reload the browser page as you follow the tutorial.

For Linux and Mac:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

For Windows cmd, use set instead of export:

```bash
> set FLASK_APP=flaskr
> set FLASK_ENV=development
> flask run
```

For Windows PowerShell, use $env: instead of export:

```bash
> $env:FLASK_APP = "flaskr"
> $env:FLASK_ENV = "development"
> flask run
```

You’ll see output similar to this:

```bash
* Serving Flask app "flaskr"
* Environment: development
* Debug mode: on
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
* Restarting with stat
* Debugger is active!
* Debugger PIN: 855-212-761
```

# Initializing the database
The application uses a SQLite database to store books and questions. Python comes with built-in support for SQLite in the *sqlite3* module.

To initialize the database, run the *init-db* command:

```bash
$ flask init-db
```

You should see the message *Initialized the database* on the terminal.

There will now be a *flaskr.sqlite* file in the instance folder in your project.
