# food_ordering_app

This is my diploma project at University of Debrecen - Computer Science (2021)

### About the app

This is a webapplication to order food from restaurants online using Python's django Web Framework.

* General Functions:
  * User Registration
  * Restaurant registration
* User Functions:
  * View home page (Shows list of available restaurants)
  * View restaurants specific page (Shows the menu)
  * Put foods from restaurants into the user's cart.
  * Order the contents of the cart
  * View orders from the past
* Restaurant Functions:
  * Specify add modify restaurant's name and location
  * Specify add modify restaurant's menu

### Getting started

Install python virtual environment:

```bash
$ python3 -m venv env
```

Run the python virtual environment (Be aware of using `\` or `/` depending on your OS):
```bash
$ env\Scripts\activate
```

Install the following packages with the correct versions using pip:
* asgiref==3.3.1
* Django==3.1.5
* gunicorn==20.1.0
* pytz==2020.5
* six==1.15.0
* sqlparse==0.4.1
* whitenoise==5.2.0

Navigate to the `app` directory:
```bash
$ cd app
```

To get the database set up and the sample data I provide for the app run:
```bash
$ python3 manage.py migrate
```

#### IMPORTANT:
Change the email credentials in settings.py for the one you want the application to use.

Run the server (pass `runserver` to `manage.py` as a command line argument):
```bash
$ python3 manage.py runserver
```

> NOTE: The server will run at: http://127.0.0.1:8000
