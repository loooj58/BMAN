import argparse
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import psycopg2
import re
import warnings

from config import *


def convert_units(arr):
	mean = np.mean(arr)
	u = len(UNITS) - 1
	for i, unit in enumerate(UNITS):
		mean = mean / SIZE[i]
		if mean < SIZE[i+1]:
			u = i
			break
	for i in range (u + 1):
		arr = arr / SIZE[i]
	return arr, UNITS[u]


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
	count = cursor.fetchone()
	if count is None:
		return None
	count = count[0]
	cursor.close()
	conn.close()
	return count

def is_file_to_parse(root, file):
	filepath = os.path.join(root, file)
	correct_ext = all([not file.endswith(ext) for ext in EXCLUDED_EXTENSIONS])
	correct_folder = all([elem not in os.path.join(root, file) for elem in FOLDERS_IGNORE])
	return correct_ext and correct_folder

def parse_dir(dirname):
	time_arr = []
	time_per_events_arr = []
	unsuccessful_arr = []
	for root, dirs, files in os.walk(dirname):
		for file in files:
			if is_file_to_parse(root, file):
				time, is_successful, run_num = parse_time(os.path.join(root, file))
				if time is not None:
					if run_num is not None:
						time_arr.append(time)
						time_per_events_arr.append(time / get_events_count(run_num))
					elif is_successful == True:
						warnings.warn("Can not parse run number in successfully ended log file")
				elif is_successful == True:
					warnings.warn("Can not parse time in successfully ended log file")
				if is_successful == False and file != UNSUCCESSFUL_OUT:
					unsuccessful_arr.append(file)
	if time_arr == []:
		warnings.warn("No data")
		return np.array([]), 0., []
	return np.array(time_arr), np.array(time_per_events_arr), unsuccessful_arr


def plot_stats(array, bins, title, filename=None):
	plt.clf()
	plt.hist(array, bins=bins)
	plt.axvline(np.mean(array), linestyle='dashed', linewidth=1)
	plt.title(title)
	if filename is None:
		plt.show()
	else:
		plt.savefig(filename, dpi=DPI)


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--dirname', type=str, help='Name of directory to explore', default='.')
	parser.add_argument('--bins', type=int, help='Number of bins for time histogram', default=10)
	parser.add_argument('--bins_per_event', type=int, help='Number of bins for time per event histogram', default=10)
	args = parser.parse_args()
	dirname, bins, bins_per_event = args.dirname, args.bins, args.bins_per_event

	arr, arr_per_event, unsuccessful_arr = parse_dir(dirname)

	arr, unit = convert_units(arr)
	title = f'Time, {unit}. Mean = {np.mean(arr)} {unit}.'
	plot_stats(arr, bins, title, NAME_TIME)

	arr_per_event, unit_per_event = convert_units(arr_per_event)
	title_per_event = f'Time per event, {unit_per_event}. Mean = {np.mean(arr_per_event)} {unit_per_event}.'
	plot_stats(arr_per_event, bins_per_event, title_per_event, NAME_TIME_PER_EVENT)


	with open(UNSUCCESSFUL_OUT, 'w') as f:
		for elem in unsuccessful_arr:
			f.write(elem + '\n')


if __name__ == '__main__':
	main()

