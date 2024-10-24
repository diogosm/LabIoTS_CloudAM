from localdbsharedlib import select_all_data

def main():
    data = select_all_data()
    
    if data is not None:
        for record in data:
            print(record)
    else:
        print("some errorr.")

if __name__ == "__main__":
    main()