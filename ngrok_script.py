from pyngrok import ngrok, conf
from pyngrok.conf import PyngrokConfig
from dotenv import load_dotenv
import os


load_dotenv()

def tunel():
    conf.get_default().config_path = "/ngrok.yml"
    ngrok.set_auth_token(os.environ.get("authtoken"))
    global tunnel1
    tunnel1 = ngrok.connect(8090).public_url
    ngrok_process = ngrok.get_ngrok_process()
    print(tunnel1)
    try:
        # Block until CTRL-C or some other terminating event
        ngrok_process.proc.wait()
        
    except KeyboardInterrupt:
        print(" Shutting down server.")

        ngrok.kill()
    return tunnel1

tun = tunel()
