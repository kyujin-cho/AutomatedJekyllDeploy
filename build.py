import subprocess
import click
import os 
import typing 
from colorama import init, Fore
from git import Repo

class BuildError(Exception):
  def __init__(self, message):
    super().__init__(message)
    self.message = message

def exec(command: str, cwd=None, debug=False):
  if debug:
    print(f'Executing command {command}')
  print(Fore.YELLOW, end='')
  proc = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
  (out, err) = proc.communicate()
  if debug:
    print(out.decode('utf-8').strip())

  print(Fore.BLUE, end='')
  if len(err) > 0:
    raise BuildError(err.decode('utf-8').strip())
  
@click.group()
def cli():
  pass

@cli.command()
@click.option('--branch', '-b', default='gh-pages', help='Branch name where Github Pages provided')
@click.option('--backup-branch', default='master', help='Branch name for backup repo')
@click.option('--debug', '-d', is_flag=True)
@click.argument('message')
def build(branch: str, message: str, backup_branch: str, debug: bool):
  init()
  cwd = os.getcwd()
  build_repo = Repo(os.path.join(cwd, '_site'))
  backup_repo = Repo(cwd)

  print(Fore.BLUE, end='')

  print('Pulling latest blog markdown articles')
  build_repo.remote(name='origin').pull(refspec=f'refs/heads/{backup_branch}:refs/heads/{backup_branch}')
  
  print('Building site for production ready')
  exec('bundle exec jekyll build', debug=debug)

  print('Adding new files on Github Pages git folder')
  index = build_repo.index
  index.add(['*'])

  print('Making commit for changes on website')
  index.commit(message)

  print('Pushing changes to Github Pages repository')
  build_repo.remote(name='origin').push(refspec=f'refs/heads/{branch}:refs/heads/{branch}')
  
  print('Adding new files on backup git')
  exec('git add *')
  # backup_index.add(['*'])

  print('Making commit for change on backup')
  backup_index = backup_repo.index
  backup_index.commit(message)

  print('Pushing changes to backup repository')
  backup_repo.remote(name='origin').push(refspec=f'refs/heads/{backup_branch}:refs/heads/{backup_branch}')

  print(Fore.GREEN + 'Done!')
  print(Fore.RESET)

if __name__ == '__main__':
    cli()