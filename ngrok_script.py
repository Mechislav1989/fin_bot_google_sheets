from pyngrok import ngrok
from dotenv import load_dotenv
import os


load_dotenv()

def tunel():
    ngrok.set_auth_token(os.environ.get("authtoken"))
    tunnel1 = ngrok.connect(8080).public_url
    ngrok_process = ngrok.get_ngrok_process()
    print(tunnel1)
    try:
        # Block until CTRL-C or some other terminating event
        ngrok_process.proc.wait()
        
    except KeyboardInterrupt:
        print(" Shutting down server.")

        ngrok.kill()
    

tun = tunel()
