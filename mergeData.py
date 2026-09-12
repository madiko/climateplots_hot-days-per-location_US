import json
from datetime import date

datafolder = 'data'

today = date.today()

def main():
    
    data = []

    for year in range(1900, 2029, 5):
        
        fn = datafolder + '/' + str(year) + '.json'
        print("Reading file " + fn + " ...")
        try:
            f = open(fn)
            fulldata = json.load(f)
            f.close()
        except OSError as error:
            print("process: ERROR: opening file failed!")
            quit()
        
        print("Merging ...")
        for daydata in fulldata['data']:
            data.append(daydata)
            
    print()
    print("Storing merged json ...")
    try:
        out_file = open(datafolder + "/merged.json", "w")
        json.dump(data, out_file, indent = 6)
        out_file.close()
    except OSError as error:
        print("process: ERROR: writing merged file!")
        quit()
        
    print()
    print("... done!")
    print()
    
    
if __name__ == '__main__':
    main()
