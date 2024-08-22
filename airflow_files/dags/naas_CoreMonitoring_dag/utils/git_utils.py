import logging 
import requests
import urllib.parse
import os
import json
import datetime

from github import Github
from github import Auth

os.system("clear")

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

def repo_sync_file(gh_token,gh_reponame, entity, local_path, git_path, git_branch, scenario):
    print('Synchronize git repo...')


    print("Connect to repo ")
    # using an access token
    g = Github(gh_token)
    repo = g.get_repo(gh_reponame)

    print('Path from dag for file')
    dag_file= local_path
    
    try:
        print('Open following file: ', dag_file)
        with open(dag_file, 'r') as file:
            content = file.read()
    except:
        print('Exception: ', dag_file)
        print('File not available.')

    print('Path from repository for file git path... %s ' % git_path)
    git_file = git_path
    contents = repo.get_contents(git_file, ref=git_branch)
    print('Contets sha: ', contents.sha)

    try:
        print('----------Entity: ', entity)
        print('git_pah: ', git_path)
        print('Updating %s file in GitHub path: %s' % (entity, git_path))
        repo.update_file(contents.path, "commit scenario update of file %s" % entity, content, contents.sha, branch=git_branch)
    except:
        print('Creating new %s file in GitHub in path: %s' % (entity, git_file))
        repo.create_file('%s.yaml' % entity, 'create %s yaml' %entity, contents.sha, branch=git_branch)

    print(git_file + ' UPDATED')

    g.close()

