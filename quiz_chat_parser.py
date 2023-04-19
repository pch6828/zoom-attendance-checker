import os
import sys
import re

database = {}
classdates = []


def reformat_name(name: str):
    name = name.strip()
    if str.isdigit(name[:8]):
        name = name[9:]

    name = re.sub(r'[_-]|\(.+\)', '', name)
    name = name.strip()
    name = name.lower()
    return name


def parse(dirname: str, filename: str):
    file = open(dirname+"/"+filename, 'r', encoding="UTF-8")
    date = filename[4:9]
    classdates.append(date)
    regex_expression = r'(\d\d:\d\d:\d\d)\s+From ([a-zA-Z0-9가-힣()\. \u4e00-\u9fff]+?)( to ([a-zA-Z0-9가-힣()\. \u4e00-\u9fff]+?)(\(Direct Message\))?(\(Privately\))?)?:'

    while True:
        line = file.readline()
        if not line:
            break
        groups = re.match(regex_expression, line)
        if groups:
            sender = groups[2]
            name = reformat_name(sender)
            if name not in database:
                database[name] = set()
            database[name].add(date)


def make_header():
    header = 'name'
    for date in classdates:
        header += ','
        header += date

    return header


def write_csv(filename: str):
    classdates.sort()
    file = open(filename, 'w', encoding='UTF-8')

    file.write(make_header())
    file.write('\n')
    for student in database:
        attendance_list = database[student]
        row = student
        for date in classdates:
            row += ','
            if date in attendance_list:
                row += 'O'
            else:
                row += 'X'
        file.write(row)
        file.write('\n')
    file.close()


def main():
    dirname = sys.argv[1]
    output_filename = sys.argv[2]

    files = os.listdir(dirname)
    for filename in files:
        parse(dirname, filename)

    write_csv(output_filename)


main()
