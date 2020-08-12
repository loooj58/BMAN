import argparse
import matplotlib.pyplot as plt
import numpy as np
import os
import psycopg2
import re
import warnings

from config import *


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


def convert_units(arr):
	mean = np.mean(arr)
	for i, unit in enumerate(UNITS):
		if mean / SIZE**i < SIZE:
			break
			arr = arr / (SIZE**i)
	return arr, unit


def is_file_to_parse(root, file):
	filepath = os.path.join(root, file)
	correct_ext = any([file.endswith(ext) for ext in EXTENSIONS])
	correct_folder = all([elem not in os.path.join(root, file) for elem in FOLDERS_IGNORE])
	return correct_ext and correct_folder


def parse_dir(dirname):
	filesize_arr = []
	filesize_per_event = []
	for root, dirs, files in os.walk(dirname):
		for file in files:
			if is_file_to_parse(root, file):
				filesize_bytes = os.stat(os.path.join(root, file)).st_size
				run_num = re.search(RUN_NUM_REGEX, file)
				if run_num is None:
					warnings.warn("No run number found in filename")
				else:
					run_num = run_num.group()
					run_count = get_events_count(run_num)
					if run_count is None:
						warnings.warn("No run number found in database")
					else:
						filesize_arr.append(filesize_bytes)
						filesize_per_event.append(filesize_bytes / run_count)
	if filesize_arr == []:
		warnings.warn("No data")
		return np.array([]), np.array([])
	return np.array(filesize_arr), np.array(filesize_per_event)


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
	parser.add_argument('--bins', type=int, help='Number of bins for filesize histogram', default=10)
	parser.add_argument('--bins_per_event', type=int, help='Number of bins for filesize per event histogram', default=10)
	args = parser.parse_args()
	dirname, bins, bins_per_event = args.dirname, args.bins, args.bins_per_event
	arr, arr_per_event = parse_dir(dirname)

	arr, unit = convert_units(arr)
	title = f'File size, {unit}. Mean = {np.mean(arr)} {unit}.'
	plot_stats(arr, bins, title, NAME_FILESIZE)

	arr_per_event, unit_per_event = convert_units(arr_per_event)
	title_per_event = f'File size per event, {unit_per_event}. Mean = {np.mean(arr_per_event)} {unit_per_event}.'
	plot_stats(arr_per_event, bins_per_event, title_per_event, NAME_FILESIZE_PER_EVENT)


if __name__ == '__main__':
	main()

