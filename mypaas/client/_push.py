import os
import io
import zipfile
from urllib.parse import quote
import requests

from ._keys import get_private_key
from ..utils import generate_uid
from ..utils import deploy_config


def push(domain, dockerfile):
    """Push the given dockerfile (or directory containing a Dockerfile)
    to your PaaS, where it will be deployed as an app/service.
    """
    config = deploy_config(dockerfile)
    if domain.lower().startswith(("https://", "http://")):
        domain = domain.split("//", 1)[-1]
    base_url = "https://" + domain.rstrip("/") + "/daemon"

    dockerfile = config["dockerfile"]
    directory = config["directory"]

    # Get the client's private key, used to sign the payload
    private_key = get_private_key()

    # Get the server's time.
    # The verify=True checks the cert (default True, but let's be explicit).
    r = requests.get(base_url + "/time", verify=True)
    if r.status_code != 200:
        raise RuntimeError(f"Could not get server time: {r.text}. Is the server daemon running?")
    server_time = int(r.text)

    # Zip it up
    print("✔ Zipping up ...")
    f = io.BytesIO()
    with zipfile.ZipFile(f, "w") as zf:
        for root, dirs, files in os.walk(directory):
            root_parts = root.replace("\\", "/").split("/")
            if any(x in root_parts for x in config["ignore"]):
                continue
            for fname in files:
                filename = os.path.join(root, fname)
                fname_in_zip = os.path.relpath(filename, directory)
                if fname_in_zip != "Dockerfile":
                    zf.write(filename, fname_in_zip)
        zf.write(dockerfile, "Dockerfile")  # the deploy will simply use "Dockerfile"
    payload = f.getvalue()
    fileSize = f.getbuffer().nbytes
    print(f"✔ Deploy file size is {fileSize / 2**20:.2f} MiB.")
    # Compose a nice little token, and a signature for it that can only be
    # produced with the private key. The public key can verify this signature
    # to confirm that we have the private key.
    fingerprint = private_key.get_id()
    token = str(server_time) + "-" + generate_uid()
    sig1 = private_key.sign(token.encode())
    sig2 = private_key.sign(payload)

    # POST to the deploy server
    url = base_url + f"/push?id={fingerprint}&token={token}"
    url += f"&sig1={quote(sig1)}&sig2={quote(sig2)}"
    print(f"✔ Pushing ...")
    r = requests.post(url, data=payload, stream=True, verify=True)
    if r.status_code != 200:
        raise RuntimeError("Push failed: " + r.text)
    else:
        for line in r.iter_lines():
            if isinstance(line, bytes):
                line = line.decode(errors="ignore")
            print(line)
