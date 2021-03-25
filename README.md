# eRecht24-Hugo

This project allows the automated usage of legal documents from e-recht24.de with the hugo static site generator.

It uses the [REST API](https://docs.api.e-recht24.de/) for downloading the current versions, converts the html to markdown and makes them hugo-compatible.

## Requirements

- The usage of the API requires a valid premium subscription for eRecht24
- An API key for the corresponding project has to exist. It can be created in the [eRecht24 Project-Manager](https://www.e-recht24.de/mitglieder/tools/projekt-manager/)
- This project is written in Python 3.8, so it requires a working Python distribution

## Setup

1. Download/Clone the `run.py`, `requirements.txt` and the `config.yaml`
2. Configure the API key by setting an environment variable (`export API_KEY=xxxx`) or by creating a file called `.env` with the following content:
```
API_KEY=xxxxx
```
3. Configure all values in `config.yaml` according to your needs (see below)
4. Install all requirements by running `pip -r requirements.txt`
5. Execute the script (e.g. `python3 run.py`)
6. You should now see the markdown files appear in your output directory

## Configuration

The `config.yaml` is used for configuring the script. The settings are explained here:

**General `config.yaml`:**

|Key|Type|Description|Example|
|---|----|-----------|-------|
|`api_url`|String|The URL of the eRecht24 REST API|`https://api.e-recht24.de`|
|`output_dir`|String|Path to a directory where the generated files will be saved. If it doesn't exist, it will be created.|`output/`|
|`save_html`|Bool|Whether to save html files or not|`false`|
|`pages`|List|List of pages object||

**Pages objects:**

A page object defines a hugo page. A page can consist of multiple documents, which get concatenated (e.g. privacy policy and social media privacy policy).
Each page object contains a header template for hugo, a filename and a list of document objects.

|Key|Type|Description|Example|
|---|----|-----------|-------|
|`filename`|String|The filename for the generated files (`.md` or `.html` get appended)|`imprint.de`|
|`hugo_head`|Object|A yaml object which will be used as header in the markdown-file (hugo uses this). This script searches for some variables (see below) and replaces them.||
|`query`|List|List of document objects||

**Document objects:**

A document object describes a single document and how to fetch it (path in REST API and JSON key in response).

|Key|Type|Description|Example|
|---|----|-----------|-------|
|`path`|String|The path in the REST API used to fetch this document|`/v1/imprint`|
|`json_key`|String|The key used to get the html for this document out of the JSON response|`html_de`|

**Replacements:**

When building the markdown-files, the script prepends the hugo header before the document's content. Therefore, it uses the `hugo_head` value of the page object and does some replacements. The following table defines, which values can be inserted:

|Placeholder|Description|
|-----------|-----------|
|`H1_TEXT`  |If this placeholder is present in a template, the script searches for the first h1 heading in the markdown, removes it from the markdown and puts it into the hugo-header.|
|`PUBLISH_DATE`|This placeholder will be replaced by the smallest creation date of the documents included in this page|
|`MAX_DATE`|This placeholder will be replaced by the greatest modified date of the documents included in this page|