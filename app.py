from http import HTTPStatus
import os
import joblib

from flask import Flask, Response, make_response, render_template

from literals import models_dir
from app_pca import pca_blueprint
from common.model_register import register_model

# TODO: Consider error handling (see https://flask.palletsprojects.com/en/2.0.x/errorhandling/)
#       Would be preferable to pass error details back to pigi, not just 500
#       * Catch warnings (https://stackoverflow.com/a/5645133/2012446)
#         e.g. sklearn warning (https://github.com/Prosserc/python_notebooks/blob/master/learning/sklearn/ICA.ipynb)

app = Flask("ml_service")
app.register_blueprint(pca_blueprint)


@app.route("/")
def connection_test() -> Response:
    return make_response("Request Successful", HTTPStatus.ACCEPTED)




if __name__ =='__main__':
    import sys
    # to allow debugging, deployed version will start service using WSGI server
    if sys.argv[-1].startswith('local'):  
        # load test case into memory (tmp)
        test_ref = 'keep_test_case'
        test_model_path = os.path.join(models_dir, f'pca_{test_ref}.joblib')
        if os.path.exists(test_model_path):
            model = joblib.load(test_model_path)
            register_model(model, as_ref=test_ref)

        # start web server
        app.run(port=5000)
