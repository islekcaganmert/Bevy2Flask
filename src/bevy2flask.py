from bevyframe.widgets import *
from bevyframe import Frame as superFrame
from bevyframe import *
from bevyframe.login import *
from flask import Flask, request, Response as flaskResp
import importlib.util
import importlib
import traceback
import os

admins = {}
mime_types = {
    'html': 'text/html',
    'txt': 'text/plain',
    'jpg': 'image/jpeg',
    'png': 'image/png',
    'pdf': 'application/pdf',
    'ico': 'image/x-icon',
    'css': 'text/css',
    'json': 'application/json'
}


class Frame(superFrame):
    def run(self, host: str = '127.0.0.1', port: int = 5000, debug: bool = True, run: bool = True):
        print('BevyFrame 0.2 ⍺')
        print('Bevy2Flask enabled, handing over the server to flask...', end=' ', flush=True)
        flask_app = Flask(self.package)

        @flask_app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
        @flask_app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
        def flask_router(path):
            recv = {
                'method': request.method,
                'path': f'/{path}',
                'protocol': 'http/1.1',
                'headers': {key: value for key, value in request.headers},
                'body': request.get_data(),
                'credentials': None
            }
            try:
                recv['credentials'] = get_session(self.secret, Request(recv, self).cookies['s'])
            except KeyError:
                pass
            if recv['credentials'] is None:
                recv['credentials'] = {
                    'email': 'Guest@hereus.net',
                    'password': ''
                }
            try:
                not_in_routes = True
                if recv['path'] in self.routes:
                    not_in_routes = False
                    resp = self.routes[recv['path']]()
                for route in self.routes:
                    if not_in_routes:
                        match, variables = match_routing(route, recv['path'])
                        not_in_routes = not match
                        if not not_in_routes:
                            resp = self.routes[route](Request(recv, self), **variables)
                if not_in_routes:
                    page_script_path = f"./{recv['path']}"
                    for i in range(0, 3):
                        page_script_path = page_script_path.replace('//', '/')
                    if not os.path.isfile(page_script_path):
                        page_script_path += '/__init__.py'
                        if not os.path.isfile(page_script_path):
                            resp = self.error_handler(Request(recv, self), 404, '')
                    if os.path.isfile(page_script_path):
                        if page_script_path.endswith('.py'):
                            page_script_spec = importlib.util.spec_from_file_location(
                                os.path.splitext(os.path.basename(page_script_path))[0],
                                page_script_path
                            )
                            page_script = importlib.util.module_from_spec(page_script_spec)
                            try:
                                page_script_spec.loader.exec_module(page_script)
                                resp = getattr(page_script, recv['method'].lower())(Request(recv, self))
                            except FileNotFoundError:
                                resp = self.error_handler(Request(recv, self), 404, '')
                        else:
                            with open(page_script_path, 'rb') as f:
                                resp = Response(
                                    (f.read().decode() if page_script_path.endswith('.html') else f.read()),
                                    headers={
                                        'Content-Type': mime_types.get(
                                            page_script_path.split('.')[-1],
                                            'application/octet-stream'
                                        ),
                                        'Content-Length': len(f.read()),
                                        'Connection': 'keep-alive'
                                    }
                                )
            except Exception as e:
                resp = self.error_handler(Request(recv, self), 500, traceback.format_exc())
            if isinstance(resp, Page):
                resp.data['lang'] = ''
                resp.data['charset'] = 'utf-8'
                resp.data['viewport'] = {
                    'width': 'device-width',
                    'initial-scale': '1.0'
                }
                resp.data['keywords'] = self.keywords
                resp.data['author'] = self.developer
                resp.data['icon'] = {
                    'href': self.icon,
                    'type': mime_types[self.icon.split('.')[-1]]
                }
                if 'OpenGraph' not in resp.data:
                    resp.data['OpenGraph'] = {
                        'title': 'WebApp',
                        'description': 'BevyFrame App',
                        'image': '/Static/Banner.png',
                        'url': '',
                        'type': 'website'
                    }
                resp.style = self.style
            if not isinstance(resp, Response):
                resp = Response(resp)
            if isinstance(resp.body, Page):
                resp.body = resp.body.render()
            elif isinstance(resp.body, dict):
                resp.body = json.dumps(resp.body)
            elif isinstance(resp.body, list):
                resp.body = json.dumps(resp.body)
            resp.headers['Content-Length'] = len(resp.body.encode() if isinstance(resp.body, str) else resp.body)
            resp.headers['Set-Cookie'] = 's=' + get_session_token(self.secret, **(
                resp.credentials if resp.credentials != {} else recv['credentials']
            )) + '; '
            return flaskResp(resp.body, resp.status_code, resp.headers)

        print('DONE!')
        print()
        if run:
            flask_app.run(host=host, port=port, debug=False)
        else:
            return flask_app
        print()
        print('Server is taken over back by BevyFrame')
        print()
        print('Server was been terminated!')
        print()
