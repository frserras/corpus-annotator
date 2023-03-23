#!/usr/bin/env python

"""\
    Corpus Annotator is a text-based tool that allows the collaborative annotation of small
text corpora and datasets stored in .csv files. All users need to have access to the same machine, where the
program will be hosted.

usage: corpus_annotator.py [-h] [--mode MODE] [--source SOURCE] [--target_columns TARGET_COLUMNS] [--label_format LABEL_FORMAT]
                           [--annotations_per_text ANNOTATIONS_PER_TEXT] [--voting_policy VOTING_POLICY] [--instructions INSTRUCTIONS]
                           [--force FORCE] [--user USER]
"""

import argparse
import shutil
import json
import time
import os
import pandas as pd

"""
__author__ = "Felipe Serras"
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Felipe Serras"
__status__ = "Prototype"
"""





'''ARGUMENT PARSING'''

description = """ Corpus Annotator is a text-based tool that allows the collaborative annotation of small
text corpora and datasets stored in .csv files. All users need to have access to the same machine, where the
program will be hosted."""

parser = argparse.ArgumentParser(description=description)

parser.add_argument('--mode', dest='mode', type=str, help='The mode in which the program will run (setup/annotate/status/recover)')
parser.add_argument ('--source', dest='source', type=str, help='The adress of the unannotated corpus/dataset .csv file')
parser.add_argument('--target_columns', dest='target_columns', type=str, help=("The names of the columns in the source file that contain"
                                                                         " the texts to be annotated, separated by '/'"))
parser.add_argument('--label_format', dest='label_format', type=str, help=("The annotations format. To more details on how to express"
                                                                           " the format correctly, run the script with tha argument"
                                                                             " '--format_help True"))
parser.add_argument('--annotations_per_text', dest='annotations_per_text', type=int, help=('The number of independent annotations per text'
                                                                                           ' needed to complete the annotation process'))
parser.add_argument('--voting_policy', dest='voting_policy', type=str, help=('The adress of a python script that contains a function'
                                                                             ' named voting policy, that recieves a complete list of'
                                                                             ' individual annotations and computes the final annotation'))
parser.add_argument('--instructions', dest='instructions', type=str, help=('The adress of the .txt file containing the instructions'
                                                                           ' that need to be displayed for every user before each'
                                                                           ' annotationsession'))
parser.add_argument('--force', dest='force', type=bool, help='If True, this overrides all files from previous setups')

parser.add_argument('--user', dest='user', type=str, help='The name of the user that performing the action')


'''AUXILIARY FUNCTIONS'''


def parse_annotation(format, annotation):
    # void label interrupt labeling session:
    if annotation == '':
        return '__EXIT_SESSION__'
    # ordinary labels:
    else:
        if format == 'str':
            return str(annotation).lower()
        elif format == 'int':
            return int(annotation)
        elif format == 'float':
            return float(annotation)
        elif format == 'bool':
            return bool(annotation)
        # categorical labels:
        else:
            expected_categories = format.split('/')
            annotation = annotation.lower()
            if annotation in expected_categories:
                return annotation
            # invalid categorical label
            else:
                return None


'''MODE FUNCTIONS: a set of functions that process the different possible running modes'''

'''A function that perform the initial setup for corpus annotation, allowing posterior annotation sessions:'''
def setup(args):
    config = {}
    source_df = pd.read_csv(args.source)
    
    # Check if the columns set to be annotated are present in the source corpus:
    target_columns = args.target_columns.split('/')
    for target_column in target_columns:
        try:
            assert target_column in source_df
        except AssertionError:
            print('The informed target columns are invalid.')
            return
    config['target_columns'] = args.target_columns
    
    # Check label format:
    correct_categorical_format = (len(args.label_format.split('/')) > 1)
    if args.label_format in ['str','int', 'float', 'bool'] or correct_categorical_format:
        config['label_format'] = args.label_format
    else:
        print("Error while parsing label format. Run the program with '--format_help True' argument")
        return
    
    # Check the annotations per text parameter, add columns for annotations and users:
    if args.annotations_per_text >=1:
        config['annotations_per_text'] =  args.annotations_per_text
        for i in range(args.annotations_per_text):
            source_df ['Annotation_' + str(i+1)] = ['pending'] * len(source_df)
            source_df ['Annotator_' + str(i+1)] = ['pending'] * len(source_df)
        
    # create and fill up a directory for internal files:
    # verify the existence of a previous setup:
    if os.path.exists('.annotation_files/') or os.path.exists('annotated_corpus.csv'):
        if args.force:
            shutil.rmtree('.annotation_files/')
        else:
            print(('Files from an previous setup are stored in this directory. A new setup will erase these files.'
                   'All information from previous annotations will be lost. If you are sure, repeat the setup command'
                   "with '--force True'"))
            return
    os.mkdir('.annotation_files/')
    
    # copy voting policy script:
    shutil.copyfile(args.voting_policy, '.annotation_files/voting_police.py')
    
    # copy instructions file:
    shutil.copyfile(args.instructions, '.annotation_files/instructions.txt')
    
    # save config file:
    with open('.annotation_files/config.json', 'w') as f:
        json.dump(config, f)
    # save local copies of the corpus with annotation columns:
    source_df.to_csv('.annotation_files/annotated_corpus_backup.csv', index=False)
    source_df.to_csv('annotated_corpus.csv', index=False)
    
    print('Setup completed successfully. You can start annotation sessions now :)')
    return


'''A function that execute a annotation session, where the user can label several texts'''
def annotate(args):
    if args.user == None:
        print("Please, specify who you are using the argument '--user YOUR_NAME'")
        return

    with open('.annotation_files/config.json', 'r') as f:
        config = json.load(f)
    annotation_start = time.time()
    
    # show annotation instructions:
    with open('.annotation_files/instructions.txt', 'r') as f:
        print(f.read())
    
    #annotation loop:
    annotation_session_on = True
    while annotation_session_on:
        corpus_df = pd.read_csv('annotated_corpus.csv')
        
        # select rows without annotation, in a way that garantees no user will label the same text twice
        # and that all texts will receive a label as soon as possible:
        for i in range(config['annotations_per_text']+1):
            iteration_df = corpus_df[corpus_df['Annotation_'+ str(i+1)] == 'pending']
            for j in range(config['annotations_per_text']):
                if len(iteration_df) == 0:
                    break
                iteration_df = iteration_df.loc[corpus_df['Annotator_'+ str(j+1)] != args.user]
            
            if len(iteration_df) > 0:
                annotation_column = 'Annotation_'+ str(i+1)
                annotator_column = 'Annotator_'+ str(i+1)
                break
            elif i == config["annotations_per_text"]-1:
                print('You completed your part on the labeling process! Thank you!. :)')
                return
            
        # Randomly select the text to be labeled from the set of selected texts and get the label:
        row = iteration_df.sample().index[0]
        target_columns = config['target_columns'].split('/')
        text_to_annotate = ''
        for target_column in target_columns:
            text_to_annotate += ("\t" + target_column + ':' + iteration_df[target_column][row] + '\n') 
        # annotation menu:
        correctly_annotated = False
        while not correctly_annotated:
            print('TEXT TO ANNOTATE:')
            print(text_to_annotate)
            raw_annotation = input('\nEnter Your Annotation (' + config['label_format'] + ')[Press Enter to quit the session]:')
            annotation = parse_annotation(config['label_format'], raw_annotation)
            if annotation == '__EXIT_SESSION__':
                correctly_annotated = True
                annotation_session_on = False
            elif annotation is not None:
                correctly_annotated = True
            else:
                print('Invalid class. Please note the correct label format: ' + config['label_format'] )
        # add annotation and user to dataframe:
        if annotation != '__EXIT_SESSION__':
            corpus_df.at[row, annotation_column] = annotation
            corpus_df.at[row,annotator_column] = args.user
            corpus_df.to_csv('.annotation_files/annotated_corpus_backup.csv', index=False)
            corpus_df.to_csv('annotated_corpus.csv', index=False)
        else:
            annotation_end = time.time()
    return


'''A function that show the current status of the annotation process:'''
def status():
        with open('.annotation_files/config.json', 'r') as f:
            config = json.load(f)
        corpus_df = pd.read_csv('annotated_corpus.csv')
        pending_annotations = 0
        for i in range(config['annotations_per_text']):
            column_counts = corpus_df['Annotation_'+str(i+1)].value_counts()
            if 'pending' in column_counts:
                pending_annotations += column_counts['pending']
        annotation_percentage = (1 - (pending_annotations/(config['annotations_per_text']*len(corpus_df))))*100
        print('The corpus is ' + str(annotation_percentage) + '% annotated')


'''A function that rebuild the corpus to fix any problems caused by competing labeling sessions:'''
def recover():
    print("Sorry, this feature is currently in development and unavailable.")
    return


'''A main function that select and call the correct running mode:'''
def main(args):
    if args.mode == 'setup':
        setup(args)
    elif args.mode == 'annotate' or args.mode == None:
        annotate(args)
    elif args.mode == 'status':
        status()
    elif args.mode == 'recover':
        recover()
    else:
        print('Unknow mode. The allowed modes are: setup, annotate, status, recover.')


main(parser.parse_args())
