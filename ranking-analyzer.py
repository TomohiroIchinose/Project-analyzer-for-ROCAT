# -*- coding: utf-8 -*-
import git
import os
import re
import json
import sys


class Diff(object):

    DELIMITER = "\n\n"

    def __init__(self, repo_path, file_name):
        self.repo = git.Repo(repo_path)
        self.ranking = {}
        #self.head = self.repo.head.commit
        #self.parent = self.head.parents[0]
        self.file_name = file_name
        self.key = ["TODO", "hack"]
        self.debt_words = ["hack", "retarded", "at a loss", "stupid", "remove this code", "ugly", "take care", "something's gone wrong", "nuke", "is problematic", "may cause problem", "hacky", "unknown why we ever experience this", "treat this as a soft error", "silly", "workaround for bug", "kludge", "fixme", "this isn't quite right", "trial and error", "give up", "this is wrong", "hang our heads in shame", "temporary solution", "causes issue", "something bad is going on", "cause for issue", "this doesn't look right", "is this next line safe", "this indicates a more fundamental problem", "temporary crutch", "this can be a mess", "this isn't very solid", "this is temporary and will go away", "is this line really safe", "there is a problem", "some fatal error", "something serious is wrong", "don't use this", "get rid of this", "doubt that this would work", "this is bs", "give up and go away", "risk of this blowing up", "just abandon it", "prolly a bug", "probably a bug", "hope everything will work", "toss it", "barf ", "something bad happened", "fix this crap", "yuck", "certainly buggy", "remove me before production", "you can be unhappy now", "this is uncool", "bail out", "it doesn't work yet", "crap", "inconsistency", "abandon all hope", "kaboom"]

    def check_word(self, line):
        for keyword in self.debt_words:
            if keyword in line:
                return keyword
        return None

    def check_satd(self):
        precommit = None
        alluser = {}
        ranklist = []
        check = 0
        preword = ""
        for commit in self.repo.iter_commits('master'):
            if not precommit is None:
                diff = [
                    (test.diff) for test
                    in commit.diff(precommit, create_patch=True)
                ]
                for line in self.DELIMITER.join(diff).splitlines():
                    print line
                    if(check == 1):
                        if(line.startswith("+") and preword == self.check_word(line)):
                            # SATD is not removed.
                            print "NO!"
                        else:
                            #SATD is removed.
                            print "OK!"
                            print precommit.committer
                            if precommit.committer in alluser:
                                alluser[precommit.committer] = int(alluser[precommit.committer]) + 1
                            else:
                                alluser[precommit.committer] = 1
                        check = 0
                    if any([word.lower() in line.lower() for word in self.debt_words]) and line.startswith("-") and check == 0:
                        preword = self.check_word(line)
                        check = 1
            precommit = commit

        for key, value in alluser.iteritems():
            user = {"name":unicode(key), "num":value}
            ranklist.append(user)

        self.ranking["SATDRanking"] = ranklist

        with open(self.file_name, 'w') as f:
            f.write(json.dumps(self.ranking, indent=4))
        return json.dumps(self.ranking, indent=4)

if __name__ == '__main__':
    argv = sys.argv
    #obj = Diff("./Activiti", "./test.json")
    #obj = Diff("./repo", "./test2.json")
    #obj = Diff("./acra", "./test3.json")
    #obj = Diff("./redis-py", "./test4.json")
    #obj = Diff("./activeadmin", "./test5.json")
    obj = Diff(argv[1], argv[2])
    print obj.check_satd()