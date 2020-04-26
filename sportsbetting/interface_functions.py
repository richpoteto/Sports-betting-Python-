import ast
import datetime

def odds_table(result):
    lines = result.split("\n")
    for i, line in enumerate(lines):
        if "}}" in line:
            break
    dict_odds = eval("".join(lines[1:i+1]))
    odds = dict_odds["odds"]
    table = []
    for key, value in odds.items():
        table.append([key]+list(map(str, value)))
    return(table)

def indicators(result):
    lines = result.split("}}\n")[1].split("\nmises arrondies")[0].split("\n")
    for line in lines:
        yield line.split(" = ")

def stakes(result):
    return result.split("\n\n")[-1]

def infos(result):
    lines = result.split("\n")
    match = lines[0]
    for i, line in enumerate(lines):
        if "}}" in line:
            break
    dict_odds = eval("".join(lines[1:i+1]))
    date = dict_odds["date"]
    return match, date.strftime("%A %d %B %Y %H:%M")
    
    