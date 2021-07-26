# -*- coding: utf-8 -*-
"""
Created on Fri Jul 23 22:38:30 2021

@author: JaysC

Raw downloaded decklist file from ManaTraders goes in the MT_PATH folder

TODO: Test the ProjectPaths import
TODO: Integrate the writer function: write_deck_to_text_file
TODO: Automate downloading the csv from MT website
"""

#import csv

from pathlib import Path

import pandas as pd

import ProjectPaths

import MtgMeleeUtils as mtg


# CONSTANTS
# TODO: TEST THESE 2 LINES BEFORE DELETING
MT_PATH = 'C:\\Users\\JaysC\\Dropbox\\Coding\\Python\\MtG\\ManaTradersSeries\\'
CBL_LISTS_PATH = f"{MT_PATH}CBL_Lists\\"

MT_PATH = ProjectPaths.MT_PATH
CBL_LISTS_PATH = ProjectPaths.CBL_LISTS_PATH

# FUNCTIONS
def make_new_folder_for_txt_files(month, year):
	"""
	Makes new folder of type "Month Year" (like "July 2021") in the CBL_LISTS_PATH dir
	: return name of newly created folder
	"""
	
	new_folder_name = f'{CBL_LISTS_PATH}{month} {year}\\'
	Path(new_folder_name).mkdir(exist_ok=True)
	
	return new_folder_name
	

def write_deck_to_text_file(compressed_decklist_csv_main, compressed_decklist_csv_sb, file_writer_object):
    '''
    Writes the decklist to a file
    TODO: Compress the decklist in this fn?
    
    :param compressed_decklist_csv_main: DF of maindeck after being collapsed to QTY CARDNAME format
    :param compressed_decklist_csv_sb: DF of sideboard after being collapsed to QTY CARDNAME format
	 :param file_writer_object: File Writer Object to write decklist to

    :return: None
    
    '''
    for i in range(len(compressed_decklist_csv_main)):
        file_writer_object.write(f"{compressed_decklist_csv_main['Number'][i]} {compressed_decklist_csv_main['Card'][i]}\n")
            
        file_writer_object.write("\nSideboard\n")	#Sideboard Divider
    for i in range(len(compressed_decklist_csv_sb)):
        file_writer_object.write(f"{compressed_decklist_csv_sb['Number'][i]} {compressed_decklist_csv_sb['Card'][i]}\n")

def streamdecker_text_files_manatraders(csvOfDecklists, pathForLists):
    """
    Takes csv of all decklists and splits them out into individual txt files for StreamDecker Upload
    :param pathForCSV: Where the decklist csv is
    :param csvOfDecklists: Name of decklist csv (includes ".csv")
	 :param pathForLists: Path to write decklists
    :return: None
    """
    decklist_file_expanded = f"{MT_PATH}{csvOfDecklists}"
    # print(decklist_file_expanded)

    df = pd.read_csv(decklist_file_expanded)
    Player_Usernames = df['Player_Username'].unique()
    # print(Player_Usernames)

    for player in Player_Usernames:
        # print(player)
        dontstrip = [' ', '_', '-']
        Player_Username_for_file_name = "".join(c for c in player if c.isalnum() or c in dontstrip).rstrip()

        single_deck_df_main = df.loc[(df['Player_Username'] == player) &
                                                  (df['Sideboard'] == 0) &
                                                  (df['Companion'] == 0)].copy()
		
        single_deck_df_sb = df.loc[(df['Player_Username'] == player) &
                                              (df['Sideboard'] == 1) &
                                              (df['Companion'] == 0)].copy()

        # print(single_deck_df_main.head(2).to_string())
        # print(single_deck_df_sb.head(2).to_string())

        compressed_df_main = single_deck_df_main.groupby(['Card']) \
                                 .size().reset_index(name='Number').iloc[:, ::-1]
        compressed_df_sb = single_deck_df_sb.groupby(['Card']) \
                               .size().reset_index(name='Number').iloc[:, ::-1]

        ###Trying writing rows at a time
        # print(compressed_df_main.to_string())
        
        with open(f"{pathForLists}{Player_Username_for_file_name}_deck.txt", "w", newline="") as deckfile:
            #line_writer = csv.writer(deckfile, delimiter=' ')

            for i in range(len(compressed_df_main)):
                deckfile.write(f"{compressed_df_main['Number'][i]} {compressed_df_main['Card'][i]}\n")
            
            deckfile.write("\nSideboard\n")	#Sideboard Divider
            for i in range(len(compressed_df_sb)):
                deckfile.write(f"{compressed_df_sb['Number'][i]} {compressed_df_sb['Card'][i]}\n")

    print("Completed Streamdecker Lists")


def main(date, month, year, decklist_filename):
    
	raw_decklists_to_load = f"{MT_PATH}{decklist_filename}.csv"
	expanded_csv_filename = f"{date}_manatraders_expanded.csv"
	path_for_lists = make_new_folder_for_txt_files(month=month, year=year)
	
	df = pd.read_csv(raw_decklists_to_load)
	df_expanded = mtg.expand_decklist(decklist_dataframe=df)
	
	df_expanded.to_csv(f"{MT_PATH}{expanded_csv_filename}")
	print("Saved:", expanded_csv_filename)
	
	streamdecker_text_files_manatraders(
		csvOfDecklists=expanded_csv_filename,
		pathForLists=path_for_lists
		)


date = '210723'
month = 'July'
year = '2021'
filename = 'ManaTraders_SeriesModern_July_2021'

main(date=date, month=month, year=year, decklist_filename=filename)
