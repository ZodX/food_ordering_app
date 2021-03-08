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
$ python -m venv env
```

Run the python virtual environment (Be aware of using `\` or `/` depending on your OS):
```bash
$ env\Scripts\activate
```

Navigate to the `app` directory:
```bash
$ cd app
```

Run the server (pass `runserver` to `manage.py` as a command line argument):
```bash
$ python manage.py runserver
```

> NOTE: The server will run at: http://127.0.0.1:8000
