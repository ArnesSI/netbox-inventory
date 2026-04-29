import re
import sys

tag = sys.argv[1]
tag_version = tag.lstrip("v")

ftxt = open("netbox_inventory/version.py", "r").read()
if m:= re.search(r"__version__\s*=\s*[\"'](\d+\.\d+\.\d+)[\"']", ftxt, re.MULTILINE):
    ver_code = m.group(1)
else:
    sys.stderr.write("Could not find version in version.py\n")
    sys.exit(1)

ttxt = open("netbox_inventory/tests/test_load.py", "r").read()
if m:= re.search(r"__version__\s*==\s*[\"'](\d+\.\d+\.\d+)[\"']", ttxt, re.MULTILINE):
    test_code = m.group(1)
else:
    sys.stderr.write("Could not find version in tests/test_load.py\n")
    sys.exit(1)

ptxt = open("pyproject.toml", "r").read()
if m:= re.search(r"version\s*=\s*[\"'](\d+\.\d+\.\d+)[\"']", ptxt, re.MULTILINE):
    proj_code = m.group(1)
else:
    sys.stderr.write("Could not find version in pyproject.toml\n")
    sys.exit(1)

print(f"       Git tag:{tag}")
print(f"    version.py: {ver_code}")
print(f"  test_load.py: {test_code}")
print(f"pyproject.toml: {proj_code}")
print("")

if not (tag_version == ver_code == test_code == proj_code):
    sys.stderr.write("Update version string in all files before release\n")
    sys.exit(1)

print("Versions OK")
