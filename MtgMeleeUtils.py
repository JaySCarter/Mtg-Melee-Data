### Packages
import ezsheets
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import random
import csv

### Other stuff to import ###
from pathlib import Path
import time
from os import listdir
import numpy as np
import shutil
import datetime
from collections import defaultdict
from collections import OrderedDict
from pprint import pprint


def most_played_cards_to_df(path, decklist_file, dataframe_flag=False, files_to_return='All'):
    files_to_return_main_flag = False
    files_to_return_sideboard_flag = False
    files_to_return_companion_flag = False
    files_to_return_all_flag = False

    if dataframe_flag:
        decklist_df = decklist_file
    else:
        working_file = path + decklist_file
        decklist_df = pd.read_csv(working_file)

    if files_to_return.lower().find('all') > 0:
        files_to_return_main_flag = True
        files_to_return_sideboard_flag = True
        files_to_return_companion_flag = True
        files_to_return_all_flag = True
    if files_to_return.lower().find('main') > 0:
        files_to_return_main_flag = True
    if files_to_return.lower().find('board') > 0:
        files_to_return_sideboard_flag = True
    if files_to_return.lower().find('sb') > 0:
        files_to_return_sideboard_flag = True
    if files_to_return.lower().find('comp') > 0:
        files_to_return_companion_flag = True

    deck_flag_list = [files_to_return_all_flag, files_to_return_main_flag, files_to_return_companion_flag,
                      files_to_return_sideboard_flag]
    if all(deck_flag_list) == False:
        print("Returning All by Default")
        files_to_return_all_flag = True

    decklist_df_sorted = decklist_df.copy()
    most_played_cards = decklist_df_sorted.groupby(['Card'])['Sideboard'] \
        .size().reset_index(name='Total') \
        .sort_values(['Total'], ascending=False).head(10)
    most_played_main = decklist_df_sorted[decklist_df_sorted['Sideboard'] == 0].groupby(['Card'])['Sideboard'] \
        .size().reset_index(name='Total') \
        .sort_values(['Total'], ascending=False).head(10)
    most_played_sb = decklist_df_sorted[decklist_df_sorted['Sideboard'] == 1].groupby(['Card'])['Sideboard'] \
        .size().reset_index(name='Total') \
        .sort_values(['Total'], ascending=False).head(10)
    most_played_companion = decklist_df_sorted[decklist_df_sorted['Companion'] == 1].groupby(['Card'])['Sideboard'] \
        .size().reset_index(name='Total') \
        .sort_values(['Total'], ascending=False).head(10)

    if files_to_return_all_flag == True:
        return most_played_cards
    elif files_to_return_main_flag == True:
        return most_played_main
    elif files_to_return_sideboard_flag == True:
        return most_played_sb
    elif files_to_return_companion_flag == True:
        return most_played_companion
    else:
        print("Problem")
        return None


def get18s(sheet, all_standings=False):
    ss = ezsheets.Spreadsheet(sheet)
    print(ss.title)
    print(ss.sheetTitles)
    players = ss['Player Results'].getColumn('I')
    points = ss['Player Results'].getColumn('J')

    listOfLists = [players, points]

    players = [x for x in players if x]
    points = [x for x in points if x]
    players.pop(0)
    points.pop(0)
    print(players, "\n", points)
    some_tuples = list(zip(players, points))
    df_results = pd.DataFrame(some_tuples, columns=['Players', 'Points'])
    df_results['Results'] = pd.to_numeric(df_results['Points'])
    for i in range(len(df_results['Points'])):
        df_results['Points'][i] = int(df_results['Points'][i])

    df_18_plus = df_results[df_results['Points'] > 18]
    # print(type(df_results['Points'][0]))
    players_18_plus = list(df_18_plus['Players'])
    # print(players_18_plus)

    if all_standings is True:
        return df_results
    else:
        return players_18_plus


def decklist_to_file(filename, decklist_df, extension='csv', path=None):
    if extension.lower().find('csv') > 0:
        separator = ','
    elif extension.lower().find('txt') > 0:
        separator = ' '

    decklist_df.to_csv('{0}tournament_{1}_deck_{2}.{3}'. \
                       format(path, filename, extension), \
                       header=None, index=None, sep=separator, mode='a')


def get_list_of_decklists(sheet):
    '''

    :param sheet: Google sheet that has the decklists
        Need to get hyperlinks and then strip out numbers
    :return: list of decklist numbers
    '''
    ss = ezsheets.Spreadsheet(sheet)  # Import Sheet From EZSheets
    decklist_numbers = ss.sheets[-1].getColumn('M')  # Stripped Out Decklist numbers - need this for the loop

    ### Get rid of blanks
    decklist_numbers[:] = [x for x in decklist_numbers if x]

    ### Deal with Excel Errors
    exclude_nas = ['#N/A', 'N/A', 'NA', 'ERROR']
    decklist_numbers = [x for x in decklist_numbers if x not in exclude_nas]

    return decklist_numbers


def expand_decklist(decklist_dataframe):
    decklist_to_return = decklist_dataframe.reindex(decklist_dataframe.index.repeat(decklist_dataframe['Qty']))
    return decklist_to_return


def get_individual_decklist(list_number, player_id=None):
    '''
        Gets Decklist from MtgMelee
        Returns dataframe
    '''

    deck_hyperlink_stem = "https://mtgmelee.com/Decklist/View/"

    ### HTML Tag Constants
    card_condition = "decklist-builder-card-name-cell"  # Finds the Cards
    qty_condition = "decklist-builder-card-quantity-cell"  # Finds the Counts
    section_label_condition = "decklist-builder-section-label-cell"
    section_qty_condition = "decklist-builder-section-quantity-cell"
    player_name_condition = "decklist-card-title-author"
    tournament_name_condition = "decklist-card-info-tournament mr-3"

    ### Regular Expression Constants
    card_re = re.compile('blank\"\>([\s+\S+]+)\<\/a\>')
    qty_re = re.compile('\"\>([\s+\S+]+)\<\/td\>')
    sideboard_re = re.compile('\"\>([\s+\S+]+)\<\/td\>')
    sideboard_qty_re = re.compile('\"\>(\d+)([\s+\S+]+)\<\/td\>')
    name_re = re.compile('blank\"\>([\s+\S+]+)\<\/a\>')
    tournament_re = re.compile('\"\/Tournament\/View\/(\d+)\"\>([\s+\S+]+)\<\/a\>')  # Group 1 is number Group 2 is Name

    user_name_re = re.compile('Index\\/([\\s+\\S+]+)"\\starget\\="\\_blank"\\>([\\s+\\S+]+)\\<\\/a\\>')

    website = deck_hyperlink_stem + list_number

    page = requests.get(website)
    soup = BeautifulSoup(page.content, 'html.parser')  # More bs4 Stuff

    tables = soup.find_all("td")  # Find all the tables on the page
    # print(textclass)
    # pprint(tables)
    table_list = list(tables)

    ### BS4 scraping tables on the page
    card_names = soup.find_all("td", class_=card_condition)
    card_qtys = soup.find_all("td", class_=qty_condition)
    section_names = soup.find_all("td", class_=section_label_condition)
    section_qtys = soup.find_all("td", class_=section_qty_condition)
    player_name_soup = soup.find_all(class_=player_name_condition)
    tournament_name_soup = soup.find_all(class_=tournament_name_condition)

    ###Need these to be lists
    new_card_names = card_names[0:]
    new_card_qtys = card_qtys[0:]
    new_section_names = section_names[0:]
    new_section_qtys = section_qtys[0:]

    # print("Cards")
    # print(type(card_names))             # blank\"\>([\s+\S+]+)\<\/a\> - This regular expression gets the card
    # pprint(card_names)
    # print("Qtys")
    # print(type(card_qtys))              # \"\>([\s+\S+]+)\<\/td\>     - This RE gets the number
    # pprint(card_qtys)

    # print(card_re)
    # print(new_card_names[1], "\n Separator \n", new_card_qtys[1])
    # print("Separator \n")

    decklist_card_names = []
    decklist_card_qtys = []
    decklist_sections = []
    sb_section_num = []

    ### Name of Player
    player_name = name_re.search(str(player_name_soup[0])).group(1)

    user_name = user_name_re.search(str(player_name_soup[0])).group(1)
    ###Tournament Name & Number
    tournament_name = tournament_re.search(str(tournament_name_soup[0])).group(2)
    # print(tournament_name)
    tournament_number = tournament_re.search(str(tournament_name_soup[0])).group(1)
    # print("Tournament Number: ", tournament_number, "\nTournament Name: ", tournament_name)

    ### Grab a Decklist - Cards
    for i in range(len(new_card_names)):
        card_name_temp = card_re.search(str(new_card_names[i]))
        decklist_card_names.append(card_name_temp.group(1))

    ### Grab a Decklist - Qtys
    for i in range(len(new_card_qtys)):
        card_qty_temp = qty_re.search(str(new_card_qtys[i]))
        decklist_card_qtys.append(card_qty_temp.group(1))

    decklist_card_qtys = [int(i) for i in decklist_card_qtys]

    ### Sideboard
    for i in range(len(new_section_names)):
        section_name_temp = sideboard_re.search(str(new_section_names[i]))
        section_num_temp = sideboard_qty_re.search(str(new_section_qtys[i]))
        decklist_sections.append(section_name_temp.group(1))
        sb_section_num.append(section_num_temp.group(1))

    ### Figure out where the sb begins and ends
    sb_running_total = 0
    sb_total = int(sb_section_num[-1])
    sb_index = len(decklist_card_qtys) - 1

    decklist_sideboard = [0 for x in range(len(decklist_card_qtys))]

    while sb_running_total < sb_total:
        sb_running_total = sb_running_total + int(decklist_card_qtys[sb_index])
        decklist_sideboard[sb_index] = 1
        sb_index = sb_index - 1

    ### Companions
    companion = [False for x in range(len(decklist_card_qtys))]
    # print(decklist_sections)
    # print(companion)

    if "Companion" in decklist_sections:
        companion[0] = True

    # print(companion)

    # print(sb_total)
    # print(sb_running_total)
    # print(sb_index)

    # print(decklist_card_qtys)
    # print(decklist_card_names)
    #
    # print(decklist_sections)
    # print(sb_section_num)
    # print(sb_section_num[-1])

    # print(type(decklist_card_qtys[0]))
    ### Dataframe out of the list
    some_tuples = list(zip(decklist_card_qtys, decklist_card_names, decklist_sideboard, companion))
    decklist_df = pd.DataFrame(some_tuples, columns=['Qty', 'Card', 'Sideboard', 'Companion'])

    ### Add ID Variables
    decklist_df['Player_Name'] = player_name
    decklist_df['Player_Id'] = player_id
    decklist_df['Tournament_Name'] = tournament_name
    decklist_df['Tournament_Number'] = tournament_number
    decklist_df['Player_Username'] = user_name

    return decklist_df


def streamdecker_text_files(path, csvOfDecklists):
    '''
    Takes csv of all decklists and splits them out into individual txt files for StreamDecker Upload
    :param path: Where the decklist csv is
    :param csvOfDecklists: Name of decklist csv (includes ".csv")
    :return: None
    '''
    decklist_file_expanded = '{0}{1}'.format(path, csvOfDecklists)
    # print(decklist_file_expanded)

    df = pd.read_csv(decklist_file_expanded)
    player_names = df['Player_Name'].unique()
    # print(player_names)

    for player in player_names:
        # print(player)
        dontstrip = [' ', '_', '-']
        player_name_for_file_name = "".join(c for c in player if c.isalnum() or c in dontstrip).rstrip()

        single_deck_df_main = df.copy()
        single_deck_df_sb = df.copy()

        single_deck_df_main = single_deck_df_main[(single_deck_df_main['Player_Name'] == player) &
                                                  (single_deck_df_main['Sideboard'] == 0) &
                                                  (single_deck_df_main['Companion'] == 0)]

        single_deck_df_sb = single_deck_df_sb[(single_deck_df_sb['Player_Name'] == player) &
                                              (single_deck_df_sb['Sideboard'] == 1) &
                                              (single_deck_df_sb['Companion'] == 0)]

        # print(single_deck_df_main.head(2).to_string())
        # print(single_deck_df_sb.head(2).to_string())

        compressed_df_main = single_deck_df_main.groupby(['Card']) \
                                 .size().reset_index(name='Number').iloc[:, ::-1]
        compressed_df_sb = single_deck_df_sb.groupby(['Card']) \
                               .size().reset_index(name='Number').iloc[:, ::-1]

        ###Trying writing rows at a time
        # print(compressed_df_main.to_string())
        with open('{0}{1}_deck.txt'.format(path, player_name_for_file_name), 'w', newline='') as deckfile:
            line_writer = csv.writer(deckfile, delimiter=' ')

            for i in range(len(compressed_df_main)):
                deckfile.write('{0} {1}\n'.format(compressed_df_main['Number'][i], compressed_df_main['Card'][i]))
            deckfile.write("\nSideboard\n")
            for i in range(len(compressed_df_sb)):
                deckfile.write('{0} {1}\n'.format(compressed_df_sb['Number'][i], compressed_df_sb['Card'][i]))

        print("Completed Streamdecker Lists")

### The rest of these aren't done

def mtgmeleemakeid():
    seed = 5759
    base = 1000000000
    # random.seed(5759)

    newid = base + random.randint(1, 999999999)
    # print(newid)

    return newid


def mtgmeleecheckid(new_id=None, id_db=None, name=None, username=None):
    result = False  # Defaults to the ID is not in the database
    if new_id is None:
        result = True  # Returns True to exit loop if it's not fed an ID
    if new_id in id_db:
        result = True  # Also returns true if the id is in the database
        # print(result)
    result_tuple = (result, new_id, name, username)
    return result_tuple


def mtgmeleeresults(sheet):
    ss = ezsheets.Spreadsheet(sheet)
    # print(ss.title)
    # print(ss.sheetTitles)
    # ss_deck_breakdown = ss.sheets[1]
    # ss_results = ss.sheets[2]
    # print(ss_deck_breakdown)

    # players = ss.sheets[1].getColumn(1)
    # deck_lists = ss.sheets[1].getColumn(2)

    tournamentIdList = ss.sheets[2].getColumn(1)
    roundList = ss.sheets[2].getColumn(2)
    playerOneList = ss.sheets[2].getColumn(3)
    playerTwoList = ss.sheets[2].getColumn(4)
    resultsList = ss.sheets[2].getColumn(5)

    listOfLists = [tournamentIdList, roundList, playerOneList, playerTwoList, resultsList]

    ### Delete Empty Lists
    for l in listOfLists:
        print("List", l)
        l[:] = [x for x in l if x]
        l.pop(0)

    resultType = [-9 for x in range(len(resultsList))]
    # print(resultType)

    ###Troubleshooting
    tournamentIdList = [593 for x in range(len(resultsList))]

    for i in range(len(resultsList)):
        if (playerOneList[i]) in resultsList[i]:
            resultType[i] = 1
        if (playerTwoList[i]) in resultsList[i]:
            resultType[i] = 2
        if ('0-0-3') in resultsList[i]:
            resultType[i] = 3
        if 'was awarded' in resultsList[i]:
            resultType[i] = 4  ### Bye is code 4

    # print(resultsList)
    # print("Player 1 Wins: ", resultType.count(1), "\nPlayer 2 Wins: ", resultType.count(2), "\nDraws: ", resultType.count(3))
    # print("Byes: ", resultType.count(4), "\nLeft Over: ", resultType.count(-9))

    results_df = pd.DataFrame(
        list(zip(tournamentIdList, roundList, playerOneList, playerTwoList, resultsList, resultType)),
        columns=['Tournament Id', 'Round', 'Player 1', 'Player 2', 'Result', 'Result Code'])
