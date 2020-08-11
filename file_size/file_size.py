import glob, os, sys
import numpy as np
import warnings
import matplotlib.pyplot as plt
import re
import psycopg2

SIZE = 1024
UNITS = ['bytes', 'KB', 'MB', 'GB', 'TB']
EXTENSIONS = [".data", ".root"]
RUN_NUM_REGEX = r'\d+'
UNI_DB_USERNAME = "db_reader"
UNI_DB_PASSWORD = "reader_pass"
UNI_DB_NAME = "bmn_db"
UNI_DB_HOST = "vm221-53.jinr.ru"

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

def convert_units(arr, mean):
    for i, unit in enumerate(UNITS):
        if mean / SIZE**i < SIZE:
            break
    mean /= SIZE**i
    arr = arr / (SIZE**i)
    return arr, mean, unit

def parse_dir(dirname):
	filesize_arr = []
	filesize_per_event = []
	for root, dirs, files in os.walk(dirname):
		for file in files:
			if any([file.endswith(ext) for ext in EXTENSIONS]):
				filesize_bytes = os.stat(os.path.join(root, file)).st_size
				run_num = re.search(RUN_NUM_REGEX, file)
				if run_num is None:
					warnings.warn("No run found in fillename")
				else:
					run_num = run_num.group()
					run_count = get_events_count(run_num)
					if run_count is None:
						warnings.warn("No run found in db")
					else:
						filesize_arr.append(filesize_bytes)
						filesize_per_event.append(filesize_bytes / run_count)
	if filesize_arr == []:
		warnings.warn("No data")
		return np.array(filesize_arr), 0.
	return np.array(filesize_arr), np.mean(np.array(filesize_arr)), np.array(filesize_per_event), np.mean(np.array(filesize_per_event))

def plot(mean, arr, unit, bins):
	title = f'File size, {unit}. Mean = {mean} {unit}.'
	plt.hist(arr, label=title, bins=bins)
	plt.title(title)
	plt.show()

def save(mean, arr, unit, bins):
	title = f'File size, {unit}. Mean = {mean} {unit}.'
	plt.hist(arr, label=title, bins=bins)
	plt.title(title)
	plt.savefig('file_size.png', dpi=300)

def main():
	dirname = '.'
	bins = 10
	bins_per_event = 10
	if len(sys.argv) > 1:
		dirname = sys.argv[1]
	if len(sys.argv) > 2:
		bins = sys.argv[2]
	if len(sys.argv) > 3:
		bins_per_event = sys.argv[3]
	arr, mean, arr_per_event, mean_per_event = parse_dir(dirname)
	arr, mean, unit = convert_units(arr, mean)
	arr_per_event, mean_per_event, unit_per_event = convert_units(arr_per_event, mean_per_event)
	save(mean, arr, unit, bins)
	plot(mean, arr, unit, bins)
	save(mean_per_event, arr_per_event, unit_per_event, bins_per_event)
	plot(mean_per_event, arr_per_event, unit_per_event, bins_per_event)
	


if __name__ == '__main__':
	main()
