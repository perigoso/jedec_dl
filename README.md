# jedec_dl
dowloader tool for JEDEC standards

## Usage

```
usage: jedec_dl [-h] [-o OUTPUT] [-c CONFIG] [-l LIST] [-u USERNAME] [-p PASSWORD] [--no-variations NO_VARIATIONS] [docs ...]

Downloads JEDEC documents from their website

positional arguments:
  docs                  List of documents to download

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output directory
  -c CONFIG, --config CONFIG
                        Path to config file
  -l LIST, --list LIST  Path to list file of target documents
  -u USERNAME, --username USERNAME
                        Username for JEDEC account
  -p PASSWORD, --password PASSWORD
                        Password for JEDEC account
  --no-variations NO_VARIATIONS
                        Do not look for alternative document naming
```
