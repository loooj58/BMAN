import glob, os, sys
import numpy as np
import warnings
import matplotlib.pyplot as plt
import re
import datetime
import psycopg2


SIZE = 1024
UNITS = ['seconds', 'minutes', 'hours', 'days']
START = 'Start date:'
END = 'End date:'
SUCCESS = 'Macro finished successfully!'
START_REGEX = r'Start date: \w{2} \w{3} \d{1,2} \d{1,2}:\d{1,2}:\d{1,2} \w+ \d{4}'
END_REGEX = r'End date: \w{2} \w{3} \d{1,2} \d{1,2}:\d{1,2}:\d{1,2} \w+ \d{4}'
MONTH_ARR = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']
UNITS = ['seconds', 'minutes', 'hours', 'days', 'months', 'years']
SIZE = [1, 60, 60, 24, 30, 12]
EXCLUDED_EXTENSIONS = ['.py', '.DS_Store', '.png']
UNSUCCESSFUL_OUT = 'unsuccessful.txt'
RUN_REGEX = r'run\d+'
RUN_EXTENSION = '.root'
UNI_DB_USERNAME = "db_reader"
UNI_DB_PASSWORD = "reader_pass"
UNI_DB_NAME = "bmn_db"
UNI_DB_HOST = "vm221-53.jinr.ru"




def convert_units(arr, mean):
    u = len(UNITS) - 1
    for i, unit in enumerate(UNITS):
        mean = mean / SIZE[i]
        if mean < SIZE[i+1]:
            u = i
            break
    for i in range (u + 1):
        arr = arr / SIZE[i]

    return arr, mean, UNITS[u]

def convert_month(month):
	res = MONTH_ARR.index(month) + 1
	return res

def get_date(result):
	year = int(result[7])
	month = convert_month(result[3])
	day = int(result[4])
	time = result[5].split(':')
	hour = int(time[0])
	minute = int(time[1])
	second = int(time[2])
	return year, month, day, hour, minute, second


def parse_time(log_file):
	is_successful = False
	start = None
	end = None
	run_num = None
	with open(log_file, 'r') as f:
		for line in f:
			if START in line:
				result = re.search(START_REGEX, line).group().split()
				y, m, d, h, minute, s = get_date(result)
				start = datetime.datetime(y, m, d, hour=h, minute=minute, second=s)
			if END in line:
				result = re.search(END_REGEX, line).group().split()
				y, m, d, h, minute, s = get_date(result)
				end = datetime.datetime(y, m, d, hour=h, minute=minute, second=s)
			if SUCCESS in line:
				is_successful = True
			if RUN_EXTENSION in line and run_num == None:
				result = re.search(RUN_REGEX, line)
				if result != None:
					run_num = int(result.group()[3:])
	if start == None or end == None:
		delta = None
	else:
		delta = (end - start).total_seconds()
	return delta, is_successful, run_num

def get_events_count(run_num):
	conn = psycopg2.connect(dbname=UNI_DB_NAME, user=UNI_DB_USERNAME, 
	                        password=UNI_DB_PASSWORD, host=UNI_DB_HOST)
	cursor = conn.cursor()
	cursor.execute(f'SELECT event_count FROM run_ WHERE run_number = {run_num}')
	count = cursor.fetchone()[0]
	cursor.close()
	conn.close()
	return count


def parse_dir(dirname):
	time_arr = []
	count_events_arr = []
	unsuccessful_arr = []
	for root, dirs, files in os.walk(dirname):
		for file in files:
			if all([not file.endswith(ext) for ext in EXCLUDED_EXTENSIONS]):
				time, is_successful, run_num = parse_time(os.path.join(root, file))
				if time is not None:
					time_arr.append(time)
					count_events_arr = get_events_count(run_num)
				if is_successful == False and file != UNSUCCESSFUL_OUT:
					unsuccessful_arr.append(file)
	if time_arr == []:
		warnings.warn("No data")
		return np.array([]), 0., []
	return np.array(time_arr), np.mean(np.array(time_arr)), unsuccessful_arr, np.array(count_events_arr)

def plot(mean, arr, unit, bins):
	title = f'Time, {unit}. Mean = {mean} {unit}.'
	plt.hist(arr, label=title, bins=bins)
	plt.title(title)
	plt.show()

def save(mean, arr, unit, bins):
	title = f'Time size, {unit}. Mean = {mean} {unit}.'
	plt.hist(arr, label=title, bins=bins)
	plt.title(title)
	plt.savefig('time.png', dpi=300)

def main():
	dirname = '.'
	bins = 10
	bins_time_per_event = 10
	if len(sys.argv) > 1:
		dirname = sys.argv[1]
	if len(sys.argv) > 2:
		bins = sys.argv[2]
	if len(sys.argv) > 2:
		bins_time_per_event = sys.argv[3]
	arr, mean, unsuccessful_arr, count_events_arr = parse_dir(dirname)
	arr_time_per_event = arr / count_events_arr
	mean_time_per_event = np.mean(arr_time_per_event)
	arr_time_per_event, mean_time_per_event, unit_time_per_event = convert_units(arr_time_per_event, mean_time_per_event)
	arr, mean, unit = convert_units(arr, mean)
	with open(UNSUCCESSFUL_OUT, 'w') as f:
		for elem in unsuccessful_arr:
			f.write(elem + '\n')
	save(mean, arr, unit, bins)
	plot(mean, arr, unit, bins)
	save(mean_time_per_event, arr_time_per_event, unit_time_per_event, bins_time_per_event)
	plot(mean_time_per_event, arr_time_per_event, unit_time_per_event, bins_time_per_event)



if __name__ == '__main__':
	main()
