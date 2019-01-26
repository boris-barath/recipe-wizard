#include <iostream>
#include <algorithm>
#include <fstream>
#include <boost/filesystem.hpp>
#include <unordered_set>

#include "freeling.h"
#include "config.h"

using namespace std;
using namespace freeling;

int main() {
    vector<wstring> blacklist{L"tsp", L"tablespoon", L"handful", L"strip", L"mix", L"inch", L"box", L"lbs", L"medium",
                              L"cup", L"teaspoon", L"glass"};

    wstring lang = L"en";
    wstring ipath = L"/usr/local";

    cerr << "init analizer" << endl;
    util::init_locale(L"default");

    analyzer::config_options cfg = fill_config(lang, ipath);
    analyzer anal(cfg);

    analyzer::invoke_options ivk = fill_invoke();
    anal.set_current_invoke_options(ivk);

    cerr << "Reading file" << endl;
    wstring text;
    wstring line;
    wfstream inFile;
    inFile.open("output-parsed.txt");

    if (!inFile) {
        cerr << "Unable to open file" << endl;
        exit(1);
    }

    vector<wstring> recipes{L""};

    while (getline(inFile, line)) {
        if (line == L"-") recipes.emplace_back(L"");
        else recipes[recipes.size() - 1] = recipes[recipes.size() - 1] + L" " + line + L".";
    }

    for (const auto r : recipes) {
        list<sentence> ls;
        unordered_set<wstring> res;
        anal.analyze(r, ls);

        for (const sentence s : ls) {
            for (const word &w : s) {
                wstring lemma = w.get_lemma();
                if (lemma.length() > 2 && lemma.back() != '.' && w.get_tag()[0] == 'N') {
                    if (find(blacklist.begin(), blacklist.end(), lemma) == blacklist.end())
                        res.insert(lemma);
                }
            }
        }

        for (auto it = res.begin(); it != res.end(); it++) wcout << *it << " ";
        if (res.size() == 0) cout << "N/A";
        cout << endl;
    }
}