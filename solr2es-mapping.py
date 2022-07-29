#!/bin/env python

import sys

import xml.etree.ElementTree as xml
import json

tree = xml.parse(open(sys.argv[1]))
rootElement = tree.getroot()

BASIC_TYPES = {
    "string": "keyword",
    "strings": "keyword",
    "boolean": "boolean",
    "booleans": "boolean",
    "pint": "long",
    "pints": "long",
    "pfloat": "double",
    "pfloats": "double",
    "plong": "long",
    "plongs": "long",
    "pdouble": "double",
    "pdoubles": "double",
    "pdate": "date",
    "pdates": "date",
    "binary": "binary",
}

TOKENIZERS = {
    "solr.StandardTokenizerFactory": "standard",
    "solr.WhitespaceTokenizerFactory": "whitespace",
    "solr.KeywordTokenizerFactory": "keyword",
    "solr.JapaneseTokenizerFactory": {"type": "kuromoji_tokenizer", "mode": ">mode"},
    "solr.KoreanTokenizerFactory": {"type": "nori_tokenizer", "decompound_mode": ">decompound_mode"},
    "solr.PathHierarchyTokenizerFactory": {"type": "path_hierarchy", "delimiter": ">delimiter", "replacement": ">replacement", "bufferSize": ">bufferSize"},
    "solr.ThaiTokenizerFactory": "thai",
}

TOKEN_FILTERS = {
    "solr.LowerCaseFilterFactory": "lowercase",
    "solr.StopFilterFactory": "stop",
    "solr.SynonymFilterFactory": {"type": "synonym", "synonyms_path": ">synonyms", "expand": ">expand"},
    "solr.SynonymGraphFilterFactory": {"type": "synonym", "synonyms_path": ">synonyms", "expand": ">expand"},
    "solr.KeywordMarkerFilterFactory": {"type": "keyword_marker", "keywords_path": ">protected"},
    "solr.EnglishPossessiveFilterFactory": {"type": "stemmer", "language": "possessive_english"},
    "solr.PorterStemFilterFactory": "porter_stem",
    "solr.WordDelimiterGraphFilterFactory": {"type": "word_delimiter_graph", "generateWordParts": ">generateWordParts", "generateNumberParts": ">generateNumberParts", "catenateWords": ">catenateWords", "catenateNumbers": ">catenateNumbers", "catenateAll": ">catenateAll", "splitOnCaseChange": ">splitOnCaseChange", "preserveOriginal": ">preserveOriginal", "splitOnNumerics": ">splitOnNumerics", "stemEnglishPossessive": ">stemEnglishPossessive"},
    "solr.FlattenGraphFilterFactory": "flatten_graph",
    "solr.EnglishMinimalStemFilterFactory": {"type": "stemmer", "language": "minimal_english"},
    "solr.RemoveDuplicatesTokenFilterFactory": "remove_duplicates",
    "solr.ReversedWildcardFilterFactory": "reverse",
    "solr.DoubleMetaphoneFilterFactory": {"type": "phonetic","encoder": "double_metaphone","inject": ">replace"},
    "solr.PathHierarchyTokenizerFactory": {"type": "path_hierarchy", "delimiter": ">delimiter", "replacement": ">replacement", "bufferSize": ">bufferSize"},
    "solr.DelimitedPayloadTokenFilterFactory": {"type": "delimited_payload", "encoding": ">encoder", "delimiter": ">delimiter"},
    "solr.ArabicNormalizationFilterFactory": "arabic_normalization",
    "solr.ArabicStemFilterFactory": {"type": "stemmer", "language": "arabic"},
    "solr.BulgarianStemFilterFactory": {"type": "stemmer", "language": "bulgarian"},
    "solr.ElisionFilterFactory": {"type": "elision", "articles": ">articles", "ellipsis": ">ellipsis", "ignoreCase": ">ignoreCase"},
    "solr.SnowballPorterFilterFactory": "snowball",
    "solr.CJKWidthFilterFactory": "cjk_width",
    "solr.CJKBigramFilterFactory": "cjk_bigram",
    "solr.CzechStemFilterFactory": "czech_stem",
    "solr.GermanNormalizationFilterFactory": "german_normalization",
    "solr.GermanLightStemFilterFactory": {"type": "stemmer", "language": "light_german"},
    "solr.GreekLowerCaseFilterFactory": {"type": "lowercase", "language": "greek"},
    "solr.GreekStemFilterFactory": {"type": "stemmer", "language": "greek"},
    "solr.SpanishLightStemFilterFactory": {"type": "stemmer", "language": "light_spanish"},
    "solr.PersianNormalizationFilterFactory": "persian_normalization",
    "solr.FrenchLightStemFilterFactory": {"type": "stemmer", "language": "light_french"},
    "solr.IrishLowerCaseFilterFactory": {"type": "stemmer", "language": "irish"},
    "solr.GalicianStemFilterFactory": {"type": "stemmer", "language": "galician"},
    "solr.IndicNormalizationFilterFactory": "indic_normalization",
    "solr.HindiNormalizationFilterFactory": "hindi_normalization",
    "solr.HindiStemFilterFactory": {"type": "stemmer", "language": "hindi"},
    "solr.IndonesianStemFilterFactory": {"type": "stemmer", "language": "indonesian"},
    "solr.ItalianLightStemFilterFactory": {"type": "stemmer", "language": "light_italian"},
    "solr.JapaneseBaseFormFilterFactory": "kuromoji_baseform",
    "solr.JapanesePartOfSpeechStopFilterFactory": {"type": "kuromoji_part_of_speech", "stoptags": ">tags"},
    "solr.JapaneseKatakanaStemFilterFactory": {"type": "kuromoji_stemmer", "minimumLength": ">minimumLength"},
    "solr.KoreanPartOfSpeechStopFilterFactory": {"type": "nori_part_of_speech", "stoptags": ">tags"},
    "solr.KoreanReadingFormFilterFactory": "nori_readingform",
    "solr.LatvianStemFilterFactory": {"type": "stemmer", "language": "latvian"},
    "solr.StemmerOverrideFilterFactory": {"type": "stemmer_override", "rules_path": ">dictionary", "ignoreCase": ">ignoreCase"},
    "solr.PortugueseLightStemFilterFactory": {"type": "stemmer", "language": "light_portuguese"},
    "solr.TurkishLowerCaseFilterFactory": {"type": "stemmer", "language": "turkish"},
}

custom_tokenizers = {}

custom_token_filters = {}

custom_analyzers = {}

mappings = {
    "runtime": {},
    "properties": {},
    "dynamic_templates": [],
}

for a in rootElement.findall('fieldType'):
    if a.attrib["name"] == "random":
        # skip 
        pass
    elif a.attrib["name"] not in BASIC_TYPES.keys():
        for a1 in a.findall('analyzer'):
            custom_analyzer = {"type": "custom", "tokenizer": "standard", "filter": []}
            for tokenizer in a1.findall("tokenizer"):
                tok_klass = tokenizer.attrib["class"]
                if tok_klass not in TOKENIZERS.keys():
                    print("Unknown tokenizer: ", tokenizer.tag, tokenizer.attrib)
                else:
                    if isinstance(TOKENIZERS[tok_klass], dict):
                        tokenizer_name = tok_klass.replace(".", "_") + "_" + TOKENIZERS[tok_klass]["type"]
                        custom_tokenizers[tokenizer_name] = {}
                        for k,v in TOKENIZERS[tok_klass].items():
                            if v.startswith(">"):
                                if v[1:] in tokenizer.attrib:
                                    custom_tokenizers[tokenizer_name][k] = tokenizer.attrib[v[1:]]
                            else:
                                custom_tokenizers[tokenizer_name][k] = v
                        custom_analyzer["tokenizer"] = tokenizer_name
                    else:
                        custom_analyzer["tokenizer"] = TOKENIZERS[tok_klass]
            
            for token_filter in a1.findall("filter"):
                tf_klass = token_filter.attrib["class"]
                if tf_klass not in TOKEN_FILTERS.keys():
                    print("Unknown token_filter: ", token_filter.tag, token_filter.attrib)
                else:
                    if isinstance(TOKEN_FILTERS[tf_klass], dict):
                        tf_name = tf_klass.replace(".", "_") + "_" + TOKEN_FILTERS[tf_klass]["type"]
                        custom_token_filters[tf_name] = {}
                        for k,v in TOKEN_FILTERS[tf_klass].items():
                            if v.startswith(">"):
                                if v[1:] in token_filter.attrib:
                                    custom_token_filters[tf_name][k] = token_filter.attrib[v[1:]]
                            else:
                                custom_token_filters[tf_name][k] = v
                        custom_analyzer["filter"].append(tf_name)
                    else:
                        custom_analyzer["filter"].append(TOKEN_FILTERS[tf_klass])

            if a1.attrib.get("type") in ["index", None]:
                custom_analyzers["%s_index" % a.attrib["name"]] = custom_analyzer

            if a1.attrib.get("type") in ["query", None]:
                custom_analyzers["%s_query" % a.attrib["name"]] = custom_analyzer

ATTRS_MAP = {
    "indexed": "index",
    "stored": "store",
    "docValues": "doc_values",
}

for a in rootElement.findall('field'):
    name = a.attrib["name"]
    type = a.attrib["type"]

    extra_attrs = set(a.attrib.keys()).difference({"name", "type", "indexed", "stored", "docValues", "multiValued"})
    if any(extra_attrs):
        print("Unknown attrs:", a.tag, name, extra_attrs)
    
    attrs = {}
    for k, v in a.attrib.items():
        if k in ATTRS_MAP:
            attrs[ATTRS_MAP[k]] = v

    index_analyzer = type not in BASIC_TYPES and ("%s_index" % type) in custom_analyzers and ("%s_index" % type) or None
    query_analyzer = type not in BASIC_TYPES and ("%s_query" % type) in custom_analyzers and ("%s_query" % type) or None

    if type == "random":
        mappings["runtime"].update({name: {
            "type": "double",
            "script": {
                "source": "Math.random()",
            }
        }})
    else:
        mappings["properties"][name] = {
            "type": BASIC_TYPES.get(type, "text"),
            **attrs
        }

        if index_analyzer:
            mappings["properties"][name]["analyzer"] = index_analyzer
        if query_analyzer:
            mappings["properties"][name]["search_analyzer"] = query_analyzer


for a in rootElement.findall('dynamicField'):
    pattern = a.attrib["name"]
    type = a.attrib["type"]

    extra_attrs = set(a.attrib.keys()).difference({"name", "type", "indexed", "stored", "docValues", "multiValued"})
    if any(extra_attrs):
        print("Unknown attrs:", a.tag, pattern, extra_attrs)
    
    attrs = {}
    for k, v in a.attrib.items():
        if k in ATTRS_MAP:
            attrs[ATTRS_MAP[k]] = v

    index_analyzer = type not in BASIC_TYPES and ("%s_index" % type) in custom_analyzers and ("%s_index" % type) or None
    query_analyzer = type not in BASIC_TYPES and ("%s_query" % type) in custom_analyzers and ("%s_query" % type) or None

    mapping = {
        "type": BASIC_TYPES.get(type, "text"),
        **attrs
    }
    if index_analyzer:
        mapping["analyzer"] = index_analyzer
    if query_analyzer:
        mapping["search_analyzer"] = query_analyzer

    mappings["dynamic_templates"].append({
        "%s_%s" % (type, pattern): {
          "match": pattern,
          "mapping": mapping
        }
    })

for a in rootElement.findall('copyField'):
    src = a.attrib["source"]
    dst = a.attrib["dest"]

    if src not in mappings["properties"]:
        print("Unknown source field:", a.tag, src)
        continue

    if dst not in mappings["properties"]:
        print("Unknown dest field:", a.tag, dst)
        continue

    mappings["properties"][src]["copy_to"] = dst

analysis = {"analyzer": custom_analyzers, "filter": custom_token_filters, "tokenizer": custom_tokenizers}

index_data = {
    "settings": {
        "analysis": analysis
    },
    "mappings": mappings
}

json.dump(index_data, open(sys.argv[1] + ".json", "w"), indent=2, sort_keys=True)