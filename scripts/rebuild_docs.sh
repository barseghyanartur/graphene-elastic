#!/usr/bin/env bash
rm docs/graphene_elastic*.rst
rm -rf builddocs/
sphinx-apidoc src/graphene_elastic --full -o docs -H 'graphene-elastic' -A 'Artur Barseghyan <artur.barseghyan@gmail.com>' -V '0.1' -f -d 20
cp docs/conf.py.distrib docs/conf.py
./scripts/build_docs.sh
