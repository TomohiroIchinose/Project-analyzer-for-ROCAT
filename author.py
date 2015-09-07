# -*- coding: utf-8 -*-
__author__ = 'shin-fu'

import sys
from git import Repo
from collections import defaultdict


def count_authors(project_name):
    #TARGET_PATH = "./target/"
    repo = Repo(project_name)
    file_dic = defaultdict(lambda: defaultdict(int))
    for commit in repo.iter_commits('master'):
        for file in commit.stats.files.keys():
            file_dic[file][commit.author.name] += 1
    return file_dic


def calc_authorship(project_name):
    file_dic = count_authors(project_name)
    authorship_list = []
    for key in file_dic:
        file_name = file_dic[key]
        number_of_all_commits = sum(file_name.values())
        for author, num_commits in file_name.items():
            rate = num_commits/float(number_of_all_commits)
            try:
                authorship_list.append((str(key), str(author), rate))
            except:
                pass
    return authorship_list


def print_authorship(project_name):
    authorship_list = calc_authorship(project_name)
    for line in authorship_list:
        print line[0]+","+line[1]+","+str(line[2])


def main():
    if len(sys.argv) != 2:
        print("usage: python {} <repository_path>".format(sys.argv[0]))
        sys.exit()
    print_authorship(sys.argv[1])

if __name__ == '__main__':
   # main()
    print_authorship("C:\Users\Ichinose\\ruby")
