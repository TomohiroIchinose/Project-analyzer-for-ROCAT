import os
import re
import json
import copy
import random
from author import calc_authorship


class Project:
    def __init__(self, repo_path, lang):
        self.CCOUNT_FUNC = {"java": self.count_comments4j, "py": self.count_comments4py, "rb": self.count_comments4rb}
        self.repo_path = repo_path
        self.lang = lang
        self.authors = calc_authorship(repo_path)
        self.colormap = {}
        self.color = [0.0, 0.0, 0.0]
        self.debt_words = ["hack", "retarded", "at a loss", "stupid", "remove this code", "ugly", "take care", "something's gone wrong", "nuke", "is problematic", "may cause problem", "hacky", "unknown why we ever experience this", "treat this as a soft error", "silly", "workaround for bug", "kludge", "fixme", "this isn't quite right", "trial and error", "give up", "this is wrong", "hang our heads in shame", "temporary solution", "causes issue", "something bad is going on", "cause for issue", "this doesn't look right", "is this next line safe", "this indicates a more fundamental problem", "temporary crutch", "this can be a mess", "this isn't very solid", "this is temporary and will go away", "is this line really safe", "there is a problem", "some fatal error", "something serious is wrong", "don't use this", "get rid of this", "doubt that this would work", "this is bs", "give up and go away", "risk of this blowing up", "just abandon it", "prolly a bug", "probably a bug", "hope everything will work", "toss it", "barf ", "something bad happened", "fix this crap", "yuck", "certainly buggy", "remove me before production", "you can be unhappy now", "this is uncool", "bail out", "it doesn't work yet", "crap", "inconsistency", "abandon all hope", "kaboom"]


    def get_bestauthor(self, file_path):
        max_rate = 0
        max_author = ""
        for search_path, search_author, search_rate in self.authors :
            #print search_path, file_path
            search_path = self.repo_path+"\\"+ search_path
            search_path = search_path.replace("\\", "/")
            file_path = file_path.replace("\\", "/")
            if search_path == file_path and max_rate < search_rate :
                #print search_path, file_path
                max_author = search_author
                max_rate = search_rate
        return max_author

    def set_color(self, author):
        if not author in self.colormap :
            self.color = [random.random(),random.random(),random.random()]

            #mod = len(self.colormap) % 3
            #self.color[mod] += 0.3
            #if self.color[mod] > 1.0 :
            #    self.color[mod] -= 1.0
            self.colormap[author] = copy.deepcopy(self.color)
        return self.colormap[author]

    def get_json(self):
        blocks = []
        buildings = []
        block_name = set()
        for dpath, dnames, fnames in os.walk(self.repo_path):
            for fname in fnames:
                fpath = dpath + "/" + fname
                if not self.is_target_file(fname):
                    continue
                author = self.get_bestauthor(fpath)
                print author, fpath
                color = self.set_color(author)
                block_name.add(dpath)
                loc = self.count_lines(fpath) + 2
                comment = self.CCOUNT_FUNC[self.lang](fpath)
                slist = self.count_selfadmitted(fpath)
                buildings.append(
                    {"block": dpath, "name": fname, "path": dpath + "/" + fname, "width": comment, "height": loc * 2, "color_r":color[0], "color_g":color[1], "color_b":color[2],"SATD":slist})
        for name in block_name:
            blocks.append({"name": name})
        json_string = json.dumps({"blocks": list(blocks), "buildings": buildings}, indent=4)
        with open('test.json', 'w') as f:
            #print json_string
            #json.dump(json_string, f, indent=4)
            f.write(json_string)
        return json_string

    def is_target_file(self, file_path):
        p = re.compile('.*\.' + self.lang)
        m = p.match(file_path)
        return m

    def count_lines(self, file_path):
        f = open(file_path)
        lines = f.readlines()
        f.close()
        return lines.count("\n")

    def count_selfadmitted(self, file_path):
        slist = []
        f = open(file_path)
        lines = f.readlines()
        for i,line in enumerate(lines):
            if self.is_debt_line(line):
                slist.append(i)
        f.close()
        return slist

    def is_debt_line(self,line):
        return any([word.lower() in line.lower() for word in self.debt_words])

    def count_comments4rb(self, file_path):
        f = open(file_path)
        comments = 0
        isComment = False
        for line in f:
            if "=begin" in line:
                isComment = True
            if "=end" in line:
                isComment = False
            if isComment:
                comments += 1
            if "#" in line and not "#{" in line:
                comments += 1
        return comments

    def count_comments4j(self, file_path):
        f = open(file_path)
        comments = 0
        for line in f:
            if "//" in line:
                comments += 1
        f.close()
        return comments

    def count_comments4py(self, file_path):
        f = open(file_path)
        comments = 0
        for line in f:
            if "#" in line:
                comments += 1
        f.close()
        return comments


def main():
    pa = Project("C:\Users\Ichinose\\rubyzip", "rb")
    pjson = pa.get_json()
    print pjson


main()
