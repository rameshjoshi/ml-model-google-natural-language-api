{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "1f41aa21-14c7-4194-b93f-f9f5c854a1d6",
   "metadata": {},
   "source": [
    "# Run the following command to index the sample files:\r\n",
    "\r\n",
    "python classify_text_tutorial.py index emails\r\n",
    "Observe a new file, index.json, was created and contains the text# .\r\n",
    "\r\n",
    "Re-open the Cloud Editor to see the new index.json file. Click the file to open it and review the returned JSON."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "ce958de0-0d22-4722-9e24-1a651ec3597b",
   "metadata": {},
   "outputs": [],
   "source": [
    "#!/usr/bin/env python\n",
    "\n",
    "\n",
    "\"\"\"Using the classify_text method to find content categories of text files,\n",
    "Then use the content category labels to compare text similarity.\n",
    "\n",
    "For more information, see the tutorial page at\n",
    "https://cloud.google.com/natural-language/docs/classify-text-tutorial.\n",
    "\"\"\"\n",
    "\n",
    "# [START language_classify_text_tutorial_imports]\n",
    "import argparse\n",
    "import io\n",
    "import json\n",
    "import os\n",
    "\n",
    "from google.cloud import language_v1\n",
    "import numpy\n",
    "import six\n",
    "\n",
    "# [END language_classify_text_tutorial_imports]\n",
    "\n",
    "\n",
    "# [START language_classify_text_tutorial_classify]\n",
    "def classify(text, verbose=True):\n",
    "    \"\"\"Classify the input text into categories.\"\"\"\n",
    "\n",
    "    language_client = language_v1.LanguageServiceClient()\n",
    "\n",
    "    document = language_v1.Document(\n",
    "        content=text, type_=language_v1.Document.Type.PLAIN_TEXT\n",
    "    )\n",
    "    response = language_client.classify_text(request={\"document\": document})\n",
    "    categories = response.categories\n",
    "\n",
    "    result = {}\n",
    "\n",
    "    for category in categories:\n",
    "        # Turn the categories into a dictionary of the form:\n",
    "        # {category.name: category.confidence}, so that they can\n",
    "        # be treated as a sparse vector.\n",
    "        result[category.name] = category.confidence\n",
    "\n",
    "    if verbose:\n",
    "        print(text)\n",
    "        for category in categories:\n",
    "            print(\"=\" * 20)\n",
    "            print(\"{:<16}: {}\".format(\"category\", category.name))\n",
    "            print(\"{:<16}: {}\".format(\"confidence\", category.confidence))\n",
    "\n",
    "    return result\n",
    "\n",
    "\n",
    "# [END language_classify_text_tutorial_classify]\n",
    "\n",
    "\n",
    "# [START language_classify_text_tutorial_index]\n",
    "def index(path, index_file):\n",
    "    \"\"\"Classify each text file in a directory and write\n",
    "    the results to the index_file.\n",
    "    \"\"\"\n",
    "\n",
    "    result = {}\n",
    "    for filename in os.listdir(path):\n",
    "        file_path = os.path.join(path, filename)\n",
    "\n",
    "        if not os.path.isfile(file_path):\n",
    "            continue\n",
    "\n",
    "        try:\n",
    "            with io.open(file_path, \"r\") as f:\n",
    "                text = f.read()\n",
    "                categories = classify(text, verbose=False)\n",
    "\n",
    "                result[filename] = categories\n",
    "        except Exception:\n",
    "            print(\"Failed to process {}\".format(file_path))\n",
    "\n",
    "    with io.open(index_file, \"w\", encoding=\"utf-8\") as f:\n",
    "        f.write(json.dumps(result, ensure_ascii=False))\n",
    "\n",
    "    print(\"Texts indexed in file: {}\".format(index_file))\n",
    "    return result\n",
    "\n",
    "\n",
    "# [END language_classify_text_tutorial_index]\n",
    "\n",
    "\n",
    "def split_labels(categories):\n",
    "    \"\"\"The category labels are of the form \"/a/b/c\" up to three levels,\n",
    "    for example \"/Computers & Electronics/Software\", and these labels\n",
    "    are used as keys in the categories dictionary, whose values are\n",
    "    confidence scores.\n",
    "\n",
    "    The split_labels function splits the keys into individual levels\n",
    "    while duplicating the confidence score, which allows a natural\n",
    "    boost in how we calculate similarity when more levels are in common.\n",
    "\n",
    "    Example:\n",
    "    If we have\n",
    "\n",
    "    x = {\"/a/b/c\": 0.5}\n",
    "    y = {\"/a/b\": 0.5}\n",
    "    z = {\"/a\": 0.5}\n",
    "\n",
    "    Then x and y are considered more similar than y and z.\n",
    "    \"\"\"\n",
    "    _categories = {}\n",
    "    for name, confidence in six.iteritems(categories):\n",
    "        labels = [label for label in name.split(\"/\") if label]\n",
    "        for label in labels:\n",
    "            _categories[label] = confidence\n",
    "\n",
    "    return _categories\n",
    "\n",
    "\n",
    "def similarity(categories1, categories2):\n",
    "    \"\"\"Cosine similarity of the categories treated as sparse vectors.\"\"\"\n",
    "    categories1 = split_labels(categories1)\n",
    "    categories2 = split_labels(categories2)\n",
    "\n",
    "    norm1 = numpy.linalg.norm(list(categories1.values()))\n",
    "    norm2 = numpy.linalg.norm(list(categories2.values()))\n",
    "\n",
    "    # Return the smallest possible similarity if either categories is empty.\n",
    "    if norm1 == 0 or norm2 == 0:\n",
    "        return 0.0\n",
    "\n",
    "    # Compute the cosine similarity.\n",
    "    dot = 0.0\n",
    "    for label, confidence in six.iteritems(categories1):\n",
    "        dot += confidence * categories2.get(label, 0.0)\n",
    "\n",
    "    return dot / (norm1 * norm2)\n",
    "\n",
    "\n",
    "# [START language_classify_text_tutorial_query]\n",
    "def query(index_file, text, n_top=3):\n",
    "    \"\"\"Find the indexed files that are the most similar to\n",
    "    the query text.\n",
    "    \"\"\"\n",
    "\n",
    "    with io.open(index_file, \"r\") as f:\n",
    "        index = json.load(f)\n",
    "\n",
    "    # Get the categories of the query text.\n",
    "    query_categories = classify(text, verbose=False)\n",
    "\n",
    "    similarities = []\n",
    "    for filename, categories in six.iteritems(index):\n",
    "        similarities.append((filename, similarity(query_categories, categories)))\n",
    "\n",
    "    similarities = sorted(similarities, key=lambda p: p[1], reverse=True)\n",
    "\n",
    "    print(\"=\" * 20)\n",
    "    print(\"Query: {}\\n\".format(text))\n",
    "    for category, confidence in six.iteritems(query_categories):\n",
    "        print(\"\\tCategory: {}, confidence: {}\".format(category, confidence))\n",
    "    print(\"\\nMost similar {} indexed texts:\".format(n_top))\n",
    "    for filename, sim in similarities[:n_top]:\n",
    "        print(\"\\tFilename: {}\".format(filename))\n",
    "        print(\"\\tSimilarity: {}\".format(sim))\n",
    "        print(\"\\n\")\n",
    "\n",
    "    return similarities\n",
    "\n",
    "\n",
    "# [END language_classify_text_tutorial_query]\n",
    "\n",
    "\n",
    "# [START language_classify_text_tutorial_query_category]\n",
    "def query_category(index_file, category_string, n_top=3):\n",
    "    \"\"\"Find the indexed files that are the most similar to\n",
    "    the query label.\n",
    "\n",
    "    The list of all available labels:\n",
    "    https://cloud.google.com/natural-language/docs/categories\n",
    "    \"\"\"\n",
    "\n",
    "    with io.open(index_file, \"r\") as f:\n",
    "        index = json.load(f)\n",
    "\n",
    "    # Make the category_string into a dictionary so that it is\n",
    "    # of the same format as what we get by calling classify.\n",
    "    query_categories = {category_string: 1.0}\n",
    "\n",
    "    similarities = []\n",
    "    for filename, categories in six.iteritems(index):\n",
    "        similarities.append((filename, similarity(query_categories, categories)))\n",
    "\n",
    "    similarities = sorted(similarities, key=lambda p: p[1], reverse=True)\n",
    "\n",
    "    print(\"=\" * 20)\n",
    "    print(\"Query: {}\\n\".format(category_string))\n",
    "    print(\"\\nMost similar {} indexed texts:\".format(n_top))\n",
    "    for filename, sim in similarities[:n_top]:\n",
    "        print(\"\\tFilename: {}\".format(filename))\n",
    "        print(\"\\tSimilarity: {}\".format(sim))\n",
    "        print(\"\\n\")\n",
    "\n",
    "    return similarities\n",
    "\n",
    "\n",
    "# [END language_classify_text_tutorial_query_category]\n",
    "\n",
    "\n",
    "if __name__ == \"__main__\":\n",
    "    parser = argparse.ArgumentParser(\n",
    "        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter\n",
    "    )\n",
    "    subparsers = parser.add_subparsers(dest=\"command\")\n",
    "    classify_parser = subparsers.add_parser(\"classify\", help=classify.__doc__)\n",
    "    classify_parser.add_argument(\n",
    "        \"text\",\n",
    "        help=\"The text to be classified. \" \"The text needs to have at least 20 tokens.\",\n",
    "    )\n",
    "    index_parser = subparsers.add_parser(\"index\", help=index.__doc__)\n",
    "    index_parser.add_argument(\n",
    "        \"path\", help=\"The directory that contains \" \"text files to be indexed.\"\n",
    "    )\n",
    "    index_parser.add_argument(\n",
    "        \"--index_file\", help=\"Filename for the output JSON.\", default=\"index.json\"\n",
    "    )\n",
    "    query_parser = subparsers.add_parser(\"query\", help=query.__doc__)\n",
    "    query_parser.add_argument(\"index_file\", help=\"Path to the index JSON file.\")\n",
    "    query_parser.add_argument(\"text\", help=\"Query text.\")\n",
    "    query_category_parser = subparsers.add_parser(\n",
    "        \"query-category\", help=query_category.__doc__\n",
    "    )\n",
    "    query_category_parser.add_argument(\n",
    "        \"index_file\", help=\"Path to the index JSON file.\"\n",
    "    )\n",
    "    query_category_parser.add_argument(\"category\", help=\"Query category.\")\n",
    "\n",
    "    args = parser.parse_args()\n",
    "\n",
    "    if args.command == \"classify\":\n",
    "        classify(args.text)\n",
    "    if args.command == \"index\":\n",
    "        index(args.path, args.index_file)\n",
    "    if args.command == \"query\":\n",
    "        query(args.index_file, args.text)\n",
    "    if args.command == \"query-category\":\n",
    "        query_category(args.index_file, args.category)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.1"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
