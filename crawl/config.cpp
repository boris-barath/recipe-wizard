#include "config.h"

analyzer::config_options fill_config(const wstring &lang, const wstring &ipath) {
    wstring lpath = ipath + L"/share/freeling/" + lang + L"/";

    analyzer::config_options cfg;

    cfg.Lang = lang;

    cfg.TOK_TokenizerFile = lpath + L"tokenizer.dat";
    cfg.SPLIT_SplitterFile = lpath + L"splitter.dat";

    cfg.MACO_LocutionsFile = lpath + L"locucions.dat";
    cfg.MACO_QuantitiesFile = lpath + L"quantities.dat";
    cfg.MACO_AffixFile = lpath + L"afixos.dat";
    cfg.MACO_ProbabilityFile = lpath + L"probabilitats.dat";
    cfg.MACO_DictionaryFile = lpath + L"dicc.src";
    cfg.MACO_NPDataFile = lpath + L"np.dat";
    cfg.MACO_PunctuationFile = lpath + L"../common/punct.dat";
    cfg.MACO_CompoundFile = lpath + L"compounds.dat";
    cfg.MACO_NPDataFile = lpath + L"nerc/ner/ner-ab-poor1.dat";
    //cfg.MACO_UserMapFile = L"config/usermap.dat";

    //cfg.SENSE_ConfigFile = lpath + L"senses.dat";
    //cfg.UKB_ConfigFile = lpath + L"ukb.dat";

    cfg.TAGGER_HMMFile = lpath + L"tagger.dat";
    cfg.TAGGER_ForceSelect = freeling::RETOK;

    cfg.NEC_NECFile = lpath + L"nerc/nec/nec-ab-poor1.dat";

    cfg.PARSER_GrammarFile = lpath + L"chunker/grammar-chunk.dat";

    cfg.DEP_TxalaFile = lpath + L"dep_txala/dependences.dat";
    //cfg.DEP_TreelerFile = lpath + L"dep_treeler/dependences.dat";

    return cfg;
}

analyzer::invoke_options fill_invoke() {
    analyzer::invoke_options ivk;

    ivk.InputLevel = TEXT;
    ivk.OutputLevel = TAGGED;

    ivk.MACO_UserMap = false;
    ivk.MACO_AffixAnalysis = true;
    ivk.MACO_MultiwordsDetection = true;
    ivk.MACO_NumbersDetection = true;
    ivk.MACO_PunctuationDetection = true;
    ivk.MACO_DatesDetection = true;
    ivk.MACO_QuantitiesDetection = true;
    ivk.MACO_DictionarySearch = true;
    ivk.MACO_ProbabilityAssignment = true;
    ivk.MACO_CompoundAnalysis = true;
    ivk.MACO_NERecognition = true;
    ivk.MACO_RetokContractions = true;

    //ivk.SENSE_WSD_which = UKB;
    ivk.TAGGER_which = HMM;

    ivk.DEP_which = TXALA;

    ivk.NEC_NEClassification = true;

    return ivk;
}