# Flask-Blog-Tutorial
A blog application in python using Flask.
Followed at this video: https://www.youtube.com/watch?v=GQcM8wdduLI&list=PL9KAMnQr-CNZ0V_RsQSIFWOKBnU8F7S3y&index=6 and https://www.youtube.com/watch?v=f_bml-MILAs&list=PL9KAMnQr-CNZ0V_RsQSIFWOKBnU8F7S3y&index=8&t=1255s

# How to run
Create a virtual environment, To do this...
navigate to the FlaskLogin Directory
In PowerShell or CMD type in: pipenv shell
This will activate the virtual environment

From there you will need to install the dependencies from the Pipfile. To do this you can type in (if the virtualenv is already activated) pipenv sync --dev

It may be the case that some of the dependencies are out of date. If certain modules which you know have been installed are not working first check that they are installed by typing in: pipenv run pip freeze

Then you might simply have to reinstall them so they are the latest versions e.g. pipenv install flask-sqlalchemy

To then run your applicaiton type:

flask --app app run (where app is the name of your python file in the route directory)

If you don't want to have to stop the server and restart it each time a change is made (Ctrl+C). Then start the application with this command instead, to put it in debug mode: flask --app example_app.py --debug run


# To NOTE
In the auth.py file on line 68 the sha256 method is passed as a parameter but in the latest version of the werkzeug module (which is imported) this has to be changed to scrypt i.e. method='scrypt'

Have used https://datatables.net/ for table layout css