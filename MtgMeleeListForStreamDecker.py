import MtgMeleeUtils
import csv
import pandas as pd
import os

def main(path, csvOfDecklists):
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
                                                  (single_deck_df_main['Sideboard']==0) &
                                                  (single_deck_df_main['Companion'] == 0)]

        single_deck_df_sb = single_deck_df_sb[(single_deck_df_sb['Player_Name'] == player) &
                                              (single_deck_df_sb['Sideboard'] == 1) &
                                              (single_deck_df_sb['Companion'] == 0)]

        # print(single_deck_df_main.head(2).to_string())
        # print(single_deck_df_sb.head(2).to_string())

        compressed_df_main = single_deck_df_main.groupby(['Card'])  \
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
        ### With to_csv
        # compressed_df_main.to_csv('{0}{1}_deck.txt'.format(path, player_name_for_file_name),
        #                           header=None, index=None, sep='\t', mode='w', quoting=csv.QUOTE_NONE, escapechar="\\")
        # with open('{0}{1}_deck.txt'.format(path, player_name_for_file_name), 'a', newline='') as deckfile:
        #     deckfile.write("Sideboard\n")
        #
        # compressed_df_sb.to_csv('{0}{1}_deck.txt'.format(path, player_name_for_file_name), \
        #                           header=None, index=None, sep='\t', mode='a', quoting=csv.QUOTE_NONE, escapechar="\\")
        #
        # filereplace('{0}{1}_deck.txt'.format(path, player_name_for_file_name), "\t", " ")
        # #
        # path = Path('{0}{1}_deck.txt'.format(path, player_name_for_file_name))
        # text = path.read_text()
        # new_text = text.replace("\t", " ")
        # path.write_text(new_text)

path_for_list = 'C:\\Users\\JaysC\\Dropbox\\Coding\\Python\\MtG\\CBL Test\\'
decklist_csv = 'all_decklists.csv'
#decklist_to_file(filename='newdeck', decklist_df=, extension='txt', path=path_for_list)

##Lotus Box 5-17-2020
path_for_list = 'C:\\Users\\JaysC\\Dropbox\\Coding\\Python\\MtG\\Decklists\\'
decklist_csv='tournament__all_decklists_for_sql.csv'

main(path=path_for_list, csvOfDecklists=decklist_csv)


