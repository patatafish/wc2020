import pandas as pd
import plotly.express as px
import requests as req




if __name__ == '__main__':

    time_url = 'https://docs.google.com/spreadsheets/d/e/2PACX' \
               '-1vQ6quxuNPCU6dvKxbzpQoaWk71ygyFjjF7g7GSCDYxindPgGZXBJDJNbJWuOTKwUOervR-Ysqpy6KP-/pub?output=csv&gid=0'
    sponsor_url = 'https://docs.google.com/spreadsheets/d/e/2PACX' \
                  '-1vQ6quxuNPCU6dvKxbzpQoaWk71ygyFjjF7g7GSCDYxindPgGZXBJDJNbJWuOTKwUOervR-Ysqpy6KP-/pub?output=csv' \
                  '&gid=501915331'

    # open connection and pull most recent data
    print('grabbing csv data...')
    with req.Session() as session:
        print('grabbing time data...')
        time_data = session.get(url=time_url).text
        print('grabbing sponsor data...')
        sponsor_data = session.get(url=sponsor_url).text


    print('cleaning data...')
    # copy sponsors to dict item
    # split between lines
    sponsor_data = sponsor_data.split('\r\n')
    # look at each line
    for i in range(len(sponsor_data)):
        # split the item on commas
        sponsor_data[i] = sponsor_data[i].split(',')
        # redefine the item as a tuple for dict creation
        sponsor_data[i] = (sponsor_data[i][0], sponsor_data[i][1])
    # create a dict from list of tuples
    sponsor_dict = dict(sponsor_data)
    print(sponsor_dict)

    # parse the time items
    # split between lines
    time_data = time_data.split('\r\n')
    # look at each line
    in_quotes = False
    for i in range(len(time_data)):
        # append a , to mark end of line
        time_data[i] += ','
        # temp items to hold line data
        new_line = []
        new_string = ''
        # copy strings to new line, splitting on comma BUT skipping commas in quotes
        for char in time_data[i]:
            if char == '\"':
                in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                new_line.append(new_string)
                new_string = ''
            else:
                new_string += char


        # copy new line into place in time data
        time_data[i] = new_line.copy()

    print(time_data)

    clean_csv_array = []
    # get a list of unique sponsors
    for company in sponsor_dict.values():
        if company not in clean_csv_array:
            clean_csv_array.append(company)

    # seed the CSV array with series 0 data of sponsors and minutes
    for i in range(len(clean_csv_array)):
        clean_csv_array[i] = [clean_csv_array[i], 0, 0]


    print(clean_csv_array)

    # loop each game to transfer data to CSV array
    for game in time_data[1:]:
        series = int(game[1])
        shirt_1 = sponsor_dict[game[2]]
        shirt_2 = sponsor_dict[game[4]]

        # get actual minutes
        first_half = int(game[6])
        second_half = int(game[7]) - 45
        if game[8] != '0':
            ot1 = int(game[8]) - 90
        else:
            ot1 = 0
        if game[9] != '0':
            ot2 = int(game[9]) - 105
        else:
            ot2 = 0
        pks = int(game[10])

        total_time = first_half + second_half + ot1 + ot2 + pks

        print(f'{game[2]} v. {game[4]}, {total_time} minutes.')
        print(f'{shirt_1} and {shirt_2}')

        for i in range(len(clean_csv_array)):
            current_time = clean_csv_array[i][-1]

            clean_csv_array[i].append(series)

            if clean_csv_array[i][0] == shirt_1:
                current_time += total_time
            if clean_csv_array[i][0] == shirt_2:
                current_time += total_time

            clean_csv_array[i].append(current_time)



    print(clean_csv_array)

    series_list = []
    minutes_list = []
    company_list = []

    for line in clean_csv_array:
        name = line.pop(0)
        while line:
            series_list.append(line.pop(0))
            minutes_list.append(line.pop(0))
            company_list.append(name)

    df = pd.DataFrame({'Series': series_list,
                       'Minutes': minutes_list,
                       'Company': company_list
    })

    fig = px.area(df, x="Series", y="Minutes", color="Company")
    fig.show()
