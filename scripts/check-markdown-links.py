#!/usr/bin/env python3

import collections
import glob
import itertools
import os
import re
import sys

class ValidationError(Exception):
    pass

class LinkTopology:
    def __init__(self, anchors, links):
        self.anchors = anchors
        self.links = links

def deduplicate(items):
    return list(collections.OrderedDict.fromkeys(items))

def pad(string, length):
    if len(string) >= length:
        return string
    else:
        return string + " " * (length - len(string))

def get_link_anchor(header, prev_anchors):
    # https://github.com/thlorenz/anchor-markdown-header/blob/56f77a232ab1915106ad1746b99333bf83ee32a2/anchor-markdown-header.js
    anchor = header
    anchor = anchor.casefold()
    anchor = anchor.replace(" ", "-")
    anchor = re.sub(r"%([abcdef]|\d){2,2}", "", anchor, re.IGNORECASE)
    anchor = re.sub(r"[/?!:\[\]`.,()*\"';{}+=<>~\$|#@&–—]", "", anchor)
    anchor = re.sub(
        r"[。？！，、；：“”【】（）〔〕［］﹃﹄“ ”‘’﹁﹂—…－～《》〈〉「」]",
        "", anchor)
    if anchor in prev_anchors:
        for count in itertools.count(1):
            new_anchor = "{}-{}".format(anchor, count)
            if new_anchor not in prev_anchors:
                anchor = new_anchor
                break
    return anchor

def normalize_label(label):
    label = label.casefold()
    label = label.strip()
    label = re.sub(r"\s+", " ", label)
    return label

def get_link_topology(markdown, filename):
    errors = []
    anchors = []
    # Search for headings
    for match in re.finditer(r"^#+(.+)", markdown, re.MULTILINE):
        header = match.group(1).strip()
        anchors.append(get_link_anchor(header, anchors))
    labels = {}
    # Search for label definitions
    for match in re.finditer(r"^\[(.+?)\]: (.+)", markdown, re.MULTILINE):
        label, link = match.groups()
        label = normalize_label(label)
        if label in labels:
            errors.append("In {}: Label {} appears twice"
                          .format(repr(filename), repr(label)))
        labels[label] = link
    # Search for direct links
    links = set()
    for match in re.finditer(
            r"\[[^\]\)]+?\]\((.+?)\)", markdown, re.MULTILINE):
        link = match.group(1)
        links.add(link)
    # Search for label links
    for match in re.finditer(
            r"\[[^\]\)]+?\]\[(.+?)\]", markdown, re.MULTILINE):
        label = match.group(1)
        label = normalize_label(label)
        if label not in labels:
            errors.append("In {}: Label {} is undefined"
                          .format(repr(filename), repr(label)))
            continue
        link = labels[label]
        links.add(link)
    # Search for shorthand label links
    for match in re.finditer(
            r"[^\[\(]\[([^\]\)]+?)\][^\[\(]", markdown, re.MULTILINE):
        label = match.group(1)
        label = normalize_label(label)
        if label not in labels:
            errors.append("In {}: Label {} is undefined"
                          .format(repr(filename), repr(label)))
            continue
        link = labels[label]
        links.add(link)
    return LinkTopology(anchors, links), errors

def validate_files(filenames):
    filenames = deduplicate(filenames)
    errors = []
    topologies = {}
    checked_links = {}
    unchecked_links = {}
    failed_links = {}
    for filename in filenames:
        checked_links[filename] = []
        unchecked_links[filename] = []
        failed_links[filename] = []
        with open(filename) as f:
            markdown = f.read()
        topology, new_errors = get_link_topology(markdown, filename)
        topologies[filename] = topology
        errors.extend(new_errors)
        for error in new_errors:
            # Increment the error counter
            failed_links[filename].append(None)
    for filename in filenames:
        for link in topologies[filename].links:
            if re.match(r"^(mailto|https?):", link):
                unchecked_links[filename].append(link)
                continue
            match = re.match(r"^(?:/([^#]+))?(?:#(.+))?", link)
            if not match:
                errors.append("In {}: Malformed link {}"
                              .format(repr(filename), repr(link)))
                failed_links[filename].append(link)
                continue
            path, anchor = match.groups()
            if path and path.endswith("/"):
                path = path[:-1]
            fname = path + ".md" if path else filename
            if fname not in filenames:
                errors.append("In {}: Path {} does not exist"
                              .format(repr(filename), repr(path)))
                failed_links[filename].append(link)
                continue
            if anchor and anchor not in topologies[fname].anchors:
                errors.append("In {}: Anchor {} in file {} does not exist"
                              .format(repr(filename),
                                      repr(anchor),
                                      repr(fname)))
                failed_links[filename].append(link)
                continue
            checked_links[filename].append(link)
    max_length = max(map(len, filenames))
    if errors:
        for error in errors:
            print(error)
        print()
    for filename in filenames:
        print("{} | {} checked, {} unchecked, {} errors"
              .format(pad(filename, max_length),
                      len(checked_links[filename]),
                      len(unchecked_links[filename]),
                      len(failed_links[filename])))
    return not errors

def main(*args):
    exec_name, *args = args
    if len(args) != 1:
        print("usage: {} <docs-dir>".format(exec_name))
        return False
    docs_dir = args[0]
    os.chdir(docs_dir)
    return validate_files(glob.glob("**.md"))

if __name__ == "__main__":
    sys.exit(0 if main(*sys.argv) else 1)
