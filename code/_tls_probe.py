import ssl, socket, urllib.request, time, sys

print("Python:", sys.version.split()[0])
print("OpenSSL:", ssl.OPENSSL_VERSION)
print()

def probe(host, port=443):
    try:
        t = time.time()
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=15) as s:
            with ctx.wrap_socket(s, server_hostname=host) as ss:
                cipher = ss.cipher()
                return f"OK  ({(time.time()-t)*1000:.0f} ms, {cipher[1]} {cipher[0]})"
    except Exception as e:
        return f"FAIL: {type(e).__name__}: {e}"

for host in ["www.google.com", "github.com", "huggingface.co", "cdn-lfs.huggingface.co"]:
    print(f"  {host:32s} {probe(host)}")

print()
print("=== HEAD via urllib to huggingface.co (model file) ===")
try:
    req = urllib.request.Request("https://huggingface.co/microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224/resolve/main/open_clip_pytorch_model.bin", method="HEAD")
    r = urllib.request.urlopen(req, timeout=15)
    print(f"HTTP {r.status}, length: {r.headers.get('Content-Length')}")
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}")
