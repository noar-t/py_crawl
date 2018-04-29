import os

path = '/Users/noah/Downloads/links 2/'

def get_files(path):
    files = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        files = filenames

    return files

def check_files(files):
    bad_files = set()
    good_files = set()
    for filename in files:
        with open(path + filename, 'r') as f:
            if len(f.read()) == 0:
                bad_files.add(filename)
            else:
                good_files.add(filename)

    return (bad_files, good_files)

def remove_empty_files(bad_files):
    for value in bad_files:
        os.remove(path + value)

def remove_dead_links(good_files):
    for filename in good_files:
        new_file_body = ''
        with open(path + filename, 'r') as f:
            for line in f:
                test_line = line.replace('http://', '') \
                    .replace('https://', '').replace('\n', '') \
                    .replace('/', '%2f')

                if test_line in good_files:
                    new_file_body = new_file_body + line

        with open(path + filename, 'w') as f:
            f.write(new_file_body)
            f.truncate()


def main():

    while True:
        files = get_files(path)
        bad_files, good_files = check_files(files)
        if len(bad_files) == 0:
            break
        remove_empty_files(bad_files)
        remove_dead_links(good_files)


if __name__ == '__main__':
    main()
