#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# showghrdl by shinrax2
VERSION = "1.0"
#built-in
import sys
import os
import json
import urllib.parse

#pip packages
import requests
import tabulate

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

def get_history(history, repo, tag, asset):
    try:
        return history[repo["author"]+"/"+repo["repo"]][tag["tag"]][asset]
    except KeyError:
        return 0

def set_history(history, repo, tag, asset, num):
    reponame = repo["author"]+"/"+repo["repo"]
    try:
        history[reponame][tag["tag"]][asset] = num
    except KeyError:
        history[reponame][tag["tag"]] = {}
        history[reponame][tag["tag"]][asset] = num
    return history
    
def calc_history(history, info, repo):
    for key, tag in info.items():
        for asset, dlcount in tag["assets"].items():
            history = set_history(history, repo, tag, asset, dlcount)
    return history

print(f"showghrdl {VERSION} by shinrax2\n")
default_configfile_names = ["config.json", "showghrdl.config.json"]
config_not_found = True
history_filename = os.path.abspath(os.path.join(os.path.dirname(__file__), "showghrdl.history.json"))

#config
if len(sys.argv[1:]) == 1:
    configfile = sys.argv[1:][0]
else:
    for cfn in default_configfile_names:
        if os.path.isfile(os.path.join(os.path.dirname(__file__), cfn)) == True:
            configfile = os.path.abspath(os.path.join(os.path.dirname(__file__), cfn))
            config_not_found = False
            break
    if config_not_found == True:
        print("please create config.json or point to a valid config file with commandline argument")
        sys.exit(1)

with open(configfile, "r") as fh:
    config = json.loads(fh.read())

#history
if os.path.isfile(history_filename) == False:
    with open(history_filename, "w") as f:
        history = {}
        for repo in config["repos"]:
            history[repo["author"]+"/"+repo["repo"]] = {}
        f.write(json.dumps(history, ensure_ascii=False))
with open(history_filename, "r") as f:
    history = json.loads(f.read())

for repo in config["repos"]:
    info = get_release_info(repo, config["github_api_key"])
    total = 0
    if info == False:
        print("repository \""+repo["author"]+"/"+repo["repo"]+"\" not found or private/private statistics")
    else:
        print("download counts for \""+repo["author"]+"/"+repo["repo"]+"\" (only_latest: "+str(repo["only_latest"])+")\n")
        for key, tag in info.items():
            print("release name: "+tag["name"]+"\ttag: "+tag["tag"])
            table_data = []
            for name, dlcount in tag["assets"].items():
                table_data.append([name, dlcount, dlcount - get_history(history, repo, tag, name)])
                total += dlcount
            print(tabulate.tabulate(table_data, headers=["asset name", "download count", "change"], tablefmt='orgtbl')+"\n")
        history = calc_history(history, info, repo)
        print("total downloads: "+str(total)+"\n")

with open(history_filename, "w") as f:
    f.write(json.dumps(history, ensure_ascii=False))
