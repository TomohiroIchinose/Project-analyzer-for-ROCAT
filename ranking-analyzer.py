# -*- coding: utf-8 -*-
import git
import os
import re
import json
import sys
import difflib
import time

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

    def check_comment_java(self, file):
        list = []
        isComment = False
        count = 1
        for line in file.splitlines():
            if isComment:
                list.append(count)
            if "/*" in line:
                isComment = True
                list.append(count)
            if "*/" in line:
                isComment = False
            if "//" in line and not "://" in line:
                list.append(count)
            count += 1
        #print list
        return list

    def check_comment_py(self, file):
        list = []
        isComment = False
        count = 1
        for line in file.splitlines():
            if "#" in line:
                list.append(count)
            count += 1
            # print list
        return list

    def check_comment_rb(self, file):
        list = []
        isComment = False
        count = 1
        for line in file.splitlines():
            if isComment:
                list.append(count)
            if "=begin" in line:
                isComment = True
                list.append(count)
            if "=end" in line:
                isComment = False
            if "#" in line and not "#{" in line:
                list.append(count)
            count += 1
            # print list
        return list

    def check_comment_line(self, file, filename):
        ex = (os.path.splitext(filename)[1])[1:]
        comment_list = []

        if ex == "java" or ex == "cc" or ex == "cpp":
            comment_list = self.check_comment_java(file)
        elif ex == "py":
            comment_list = self.check_comment_py(file)
        elif ex == "rb":
            comment_list = self.check_comment_rb(file)

        return comment_list


    @property
    def check_satd(self):
        precommit = None
        alluser = {}
        ranklist = []
        startcount = False
        found_keyword = False
        pre_keyword = ""
        commit_comments = []
        precommit_comments = []
        for commit in self.repo.iter_commits('master'):
            #print alluser
            #print commit
            #file_contents = self.repo.git.show('{}:{}'.format(commit, "Code1.java"))
            #print file_contents
            if not precommit is None and int(time.strftime("%Y",time.gmtime(commit.committed_date))) >= 2016:
                diff = [
                    (test.diff) for test
                    in commit.diff(precommit, create_patch=True)
                ]
                foundminus3 = False
                foundplus3 = False
                for line in self.DELIMITER.join(diff).splitlines():
                    #print line

                    # line count
                    if (startcount):
                        if not (line.startswith("-")):
                            plus_line += 1
                        if not (line.startswith("+")):
                            minus_line += 1
                    #if(startcount):
                        #print str(commit_line) + "," + str(precommit_line)

                    # minus file
                    if(line.startswith("--- a/") or line.startswith("--- /")):
                        #print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
                        startcount = False
                        commit_filepath = line.split("/",1)[1]
                        if not commit_filepath == "dev/null":
                            commit_contents = self.repo.git.show('{0}:{1}'.format(commit, commit_filepath))
                            commit_comments = self.check_comment_line(commit_contents, commit_filepath)
                            #print commit_comments
                        #print commit_filepath

                    # plua file
                    if (line.startswith("+++ b/") or line.startswith("+++ /")):
                        #print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
                        precommit_filepath = line.split("/", 1)[1]
                        if not precommit_filepath == "dev/null":
                            precommit_contents = self.repo.git.show('{0}:{1}'.format(precommit, precommit_filepath))
                            precommit_comments = self.check_comment_line(precommit_contents, precommit_filepath)
                            #print precommit_comments
                        #print precommit_filepath

                    # check diff start line
                    if(line.startswith("@@")):
                        if ("," in line.split("-")[1].split("+")[0]):
                            minus_line = int(line.split("-")[1].split(",",1)[0]) - 1
                        else:
                            minus_line = int(line.split("-")[1].split(" +", 1)[0]) - 1
                        if("," in line.split("+")[1]):
                            plus_line = int(line.split("+")[1].split(",",1)[0]) - 1
                        else:
                            plus_line = int(line.split("+")[1].split(" @@", 1)[0]) - 1
                        startcount = True
                        #print commit_line
                        #print precommit_line


                    # found keyword in previous line
                    if(found_keyword):

                        # found plus line
                        if(line.startswith("+")):

                            #print "***** " + str(plus_line) + "," + line
                            # found any keyword
                            if(any([word.lower() in line.lower() for word in self.debt_words])):

                                # found pre_keyword
                                if pre_keyword in line:
                                    #print "NOT removed SATD by " + str(precommit.committer)
                                    pass

                                # found pre key
                                else:
                                    #print "another SATD by " + str(precommit.committer)
                                    pass

                            # not found any keyword
                            else:
                                #print "removed SATD!! by " + str(precommit.committer)
                                userlist = alluser.keys()
                                already = 0
                                if str(precommit.committer) == "GitHub":
                                    adduser = precommit.author
                                else:
                                    adduser = precommit.committer
                                #print "removed SATD!! by " + str(adduser)
                                if not len(userlist) == 0:
                                    for user in userlist:
                                        if difflib.SequenceMatcher(None, unicode(user), unicode(adduser)).ratio() > 0.6:
                                            already = 1
                                            break
                                    if already == 1:
                                        alluser[user] = int(alluser[user]) + 1
                                    else:
                                        alluser[adduser] = 1
                                else:
                                    alluser[adduser] = 1

                        # not found plus line
                        else:
                            #print "removed SATD with no plus!! by " + str(precommit.committer)
                            userlist = alluser.keys()
                            already = 0
                            if str(precommit.committer) == "GitHub":
                                adduser = precommit.author
                            else:
                                adduser = precommit.committer
                            #print "removed SATD with no plus!! by " + str(adduser)
                            if not len(userlist) == 0:
                                for user in userlist:
                                    if difflib.SequenceMatcher(None, unicode(user), unicode(adduser)).ratio() > 0.6:
                                        already = 1
                                        break
                                if already == 1:
                                    alluser[user] = int(alluser[user]) + 1
                                else:
                                    alluser[adduser] = 1
                            else:
                                alluser[adduser] = 1

                        found_keyword = False

                    else:
                        # find out keyword in minus file
                        if(line.startswith("-") and any([word.lower() in line.lower() for word in self.debt_words])):
                            #print "***** " + str(minus_line) + "," + line
                            if(minus_line in commit_comments):
                                #print "found SATD!!!"
                                found_keyword = True
                                pre_keyword = self.check_word(line)
                            else:
                                #print "it is not SATD-"
                                pass

                        # find out keyword in plus file
                        if (line.startswith("+") and any([word.lower() in line.lower() for word in self.debt_words])):
                            #print "***** " + str(plus_line) + "," + line
                            if (plus_line in precommit_comments):
                                #print "added SATD!!! by " + str(precommit.committer)
                                userlist = alluser.keys()
                                already = 0
                                if str(precommit.committer) == "GitHub":
                                    adduser = precommit.author
                                else:
                                    adduser = precommit.committer
                                if not len(userlist) == 0:
                                    for user in userlist:
                                        if difflib.SequenceMatcher(None, unicode(user), unicode(adduser)).ratio() > 0.6:
                                            already = 1
                                            break
                                    if already == 1:
                                        alluser[user] = int(alluser[user]) - 1
                                    else:
                                        alluser[adduser] = -1
                                else:
                                    alluser[adduser] = -1
                            else:
                                #print "it is not SATD+"
                                pass



            precommit = commit
            #print "#############################################"

        for key, value in alluser.iteritems():
            if value > 0:
                user = {"name":unicode(key), "num":value}
                ranklist.append(user)
            #user = {"name": unicode(key), "num": value}
            #ranklist.append(user)

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
    obj.check_satd