# Lesson Plan Parse MBSSE

The Ministry of Basic and Senior Secondary Education (MBSSE) of Sierra Leone publishes a set of lesson plans for Maths and Language Arts on their [online knowledge platform](https://mbsseknowledgeplatform.gov.sl). The lesson plans are in pdf format, and cover all grade levels across Primary, Junior Secondary (JSS), and Senior Seconday (SSS).

Here we share python code for parsing the raw text of the lesson plan pdfs into structured json and subsequently cleaning the text so that it is suitable for human consumption. We also share the following files, which are the input to and outputs from this process:

- input: [raw text of the lesson plans](https://fabdatastorage.blob.core.windows.net/mbsse-lp/mbsseKP_files_lessonplans.json.gz)
- output 1: [structured json of the parsed lesson plans](https://fabdatastorage.blob.core.windows.net/mbsse-lp/mbsseKP_files_lessonplans_parsed.json.gz)
- output 2: [structured json cleaned for human consumption](https://fabdatastorage.blob.core.windows.net/mbsse-lp/mbsseKP_files_lessonplans_parsed_cleaned.json.gz)

## Step 1: Installation

First, clone the repository to some location on your computer (we'll call it `INSTALL_DIR`, but replace that with the full path to the location on your computer, e.g. `C:\my_code_directory`):

```bash
cd INSTALL_DIR
git clone https://github.com/AI-for-Education/lesson-plan-parse-mbsse.git
```

This will create the folder `INSTALL_DIR/lesson-plan-parse-mbsse`, which we will now refer to as `REPO_DIR`

The package can be installed into an existing python environment with:

```bash
cd REPO_DIR
pip install -r requirements.txt
```

For conda users, a conda environment.yml file is also included, which can be used to create a new python environment and install the package inside it in one step.

```bash
cd REPO_DIR
conda env create -f environment.yml
```

## Step 2: Set environment variables

Although most of the steps involved in parsing the lesson plans are rule-based, all cleaning steps use LLMs from OpenAI's API. In order for the scripts to run, you will need to have an OpenAI API key, which you can set by creating a file called `.env` in the root directory of the repository. This file should contain the line:

```.env
OPENAI_API_KEY=your_api_key
```

where `your_api_key` is replaced with the value of your OpenAI API key.

## Step 3: Parse lesson plans

The script for parsing the lesson plans is `REPO_DIR/scripts/parse_mbsseKP_lessonplans.py`. You can either run this from the command line with:

```bash
python REPO_DIR/scripts/parse_mbsseKP_lessonplans.py
```

or you can run it interactively in an IDE (like VSCode) to understand each of the steps.

The raw text of the lesson plans will first be downloaded to `REPO_DIR/mbsseKP_files_lessonplans.json`, and at the end of the process `REPO_DIR/mbsseKP_files_lessonplans_parsed.json` will be created.

## Step 4: Clean parsed lesson plans

The parsed lesson plans produced in Step 3 are fine to use as inputs to LLMs, but for human readability they suffer from a range of formatting errors resulting from the extraction of the raw text from pdf. The process of correcting these kinds of errors, and generally improving formatting overall (including inserting markdown tables, LaTeX formulae), is perfectly suited to an LLM like `gpt-4o`.

The script for running this cleaning process is `REPO_DIR/scripts/parse_mbsseKP_lessonplans.py`. The ouput from this process is `REPO_DIR/mbsseKP_files_lessonplans_parsed.json`. This file is created at launch, and updated as the process runs. The full process over all lesson plans can be quite expensive (although prices are descreasing), so the script can be cancelled at any time and this output file supports resuming from where it left off.