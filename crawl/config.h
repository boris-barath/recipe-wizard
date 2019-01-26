#ifndef CRAWL_CONFIG_H
#define CRAWL_CONFIG_H

#include "freeling.h"

using namespace std;
using namespace freeling;

analyzer::config_options fill_config(const wstring &lang, const wstring &ipath);

analyzer::invoke_options fill_invoke();

#endif //CRAWL_CONFIG_H
