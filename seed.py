import model
import csv
#session

def load_addresses(session):
    # use u.user
    filename = "./data/DepartDest.txt"
    with open(filename, 'rb') as f:
        reader = csv.reader(f, delimiter=",", quoting=csv.QUOTE_NONE)
        #print reader
        for row in reader:
            #print row
            street = row[0] + " " + row[1]
            temp_address = model.Address(street=street, city=row[2], state=row[3], zipcode=row[4])
            session.add(temp_address)
    session.commit()
    f.close()
    

def main(session):
    # You'll call each of the load_* functions with the session as an argument
        load_addresses(session)


if __name__ == "__main__":
    s= model.connect()
    main(s)

