import ezsheets
import time
from os import listdir
from pathlib import Path
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from pprint import pprint
import re
import csv

def main(path, decklist_file):
    working_file = path + decklist_file
    decklist_df = pd.read_csv(working_file)
    print(decklist_df.head(10).to_string())

    print(decklist_df.groupby(['Card']).size().to_frame('size').reset_index().sort_values(['Card'], ascending=False).head(15))
    print(decklist_df.groupby(['Card']).size().head(15))
    print("\n\n\n\n")
    decklist_df_sorted = decklist_df.copy()
    # decklist_df_sorted = decklist_df_sorted.groupby('Card', sort=True).size().reset_index()
    most_played_cards = decklist_df_sorted.groupby(['Card'])['Sideboard'] \
        .size().reset_index(name='Total') \
        .sort_values(['Total'], ascending=False).head(10)
    most_played_main = decklist_df_sorted[decklist_df_sorted['Sideboard'] ==0].groupby(['Card'])['Sideboard'] \
        .size().reset_index(name='Total') \
        .sort_values(['Total'], ascending=False).head(10)
    most_played_sb = decklist_df_sorted[decklist_df_sorted['Sideboard'] == 1].groupby(['Card'])['Sideboard'] \
        .size().reset_index(name='Total') \
        .sort_values(['Total'], ascending=False).head(10)
    most_played_companion = decklist_df_sorted[decklist_df_sorted['Companion'] == 1].groupby(['Card'])['Sideboard'] \
        .size().reset_index(name='Total') \
        .sort_values(['Total'], ascending=False).head(10)
    print(most_played_cards.head(15).to_string(index=False))
    print(most_played_main.head(15).to_string(index=False))
    print(most_played_sb.head(15).to_string(index=False))

    # with open('{0}{1}_Cards.txt'.format(path, player_name_for_file_name), 'w', newline='') as deckfile:
    #     line_writer = csv.writer(deckfile, delimiter=' ')
    #
    #     for i in range(len(compressed_df_main)):
    #         deckfile.write('{0} {1}\n'.format(compressed_df_main['Number'][i], compressed_df_main['Card'][i]))


path = 'C:\\Users\\JaysC\\Dropbox\\Coding\\Python\\MtG\\'
decklist_file = 'all_decklists.csv'

##Lotus Box 5-17-2020
path_for_list = 'C:\\Users\\JaysC\\Dropbox\\Coding\\Python\\MtG\\Decklists\\'
decklist_csv='tournament__all_decklists_for_sql.csv'


main(path=path_for_list, decklist_file=decklist_csv)

