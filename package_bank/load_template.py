import importlib.util
import sys

def load_from_github(url):
    import urllib.request, textwrap
    exec(textwrap.dedent(urllib.request.urlopen(url).read().decode()), globals())

# One-liner to pull the singular unified file from anywhere
load_from_github("https://raw.githubusercontent.com/yourusername/yourrepo/main/lucifer_integration_v1_standalone.py")

# Now the prior is permanently in your namespace, exactly as if you had copy-pasted it
print(tier_0_predictive_priors["lucifer_principle_v1.0"]["weight"])  # → 0.98