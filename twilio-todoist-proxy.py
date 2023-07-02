#!/usr/bin/env python
from wsgiref.simple_server import make_server
import falcon
import logging
import sys
import json
from urllib.parse import parse_qsl
from todoist_api_python.api import TodoistAPI
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="TODOGW",
    settings_files=["twilio-todoist-proxy.toml", ".twilio-todoist-proxy.toml", "/etc/twilio-todoist-proxy.toml"],
    default_env="default",
    environments=True,
    env='default',
    MERGE_ENABLED_FOR_DYNACONF=True,
)

# set up app
if settings.debug == "True":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    print("Debug enabled")
else:
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

logging.debug(settings.allowed)

api = TodoistAPI(settings.token)
app = falcon.App()

def print_stuff(req, resp):
    if not req.content_length:
        logging.debug("no content")
        return
    logging.debug(resp)
    logging.debug(req)
    logging.debug("Body:")
    body = req.stream.read(req.content_length or 0).decode('utf-8')
    logging.debug(body)
    if req.get_header('content-type') == 'application/json':
        logging.debug("body is json")
        logging.debug(json.loads(body))
    else:
        logging.debug("body not json")
        logging.debug(body)
    return

class ToDo:
    def on_post(self, request, resp):
        logging.debug("POST request")
        logging.debug(resp)
        print(request.get_header('content-type'))
        if request.method == 'POST':
            if request.get_header('content-type') == 'application/x-www-form-urlencoded':
                postdata = request.stream.read(request.content_length or 0)
                logging.debug(postdata)
                params_dict = parse_qsl(postdata)
                params = dict(params_dict)
                logging.debug(params)
                if params[b'From'].decode('ascii') in settings.allowed:
                    logging.debug(params[b'From'].decode('ascii'))
                    try:
                        try:
                            task = api.add_task(content=params[b'Body'].decode('ascii'), project_id=project_id)
                            logging.debug(task)
                        except Exception as error:
                            logging.error(error)
                        logging.info(f"body {params[b'Body'].decode('ascii')}")
                        logging.debug("worked!")
                    except:
                        logging.critical("submittion to todoist failed!")
                else:
                    logging.warning("Invalid number: %s" % params[b'From'].decode('ascii'))

class deBug:
    def on_put(self, req, resp):
        logging.debug("PUT request")
        print_stuff(req, resp)
    def on_get(self, req, resp):
        logging.debug("GET request")
        print_stuff(req, resp)
    def on_post(self, req, resp):
        logging.debug("POST request")
        print_stuff(req, resp)

todo = ToDo()
debugit = deBug()

app.add_route('/todo', todo)
app.add_route('/debug', debugit)

if __name__ == '__main__':
    global project_id
    project_id = None
    try:
        projects = api.get_projects()
        for project in projects:
            if project.name == settings.project:
                project_id = project.id
        logging.debug(f"project_id: {project_id}")
    except Exception as error:
        print(error)
    with make_server('0.0.0.0', 18080, app) as httpd:
        logging.info('Serving on port 18080...')
        httpd.serve_forever()
