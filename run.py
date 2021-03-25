import os
import requests
import yaml
import re
import html
from dotenv import load_dotenv

# define config object
from typing import List

config = {
    "api_key": "",
    "api_url": "",
    "output_dir": "",
    "save_html": False,
    "docs": [],
}

# load config from file
with open('config.yaml') as file:
    config.update(yaml.full_load(file))

# load API key from env
load_dotenv()
config['api_key'] = os.getenv("API_KEY")

# define regex patterns
h1_pattern = re.compile(r'<h1>(.*?)</h1>', flags=re.IGNORECASE | re.DOTALL)
h2_pattern = re.compile(r'<h2>(.*?)</h2>', flags=re.IGNORECASE | re.DOTALL)
h3_pattern = re.compile(r'<h3>(.*?)</h3>', flags=re.IGNORECASE | re.DOTALL)
h4_pattern = re.compile(r'<h4>(.*?)</h4>', flags=re.IGNORECASE | re.DOTALL)
h5_pattern = re.compile(r'<h5>(.*?)</h5>', flags=re.IGNORECASE | re.DOTALL)
h6_pattern = re.compile(r'<h6>(.*?)</h6>', flags=re.IGNORECASE | re.DOTALL)
br_pattern = re.compile(r'<br\s?/>\s?', flags=re.IGNORECASE | re.DOTALL)
strong_pattern = re.compile(r'<strong>(.*?)</strong>', flags=re.IGNORECASE | re.DOTALL)
p_pattern = re.compile(r'<p>(.*?)</p>', flags=re.IGNORECASE | re.DOTALL)
md_h1_pattern = re.compile(r'# (.*?)\n', flags=re.IGNORECASE | re.DOTALL)


# write string to file
def save_string(filename, string):
    f = open(os.path.join(config['output_dir'], filename), "w")
    f.write(string)
    f.close()


# convert html doc to hugo markdown
def convert_html_to_md(html_doc: str) -> str:
    md = html_doc

    # simplify line breaks
    md = md.replace("\r\n", "\n")

    # replace opening heading-tags
    md = h1_pattern.sub(r'\n# \1\n', md)
    md = h2_pattern.sub(r'\n## \1\n', md)
    md = h3_pattern.sub(r'\n### \1\n', md)
    md = h4_pattern.sub(r'\n#### \1\n', md)
    md = h5_pattern.sub(r'\n##### \1\n', md)
    md = h6_pattern.sub(r'\n###### \1\n', md)

    # rewrite line breaks
    md = br_pattern.sub(r'  \n\n', md)

    # rewrite strong text
    md = strong_pattern.sub(r'**\1**', md)

    # rewrite paragraphs
    md = p_pattern.sub(r'\n\1\n', md)

    # remove double line breaks
    md = re.sub(r'\n{2}', "\n", md)

    # clean string
    md = md.strip() + "\n"

    # unescape html
    md = html.unescape(md)

    return md


def make_hugo_head(md: str, modified_list: List[str], created_list: List[str], template: str) -> str:
    publish_date = min(created_list)
    mod_date = max(modified_list)

    # build hugo head
    tmp_hugo_head = "---\n" + yaml.dump(template) + "---\n\n"
    tmp_hugo_head = tmp_hugo_head.replace("PUBLISH_DATE", publish_date)
    tmp_hugo_head = tmp_hugo_head.replace("MOD_DATE", mod_date)

    if "H1_TEXT" in template:
        # remove h1 heading
        md_h1_match = md_h1_pattern.search(md)
        if not md_h1_match:
            raise Exception("no h1 found, but required for hugo head")
        h1_text = md_h1_match.group(1)
        h1_start_pos, h1_end_pos = md_h1_match.span(0)
        md = md[:h1_start_pos] + md[h1_end_pos:]
        tmp_hugo_head = tmp_hugo_head.replace("H1_TEXT", h1_text)

    # add hugo title to document
    md = tmp_hugo_head + md

    return md


def query(path: str, json_key: str) -> (str, str, str):
    r = requests.get(config['api_url'] + path, headers={"eRecht24": config['api_key']})
    if r.status_code != 200:
        raise Exception("error", r.status_code)

    r_json = r.json()
    html_doc = r_json[json_key]
    created = r_json['created']
    modified = r_json['modified']

    return html_doc, created, modified


def build_page(page_config: dict):
    modified_list = []
    created_list = []

    page_html = ""
    page_md = ""

    for doc in page_config['query']:
        html_doc, created, modified = query(doc['path'], doc['json_key'])

        modified_list.append(modified)
        created_list.append(created)

        page_html += html_doc.strip() + "\n"
        page_md += convert_html_to_md(html_doc) + "\n"

    if config['save_html']:
        save_string(page_config['filename'] + ".html", page_html)

    page_md = make_hugo_head(page_md, modified_list, created_list, template=page_config['hugo_head'])
    save_string(page_config['filename'] + ".md", page_md)


if __name__ == '__main__':
    if not os.path.isdir(config['output_dir']):
        os.mkdir(config['output_dir'])

    for page in config['pages']:
        build_page(page)
