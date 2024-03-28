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

# To run on mac
python app.py


# To NOTE
In the auth.py file on line 68 the sha256 method is passed as a parameter but in the latest version of the werkzeug module (which is imported) this has to be changed to scrypt i.e. method='scrypt'

Have used https://datatables.net/ for table layout css

# CSRF Form issues
<!-- If there are any CSRF issues before you do anything, try deleteing this line of code in __init__.py: -->
    csrf = CSRFProtect(app)
Then put it back in.

If you have created a Flask-WTF Form then this needs to be put in the form tag: 
<!-- <form method="POST">
  {{ form.csrf_token }}
</form> -->
If there is no Flask-WTF Form created for the form then you put this in the form tag:
<!-- <form method="POST">
  {{ csrf_token() }}
</form> -->


# Where to get icons:
https://fontawesome.com/search
Then make sure taht you select the version I am using: 5.15.4

# How to Merge Branches on Git
Open a Pull Request (PR):

On GitHub, navigate to your repository and go to the "Pull Requests" tab. Click on "New Pull Request."
Choose your "feature-branch" as the branch you want to merge from and select the main branch as the target branch.
Review and Discuss:

In the PR, you can review the changes, discuss them with collaborators, and ensure everything is in order before merging.
Merge the PR:

If the changes are approved and the branch is ready to merge, you can click the "Merge" button on the PR. This will merge your "feature-branch" into the main branch.
Confirm the Merge:

GitHub will ask you to confirm the merge. You can add a commit message to describe the merge if needed.
Merge Conflict Resolution (if applicable):

If there are conflicts between your branch and the main branch, you'll need to resolve them. This might involve manually editing the affected files to combine changes.
Complete the Merge:

Once conflicts are resolved (if any), complete the merge, and your changes from the "feature-branch" are now part of the main branch.

On GitHub you can then delete the branch if you want

>> You will then need to go back into VSCode, resolve any staged files i.e. remove them. Stop the Flask application running (won't work otherwise) then click on the button to pull the changes.

>> MAke sure in VS Code that you are then working on the main branch again