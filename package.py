#!/usr/bin/env python3
#
# package.py
#
# Simple manifest-based archiver
#
# Author: Sreepathi Pai
#
import argparse
import json
import os
import glob
import sys
import zipfile
import platform
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import cryptography
import codecs
from cryptography.hazmat.backends import default_backend

TYPE_PRIMARY = "primary"
TYPE_SECONDARY = "secondary"
VALID_TYPES = set([TYPE_PRIMARY, TYPE_SECONDARY])

SET_IN = "in"
SET_OUT = "out"

class Manifest(object):
    def __init__(self, mf):
        self.path = os.path.dirname(mf)
        self.mf = mf
        self.mt = "primary" # other is secondary
        self.name = None
        self.files = {}
        self.user_manifest = False
        self.version = 1
        self.manifest = self.read()

    def set_manifest_type(self, mt):
        assert mt in VALID_TYPES
        self.mt = mt

    def get_manifest_type(self):
        return self.mt

    def set_user_manifest(self, allow):
        self.user_manifest = allow
        if allow: self.version = 2

    def _normalize_contents(self):
        out = f"{self.version}:{self.mt}\n"

        if self.version == 2:
            out = out + f"{'um:T' if self.user_manifest else 'um:F'}\n"

        sn = sorted(self.get_sets())
        out = out + ",".join(sn) + "\n"

        for s in sn:
            fn = sorted(self.get_files(s))
            out = out + ",".join(fn) + "\n"

        return out.encode('utf-8')

    def add_private_key(self, private_key):
        self.private_key = private_key

    def add_public_key(self, public_key):
        self.public_key = public_key

    def add_signature(self):
        # should really do json signing
        if hasattr(self, 'private_key'):
            data = self._normalize_contents()
            signature = self.private_key.sign(data)
            self.signature = signature
            return True
        else:
            return False

    def check_signature(self):
        data = self._normalize_contents()
        try:
            self.public_key.verify(self.signature, data)
            return True
        except cryptography.exceptions.InvalidSignature:
            return False

    def add_file(self, s, f):
        if s not in self.files:
            self.files[s] = set()

        self.files[s].add(f)

    def remove_file(self, s, f):
        self.files[s].remove(f)

    def get_files(self, s):
        if s not in self.files:
            return []

        return self.files[s]

    def get_sets(self):
        return self.files.keys()

    def read(self):
        self.mt = TYPE_PRIMARY
        self.files = {}

        with open(self.mf, "rb") as f:
            data = f.read().decode('utf-8')
            if len(data) == 0:
                data = "{}"
                return True

        j = json.loads(data)

        if j['version'] in (1, 2):
            self.version = j['version']
            self.set_manifest_type(j['type'])

            for s in j['sets']:
                for f in j['sets'][s]:
                    self.add_file(s, f)

            if 'name' in j:
                self.name = j['name']

            if self.version == 2 and 'user_manifest' in j:
                self.set_user_manifest(j['user_manifest'])

            if 'pubkey' in j:
                try:
                    pubkey = serialization.load_pem_public_key(j['pubkey'].encode('utf-8'),
                                                               backend=default_backend())
                    self.add_public_key(pubkey)
                except Exception as e:
                    print("ERROR: Could not load public key: {e}.")
                    return False

            if 'signature' in j:
                self.signature = codecs.decode(j['signature'].encode('utf-8'), 'hex_codec')

                if not self.check_signature():
                    print(f"ERROR: Signature check on file {self.mf} failed. Contents appear to have been modified.")
                    return False

            return True
        else:
            print(f"ERROR: Don't know how to read manifest version: {j['version']}", file=sys.stderr)
            return False

    def to_json(self):
        out = {'type': self.get_manifest_type(), 'version': self.version,
               'sets': {}}

        if self.version == 2 and self.user_manifest:
            out['user_manifest'] = self.user_manifest

        if self.name is not None:
            out['name'] = self.name

        for s in self.get_sets():
            out['sets'][s] = list(self.get_files(s))

        if self.add_signature():
            out['signature'] = codecs.encode(self.signature, 'hex_codec').decode('utf-8')
            assert self.public_key is not None

            out['pubkey'] = self.public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                                         format=serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8')

        return json.dumps(out)

    def write(self):
        out = self.to_json()
        with open(self.mf, "w") as f:
            f.write(out)

    def sanitize(self):
        remove = [s for s in self.get_sets() if s[:1] == "_"]
        for r in remove:
            del self.files[r]

    def __str__(self):
        out = []
        for s in sorted(self.get_sets()):
            out.append(f"    {s}:\n\t" + "\n\t".join([x for x in self.get_files(s)]))

        set_files = "\n\n".join(out)
        n = self.name if self.name else "no-name"
        v = self.version
        return f"{self.mf}: {self.get_manifest_type()} [{n}] v{v}\n{set_files}"

def get_manifests():
    return glob.glob("**/MANIFEST.json", recursive = True)

def get_manifest_contents(mf):
    mr = Manifest(mf)
    if not mr.manifest:
        print(f"Failed to read {f} when sanitizing contents")
        sys.exit(2)

    if hasattr(mr, 'public_key'):
        private_keyfile = os.path.join(os.path.dirname(mf), 'Manifest.key')
        if os.path.exists(private_keyfile):
            with open(private_keyfile, 'rb') as f:
                x = f.read()
                k = serialization.load_pem_private_key(x, None, backend=default_backend())
                mr.add_private_key(k)
        else:
            print(f"Private key {private_keyfile} does not exist")
            sys.exit(3)

    mr.sanitize()
    json = mr.to_json()
    return json

def read_user_manifest(usrmanifest):
    if not os.path.exists(usrmanifest):
        return []

    out = []
    with open(usrmanifest, 'r') as f:
        for l in f:
            ls = l.strip()
            if not ls: continue

            if os.path.exists(ls):
                print(f"Adding {ls} from user-specified {usrmanifest}")
                out.append(ls)
            else:
                print(f"ERROR: {ls} specified in {usrmanifest}, but does not exist.", file=sys.stderr)
                return None

    return out

def package(manifests, sets, output):
    files = []
    name = None
    manifests_to_include = set()
    allow_user_manifest = False

    for m in manifests:
        # pick a name from the first primary MANIFEST
        if not name and m.name and m.mt == TYPE_PRIMARY:
            name = m.name

        if m.mt == TYPE_PRIMARY:
            allow_user_manifest = m.user_manifest

        include_manifest = False
        for s in sets:
            sf = m.get_files(s)
            if len(sf):
                files.extend([os.path.join(m.path, f) for f in sf])
                include_manifest = True

        if include_manifest or 'out' in m.get_sets() or m.mt == TYPE_PRIMARY:
            manifests_to_include.add(m)

    if allow_user_manifest:
        umfiles = read_user_manifest('manifest')
        if umfiles is None:
            return 0
        else:
            files.extend(umfiles)

    if len(files) == 0:
        print(f"ERROR: No files from set(s) '{','.join(sets)}' found to package.")
        return 0

    if output is None:
        if name is not None:
            output = name + ".zip"
        else:
            print("ERROR: No name found in manifest, and output not specified. Please use -o to specify output archive name", file=sys.stderr)
            return 0

    if os.path.exists(output):
        x = input(f"{output} already exists, overwrite (y/n)? ")
        if x == "y" or x == "Y":
            os.unlink(output)
        else:
            print(f"ERROR: {output} already exists, not overwriting", file=sys.stderr)
            return 0

    try:
        print(f"Creating {output}")
        with zipfile.ZipFile(output, 'x') as z:
            for f in files:
                print(f"\tadding {f}")
                z.write(f, arcname=os.path.join(name, f))

            if 'in' in sets:
                print(f"\tadding {__file__}")
                z.write(__file__, arcname=os.path.join(name, 'package.py'))

                for m in manifests:
                    if m in manifests_to_include:
                        print(f"\tadding {m.mf}")
                        z.writestr(os.path.join(name, m.mf), get_manifest_contents(m.mf))
                    else:
                        print(f"\tskipping {m.mf}") # empty directory

            if 'out' in sets:
                desc = f"created by package\nplatform: {sys.platform}\nnode: {platform.node()}\n"

                if allow_user_manifest and len(umfiles) > 0:
                    desc += f"user-manifest: {', '.join(umfiles)}\n"

                z.writestr(os.path.join(name, 'PACKAGER-INFO.txt'), desc)

        print("DONE.")
    except Exception as e:
        print(f"ERROR: {e}")
        return 0

    return 1

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Package files for assignment submission")
    p.add_argument("package_set", nargs="*", help="Sets to package", default = [])
    p.add_argument("-o", dest="output", help="Name of output file")

    args = p.parse_args()

    if len(args.package_set) == 0:
        args.package_set = ['out']

    if not os.path.exists('MANIFEST.json'):
        print(f"ERROR: No MANIFEST.json found in current directory.")
        sys.exit(1)

    m = []
    for f in get_manifests():
        mr = Manifest(f)
        if not mr.manifest:
            print(f"Failed to read {f}")
            sys.exit(1)

        m.append(mr)
        print("Found and read:", f)

    sys.exit(package(m, args.package_set, args.output) != 1)
