import os
import subprocess

from datetime import datetime
from git import Repo

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--local', action='store_true')
        parser.add_argument('--remote', action='store_true')

    def handle_local(self):
        commits = self.get_candidates()
        commits = self.get_commits(commits)
        files = self.get_files(commits)
        command = f"{settings.DEPLOY_USERNAME}@{settings.DEPLOY_SERVER}:{settings.DEPLOY_BASE_DIR}"
        for file in files:
            if os.path.exists(file):
                subprocess.run(["scp", file, os.path.join(command, file)])
            else:
                print(f"Warning: {file} not found, unable to scp")

    def get_candidates(self):
        repo = self.get_repo()
        pointer = repo.heads.master.commit
        commits = []
        while len(commits) < 10:
            commits.append(pointer)
            pointer = pointer.parents[0]
        return commits

    def get_commits(self, candidates):
        for index, c in enumerate(candidates):
            committed_date = datetime.fromtimestamp(c.committed_date).strftime("%Y-%m-%d %H:%M")
            print(f"{index}) {committed_date} {c.summary}")
        try:
            index = int(input("Deploy from which commit (q to quit)? "))
        except ValueError:
            return []
        return candidates[:index + 1]

    def get_files(self, commits):
        files = set()
        for commit in commits:
            files = files | set(commit.stats.files)
        
        print("Files:")
        for file in sorted(files):
            print(file)

        if not files or input("\nGo ahead and scp (y/n)? ") not in ['y', 'Y']:
            return set()

        return files

    def get_repo(self):
        repo = Repo(os.getcwd())
        assert not repo.bare
        assert repo.head.ref == repo.heads.master
        return repo

    def handle_remote(self):
        subprocess.run(["pip", "install", "-r", "requirements.txt"])
        call_command("migrate")
        subprocess.run(["npm", "install"])
        subprocess.run(["npx", "babel", "kilo/static/kilo/js/babel-src",
                        "--out-dir", "kilo/static/kilo/js/babel-prod", "--presets", "react-app/prod"])
        subprocess.run(["npx", "babel", "rhyme/static/rhyme/js/babel-src",
                        "--out-dir", "rhyme/static/rhyme/js/babel-prod", "--presets", "react-app/prod"])
        call_command("collectstatic", "--noinput")
        subprocess.run(["touch", "tmp/restart.txt"])

    def handle(self, *args, **options):
        if options['local']:
            self.handle_local()
        elif options['remote']:
            self.handle_remote()
        else:
            raise CommandError("Must provide a mode, either --local or --remote")
