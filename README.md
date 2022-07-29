# Solr schema to ES mapping converter

## Usage

```
python solr2es-mapping.py /path/to/solr/schema.xml
```

it will produce ES mapping in `/path/to/solr/schema.xml.json` 

Then it can be used to create ES indices:

```
curl -H 'Content-Type: application/json' -X PUT localhost:9200/new_index -d @/path/to/solr/schema.xml.json
```

Custom language analyzers are created from Solr definitions instead of reusing ES built-in ones.