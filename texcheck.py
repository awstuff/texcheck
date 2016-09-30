# MIT License
#
# Copyright (c) 2016 Adrian Wirth
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import sys
import io
import re
import collections

if __name__ == "__main__":

    output = ""
    problems_counter = 0

    def append_to_output(msg):
        global output
        output = output + "\n    " + msg

    def append_problem_to_output(msg):
        global output, problems_counter
        problems_counter += 1
        output = output + "\n[!] " + msg


    if len(sys.argv) < 2:
        sys.exit("No input file specified, exiting.")

    file_name = sys.argv[1]

    try:
        with io.open(file_name, "r", encoding="utf8") as file:
            file_contents = file.read()
    except Exception as e:
        sys.exit(str(e))

    comments_re = re.compile("%(.*)")   # remove comments
    file_contents = comments_re.sub("", file_contents)

    print("Detecting bibitems..... done");
    bibitems_re = re.compile("\\\\bibitem(?:\\[.*?\\])?\\{(.*?)\\}")
    bibitems = collections.Counter(bibitems_re.findall(file_contents))
    bibitems = collections.OrderedDict(sorted(bibitems.items()))

    print("Detecting citations..... done");
    citations_re = re.compile("\\\\cite\\{(.*?)\\}")
    citations = collections.Counter(citations_re.findall(file_contents))
    citations = collections.OrderedDict(sorted(citations.items()))

    print("Detecting labels..... done");
    labels_re = re.compile("\\\\label\\{(.*?)\\}")
    labels = collections.Counter(labels_re.findall(file_contents))
    labels = collections.OrderedDict(sorted(labels.items()))

    print("Detecting refs..... done");
    refs_re = re.compile("\\\\ref\\{(.*?)\\}")
    refs = collections.Counter(refs_re.findall(file_contents))
    refs = collections.OrderedDict(sorted(refs.items()))

    print("Detecting pagerefs..... done");
    pagerefs_re = re.compile("\\\\pageref\\{(.*?)\\}")
    pagerefs = collections.Counter(pagerefs_re.findall(file_contents))
    pagerefs = collections.OrderedDict(sorted(pagerefs.items()))

    print("Detecting namerefs..... done");
    namerefs_re = re.compile("\\\\nameref\\{(.*?)\\}")
    namerefs = collections.Counter(namerefs_re.findall(file_contents))
    namerefs = collections.OrderedDict(sorted(namerefs.items()))




    for name, count in bibitems.items():    # check for duplicate and never referenced bibitems
        if count > 1:
            append_problem_to_output("bibitem '" + name + "' is defined " + str(count) + " times")

        if not name in citations:
            append_problem_to_output("bibitem '" + name + "' is never cited")
        else:
            append_to_output("bibitem '" + name + "': " + str(citations[name]) + " citations")

    undefined_bibitems = [name for name in citations.keys() if not name in bibitems]    # check for bibitems that are referenced, but never defined
    for bibitem in undefined_bibitems:
        append_problem_to_output("bibitem '" + bibitem + "' is cited but never defined")




    for name, count in labels.items():    # check for duplicate and never referenced labels
        if count > 1:
            append_problem_to_output("label '" + name + "' is defined " + str(count) + " times")

        name_in_refs = name in refs;
        name_in_pagerefs = name in pagerefs;
        name_in_namerefs = name in namerefs;

        if not name_in_refs and not name_in_pagerefs and not name_in_namerefs:
            append_problem_to_output("label '" + name + "' is never referenced")
        else:
            if name_in_refs:
                ref_count = refs[name]
            else:
                ref_count = 0

            if name_in_pagerefs:
                pageref_count = pagerefs[name]
            else:
                pageref_count = 0

            if name_in_namerefs:
                nameref_count = namerefs[name]
            else:
                nameref_count = 0

            append_to_output("label '" + name + "': " + str(ref_count) + " refs, " + str(pageref_count) + " pagerefs, " + str(nameref_count) + " namerefs")

    undefined_refs = [name for name in refs.keys() if not name in labels]    # check for labels that are ref-referenced, but never defined
    for label in undefined_refs:
        append_problem_to_output("label '" + label + "' is referenced via ref but never defined")

    undefined_pagerefs = [name for name in pagerefs.keys() if not name in labels]    # check for labels that are pageref-referenced, but never defined
    for label in undefined_pagerefs:
        append_problem_to_output("label '" + label + "' is referenced via pageref but never defined")

    undefined_namerefs = [name for name in namerefs.keys() if not name in labels]    # check for labels that are nameref-referenced, but never defined
    for label in undefined_namerefs:
        append_problem_to_output("label '" + label + "' is referenced via nameref but never defined")




    print(output)

    if problems_counter:
        print("\n" + str(problems_counter) + " PROBLEMS FOUND")
    else:
        print("\nNO PROBLEMS FOUND")
