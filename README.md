# Corpus Annotator
A python text-based program that allows consistent collaborative annotation of textual corpora.
The program need to be stored and used in a shared machine.

## Setup

The first user need to setup the program, giving it the necessary files to allow posterior annotation sessions.
To setup, run `corpus_annotator.py --mode setup` adding the mandatory setup arguments: source, target_columns, label_format, annotations_per_text, voting_policy and instructions.

If a previous annotation was carried out in the same directory, there is a chance that hidden annotation files are still present, To setup a new annotation pipeline, these files need to be deleted. You can automatically delete old files during setup, using the option `--force True`.

## Annotation

To start an annotation session as a user, after the setup was successfully concluded, run `corpus_annotator.py --mode annotate --user USER_NAME`. To enter a correct and consistent username in all your annotation sessions is essential to guarantee that no user will label the same text twice.

## Status

To check the progress of the annotation process, run `corpus_annotator.py --mode status`


## Usage and Parameters

usage: corpus_annotator.py [-h] [--mode MODE] [--source SOURCE] [--target_columns TARGET_COLUMNS] [--label_format LABEL_FORMAT]
                           [--annotations_per_text ANNOTATIONS_PER_TEXT] [--voting_policy VOTING_POLICY] [--instructions INSTRUCTIONS]
                           [--force FORCE] [--user USER]

options:
  -h, --help            show this help message and exit

  --mode MODE           The mode in which the program will run (setup/annotate/status/recover)

  --source SOURCE       The adress of the unannotated corpus/dataset .csv file

  --target_columns TARGET_COLUMNS
                        The names of the columns in the source file that contain the texts to be annotated, separated by '/'
  
  --label_format LABEL_FORMAT
                        The annotations format. To more details on how to express the format correctly, run the script with tha argument '--
                        format_help True
  
  --annotations_per_text ANNOTATIONS_PER_TEXT
                        The number of independent annotations per text needed to complete the annotation process
  
  --voting_policy VOTING_POLICY
                        The adress of a python script that contains a function named voting policy, that recieves a complete list of
                        individual annotations and computes the final annotation
  
  --instructions INSTRUCTIONS
                        The adress of the .txt file containing the instructions that need to be displayed for every user before each
                        annotationsession
  
  --force FORCE         If True, this overrides all files from previous setups
  
  --user USER           The name of the user that performing the action

