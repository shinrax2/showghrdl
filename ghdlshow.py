#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# ghdlshow by shinrax2

#built-in
import sys
import os
import json
import urllib.parse

#pip packages
import requests

def get_release_info(repo, token):
    headers = {}
    if repo["github_api_key"] != "":
        token = repo["github_api_key"]
    if token != "":
        headers["Authorization"] = "token "+ token
    url = urllib.parse.urljoin(urllib.parse.urljoin(urllib.parse.urljoin("https://api.github.com/repos/" , repo["author"]+"/"), repo["repo"]+"/"), "releases")
    if repo["only_latest"] == True:
        url = urllib.parse.urljoin(url+"/", "latest")
    data = json.loads(requests.get(url, headers=headers).content)
    ret = {}
    try:
        if isinstance(data, str) == True and data["message"] == "Not Found":
            ret = False
    except KeyError:
        pass
    if ret != False:
        if repo["only_latest"] == True:
            tag = {}
            assets = {}
            tag["tag"] = data["tag_name"]
            tag["name"] = data["name"]
            for ass in data["assets"]:
                assets[ass["name"]] = ass["download_count"]
            tag["assets"] = assets
            ret[tag["tag"]] = tag
        else:
            for rel in data:
                tag = {}
                assets = {}
                tag["tag"] = rel["tag_name"]
                tag["name"] = rel["name"]
                for ass in rel["assets"]:
                    assets[ass["name"]] = ass["download_count"]
                tag["assets"] = assets
                ret[tag["tag"]] = tag
    return ret

configfile = "./config.json"
if len(sys.argv[1:]) == 1:
    configfile = sys.argv[1:][0]

if os.path.isfile(configfile) == False:
    print("please create config.json or point to a valid config file with commandline argument")
    sys.exit(1)

with open(configfile, "r") as fh:
    config = json.loads(fh.read())

for repo in config["repos"]:
    info = get_release_info(repo, config["github_api_key"])
    total = 0
    if info == False:
        print("repository \""+repo["author"]+"/"+repo["repo"]+"\" not found or private/private statistics")
    else:
        print("download counts for \""+repo["author"]+"/"+repo["repo"]+"\" (only_latest: "+str(repo["only_latest"])+")")
        for key, tag in info.items():
            print("\trelease name: "+tag["name"]+"\ttag: "+tag["tag"])
            print("\tassets:\n")
            for name, dlcount in tag["assets"].items():
                print("\t\tasset name: \""+name+"\"\tdownload count: "+str(dlcount))
                total += dlcount
            print("\n")
        print("\ttotal downloads: "+str(total)+"\n")
    