import sys
import os
import re
from datetime import datetime, timedelta

database = {}
classdates = []


def parse_line(line: str):
    tokens = line.split(',')
    name = tokens[0]

    if str.isdigit(name[:8]):
        name = name[9:]

    name = re.sub(r'[_-]|\(.+\)', '', name)
    name = name.strip()
    start = datetime.strptime(tokens[2], '%Y/%m/%d %H:%M:%S %p')
    end = datetime.strptime(tokens[3], '%Y/%m/%d %H:%M:%S %p')

    return {'name': name, 'start': start, 'end': end}


def update_attendance(date: str, attendance_info: dict):
    name = attendance_info['name']

    if name not in database:
        database[name] = {}

    attendance_list = database[name]
    if date not in attendance_list:
        curr_start = attendance_info['start']
        curr_end = attendance_info['end']
        class_start = datetime(
            curr_end.year, curr_end.month, curr_end.day, 10, 30, 0)

        if curr_end > class_start:
            latetime = (curr_start - class_start).total_seconds()
            attendance_list[date] = {
                'start': attendance_info['start'], 'end': attendance_info['end'], 'late': latetime > 600, 'disappear': False, 'early_leave': False}
    else:
        prev_end = attendance_list[date]['end']
        curr_start = attendance_info['start']
        curr_end = attendance_info['end']

        if (curr_end - attendance_list[date]['end']).total_seconds() > 0:
            attendance_list[date]['end'] = attendance_info['end']

        if (curr_start - prev_end).total_seconds() > 600:
            attendance_list[date]['disappear'] = True

            print("DISAPPEARED STUDENT!")
            print(name)
            print("LEAVED AT    " + str(prev_end))
            print("CAME BACK AT " + str(curr_start))
            print()


def get_date_from_metadata(line: str):
    tokens = line.split(',')
    date = tokens[2].split(' ')[0]

    return date


def parse(dirname: str, filename: str):
    file = open(dirname+"/"+filename, 'r', encoding="UTF-8")
    cnt = 4

    date = None

    while True:
        line = file.readline()
        cnt -= 1
        if cnt >= 0:
            if cnt == 2:
                date = get_date_from_metadata(line)
                if date not in classdates:
                    classdates.append(date)
            continue
        elif not line:
            break

        attendance_info = parse_line(line)
        update_attendance(date, attendance_info)

    file.close()


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
                attendance = attendance_list[date]
                if attendance['late']:
                    row += 'L'
                elif attendance['disappear']:
                    row += 'D'
                elif attendance['early_leave']:
                    row += 'E'
                else:
                    row += 'O'
            else:
                row += 'X'
        file.write(row)
        file.write('\n')
    file.close()


def get_class_end(date: str):
    class_end = datetime.strptime(date, '%Y/%m/%d')
    class_end = class_end.replace(hour=11, minute=45, second=0)

    diff = 0
    cnt = 0

    for student in database:
        attendance_list = database[student]
        if date in attendance_list:
            attendance = attendance_list[date]
            diff += (attendance['end'] - class_end).total_seconds()
            cnt += 1

    if cnt == 0:
        diff = 0
    else:
        diff //= cnt

    class_end += timedelta(seconds=diff)

    return class_end


def check_early_leaving(date: str):
    class_end = get_class_end(date)

    for student in database:
        attendance_list = database[student]
        if date in attendance_list:
            attendance = attendance_list[date]
            if (class_end - attendance['end']).total_seconds() >= 600:
                attendance['early_leave'] = True


def main():
    dirname = sys.argv[1]
    output_filename = sys.argv[2]

    files = os.listdir(dirname)
    for filename in files:
        parse(dirname, filename)

    for date in classdates:
        check_early_leaving(date)

    write_csv(output_filename)


main()
