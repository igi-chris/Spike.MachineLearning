from http import HTTPStatus

from sklearn.decomposition import PCA
from flask import Flask, Response, make_response, request

from principle_component import build_components, to_json

app = Flask("ml_service")


@app.route("/")
def connection_test() -> Response:
    return make_response("Request Successful", HTTPStatus.ACCEPTED)

@app.route("/pca", methods=['POST'])
def pca() -> Response:
    data = request.json
    model = PCA()
    model.fit(data)

    pcs = build_components(model)
    resp_json = to_json(pcs, model, data)
    return make_response(resp_json, HTTPStatus.ACCEPTED)

if __name__ =='__main__':
    import sys
    # to allow debugging, deployed version will start service using WSGI server
    if sys.argv[-1].startswith('local'):  
        app.run(port=5000)
