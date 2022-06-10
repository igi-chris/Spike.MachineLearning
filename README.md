# IGI.MachineLearning

Note: This is intended for experimentation / proof of concept work, not for production use.

Experiment with machine learning models and expose machine learning models via a web service.


------------------------

# Local Web Service via packaged exe

Originally implemented with [IGI.DataServices](https://github.com/IGILtd/IGI.DataServices/tree/local_runner) to plug file transformation into p:IGI+ / Transform, but the same principle of wrapping a python env, libraries and project into an executable that starts a local web service could be used for the machine learning project if required (if clients are concerned about sending data).

## Build local runner exe

Use auto_py_to_exe or if using pyinstaller from cmd line run the command below (under creating the exe sub heading). Note: the local python evnironment used when creating the exe will determine which python version and which libraries are bundled with this code into the exe.

This should be run from a virtual environment to ensure that only libraries required for this project are included.

### Setting up a virtual environment

Install Virtual env if you don't already have it:

`pip install virualenv`

Create an environment e.g. from the solution root, to create the virtual env in a .env subsir (ignored by github):

`python -m venv .venv`

Activate the virual env:

`.\.venv\Scripts\activate` (you should see an indication in your shell that you are now in the venv)

Install all libraries required for the project:

`pip install -r .\requirements.txt`

Install pyinstaller library (used to make the exe) - install in this venv even if you have it in your main environment (otherwise you main env will be used to create the exe):

`pip install pyinstaller` to confirm that you will use the version for ths env enter the powershell comand `Get-Command pyinstaller` and you will see the source path used.

Install a prod http server (waitress) - similar to gunicorn, but works on windows. If this step is skipped it will revert to the builtin flask wsgi server - which works, but is intended for dev/debugging not production. This is not listed in the requirements.txt as it is not useful for all use cases of this codebase.

`pip install waitress`

To deactivate the virtual env (after running the command to create the exe below) use:

`deactivate`

### Creating the exe

```
pyinstaller --noconfirm --onefile --console --icon "D:/code/projects/IGI.MachineLearning/pigipy_128.ico" --name "pigipy"  "D:/code/projects/IGI.DataServices/local_runner.py"
```

change `--console` to `--windowed` if you don't want the app to bring up a console window (i.e. to hide).

Running this command writes the output exe to ./dist by default.

-------------------------


## Example vscode config (for local run)

launch config for ${workspaceRoot}/.vscode/launch.json:
```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Flask debug",
            "type": "python",
            "request": "launch",
            "stopOnEntry": false,
            // need to add app.run(port=5000) to file for this to work - 
            // allows debugging / break points etc in vscode
            "program": "${workspaceRoot}/app.py", 
            "env": {
                "FLASK_APP": "${workspaceRoot}/app.py",
            },
            "args": [
                "local debug",
            ],
            "envFile": "${workspaceFolder}/.env",
            "redirectOutput": true,
            "jinja": true
        },
    ]
}
```