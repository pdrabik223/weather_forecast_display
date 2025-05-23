import gc
import socket
from wifi_tools import connect_to_wifi


def load_html(path_to_html_file: str = "index.html") -> str:
    error_html = """<!DOCTYPE html><html><head><title>failed to load html data</title></head></html>"""

    try:
        with open(path_to_html_file, "r") as file:
            html_str = file.read()
    except:
        return error_html
    return html_str


def format_dit(target: str, replacement_dict: dict) -> str:
    for key in replacement_dict.keys():
        target = target.replace("{" + key + "}", str(replacement_dict[key]))

    return target


def error_page(cl, message: str = None, stack_trace: dict = None):

    page_str = load_html("error.html")

    if message == None:
        message = "No message"
    if stack_trace == None:
        stack_trace = "No stack trace"

    page_str = page_str.format(short_message=message, stack_trace=str(stack_trace))

    cl.send(page_str)


class App:

    def __init__(self):

        self.ip = connect_to_wifi()
        addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(addr)
        self.socket.listen(1)

        # we ignore favicon for now
        self.routes_map = {"/favicon.ico": lambda *args: None}

    def __parse_uri(self, uri: str):
        params_separator = uri.find("?")
        if params_separator == -1:
            return uri, [], {}

        path = uri[:params_separator]
        params = uri[params_separator + 1 :].split("&")

        positional_params = []
        named_parameters = {}

        for param in params:
            if param.find("=") == -1:
                positional_params.append(param)
            else:
                named_parameters[param.split("=")[0]] = param.split("=")[1]

        return path.strip(), positional_params, named_parameters

    def __redirect(self, cl):

        request = cl.recv(1024)
        begin = str(request).find("GET")
        referer_str = str(request)[begin:].split("\\n")[0]
        referer_str = referer_str[3:-10]

        route_str = referer_str.strip()
        path, positional_params, named_parameters = self.__parse_uri(route_str)

        if path not in self.routes_map:
            print(f"page: {path} is not in routes_map")
            error_page(cl, f"404 page: {path} is not in routes_map")
            return

        try:
            self.routes_map[path](cl, positional_params, named_parameters)
        except KeyboardInterrupt as err:
            print("KeyboardInterrupt error appeared")
            raise err
        except Exception as err:
            error_page(cl, str(err))
            raise err
            print(err)

    def main_loop(self):
        print(f"listening on: http://{self.ip}")

        while True:
            try:
                cl, _ = self.socket.accept()
                self.__redirect(cl)

                cl.close()
            except OSError as e:
                cl.close()
                print("connection closed")
            gc.collect()

    def register_endpoint(self, path: str, func: function):
        self.routes_map[path] = func
