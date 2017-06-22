# MIT License
#
# Copyright (c) 2016-2017 Adrian Wirth
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




    def find_by_regex(regex):
        return re.compile(regex).findall(file_contents)


    def count_and_sort(array):
        return collections.OrderedDict(sorted(collections.Counter(array).items()))

    def find_by_regex_and_count_and_sort(regex, name):
        print("Detecting " + name + "..... done")
        return count_and_sort(find_by_regex(regex))


    bibitems = find_by_regex_and_count_and_sort("\\\\bibitem(?:\\[.*?\\])?\\{(.*?)\\}", "bibitems")
    citations = find_by_regex_and_count_and_sort("\\\\cite\\{(.*?)\\}", "citations")
    labels = find_by_regex_and_count_and_sort("\\\\label\\{(.*?)\\}", "labels")

    print("Detecting listing labels..... done")
    listings = count_and_sort(find_by_regex("\\\\begin\\{lstlisting\\}\\[language=[a-zA-Z]*,\\s*caption=\\{.*\\},\\s*label=(.*?)\\]") + find_by_regex("\\\\begin\\{lstlisting\\}\\[caption=\\{.*\\},\\s*label=(.*?)\\]"))

    refs = find_by_regex_and_count_and_sort("\\\\ref\\{(.*?)\\}", "refs")
    pagerefs = find_by_regex_and_count_and_sort("\\\\pageref\\{(.*?)\\}", "pagerefs")
    namerefs = find_by_regex_and_count_and_sort("\\\\nameref\\{(.*?)\\}", "namerefs")
    listingrefs = find_by_regex_and_count_and_sort("\\\\listingref\\{(.*?)\\}", "listingrefs")
    hyperrefs = find_by_regex_and_count_and_sort("\\\\hyperref\\[(.*?)\\]", "hyperrefs")




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




    def label_check(name_for_print, collection):
        for name, count in collection.items():    # check for duplicate and never referenced labels
            if count > 1:
                append_problem_to_output(name_for_print + " '" + name + "' is defined " + str(count) + " times")

            name_in_refs = name in refs
            name_in_pagerefs = name in pagerefs
            name_in_namerefs = name in namerefs
            name_in_listingrefs = name in listingrefs
            name_in_hyperrefs = name in hyperrefs

            if not name_in_refs and not name_in_pagerefs and not name_in_namerefs and not name_in_listingrefs and not name_in_hyperrefs:
                append_problem_to_output(name_for_print + " '" + name + "' is never referenced")
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

                if name_in_listingrefs:
                    listingref_count = listingrefs[name]
                else:
                    listingref_count = 0

                if name_in_hyperrefs:
                    hyperref_count = hyperrefs[name]
                else:
                    hyperref_count = 0

                append_to_output(name_for_print + " '" + name + "': " + str(ref_count) + " r, " + str(pageref_count) + " pr, " + str(nameref_count) + " nr, " + str(listingref_count) + " lr, " + str(hyperref_count) + " hr")


    label_check("label", labels)
    label_check("listing label", listings)




    def check_for_undefined_refs(ref_collection, ref_name):
        undefined_refs = [name for name in ref_collection.keys() if not (name in labels or name in listings)]

        for label in undefined_refs:
            append_problem_to_output("label '" + label + "' is referenced via " + ref_name + " but never defined")


    check_for_undefined_refs(refs, "ref")
    check_for_undefined_refs(pagerefs, "pageref")
    check_for_undefined_refs(namerefs, "nameref")
    check_for_undefined_refs(listingrefs, "listingref")
    check_for_undefined_refs(hyperrefs, "hyperref")




    print(output)

    if problems_counter:
        print("\n" + str(problems_counter) + " PROBLEMS FOUND")
    else:
        print("\nNO PROBLEMS FOUND")
