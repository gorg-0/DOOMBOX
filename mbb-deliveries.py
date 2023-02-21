import os
import numpy
import requests
import sys
import math

connections_csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTNAkeOL_ppS8jlVmALSdiNAt0dHq4nJjUcBJdUVHLGA5mHN6GcIDpmT2TN1qbuIE1O5c-3Jp5INot2/pub?gid=216210887&single=true&output=csv" #maintenance
deliveries_csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTNAkeOL_ppS8jlVmALSdiNAt0dHq4nJjUcBJdUVHLGA5mHN6GcIDpmT2TN1qbuIE1O5c-3Jp5INot2/pub?gid=0&single=true&output=csv"
coordinates_csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTNAkeOL_ppS8jlVmALSdiNAt0dHq4nJjUcBJdUVHLGA5mHN6GcIDpmT2TN1qbuIE1O5c-3Jp5INot2/pub?gid=247091508&single=true&output=csv"
urls = [connections_csv_url, deliveries_csv_url, coordinates_csv_url]
bannerlord_docs_dir = "~\\Documents\\Mount and Blade II Bannerlord\\"
from_city = "Zeonica"
to_city = "Lycaron"
possible_paths = []
number_of_paths_to_consider = 5


def create_dir(path):
    try:
        os.makedirs(path)
    except:
        pass


def find_in_array(array, searched):
    for index in range(len(array)):
        if str(array[index]) == str(searched):
            return index+1
    return 0


def remove_duplicates(array): #should be sorted
    for element_index in range(len(array) - 1, 0, -1):
        if array[element_index] == array[element_index - 1]:
            array[element_index] = ""
    return array


def two_point_distance(coords_a,coords_b):
    return math.sqrt((coords_a[0]-coords_b[0])**2+(coords_a[1]-coords_b[1])**2)


def path_length(path):
    length = 0
    for element_index in range(1, len(path)):
        x_a = int(coordinates[find_in_array(coordinates[:,0], path[element_index-1])-1][1])
        y_a = int(coordinates[find_in_array(coordinates[:,0], path[element_index-1])-1][2])
        x_b = int(coordinates[find_in_array(coordinates[:,0], path[element_index])-1][1])
        y_b = int(coordinates[find_in_array(coordinates[:,0], path[element_index])-1][2])
        length = length + two_point_distance([x_a,y_a],[x_b,y_b])
    return length


def deliveries_from_town(path, index):
    counter = 0
    for town in path[index:-1]:
        test = find_in_array(deliveries[0,:], town)
        for delivery in deliveries[1:,find_in_array(deliveries[0,:], town)-1]:
            if str(delivery) == "":
                continue
            index_temp = find_in_array(path[index+1::],delivery)
            if index_temp:
                print("from: " + str(path[index]) + " there is a delivery to: " + str(path[index+1::][index_temp-1]))
                counter = counter + 1
    return counter


def list_deliveries(paths):
    for path in paths:
        counter = 0
        print("in path " + str(path))
        for index in range(len(path)):
            counter = counter + deliveries_from_town(path, index)
        if counter == 0:
            print("there are no deliveries")


def warmup():
    csv_dir_path = os.path.expanduser(bannerlord_docs_dir) + "CSV\\"
    create_dir(csv_dir_path)
    csvs = numpy.empty(3,dtype=object)
    if not os.path.exists(csv_dir_path + "check.txt"):
        print("downloading csvs from sheets")
        check_file = open(csv_dir_path + "check.txt", "w")
        for url in urls:
            response = requests.get(url)
            if response.status_code == 200:
                file_name = response.headers["Content-Disposition"].split("\"")[1]
                content = str(response.content)[2:-1].replace("\\r\\n", "\n")
                if "fixme" in file_name:
                    file_name = file_name.replace("fixme","")
                    file = open(csv_dir_path + file_name, "w")
                    file.write(content)
                    file.close()
                    fix_connections_file(csv_dir_path + file_name)
                else:
                    file = open(csv_dir_path + file_name, "w")
                    file.write(content)
                    file.close()
                check_file.writelines(file_name + "\n")
            else:
                print("couldn't download csv(s) from sheets")
                sys.exit(0)
    else:
        print("using existing csvs, to download again delete this file:")
        print(csv_dir_path+"check.txt")
    with open(csv_dir_path+"check.txt") as check_file:
        csv_file_names = check_file.read().split("\n")
    for index in range(len(csv_file_names)-1):
        with open(csv_dir_path + csv_file_names[index]) as file:
            csvs[index] = numpy.loadtxt(file, delimiter=",", dtype=str)
    check_file.close()
    return csvs[0], csvs[1], csvs[2] #connections,deliveries,coordinates


def fix_connections_file(connections_file_path): #check for wasted time
    with open(connections_file_path) as file:
        connections_temp = numpy.loadtxt(file, delimiter=",", dtype=str)
    connections_internal = numpy.ndarray((len(connections_temp[0,:])+1,len(connections_temp[0,:])),str)
    connections_internal: numpy.ndarray = connections_internal.astype(connections_temp.dtype)
    connections_internal[:len(connections_temp[:, 0]), :len(connections_temp[0, :])] = connections_temp
    for header_a_index in range(len(connections_internal[0,:])):
        for element_a_index in range(1, len(connections_internal[:,header_a_index])):
            if connections_internal[:,header_a_index][element_a_index] == "":
                continue
            for header_b_index in range(len(connections_internal[0,:])):
                if connections_internal[element_a_index,header_a_index] == connections_internal[0,header_b_index]:
                    if header_b_index == header_a_index:
                        continue
                    for element_b_index in range(1, len(connections_internal[:,header_b_index])):
                        if connections_internal[element_b_index,header_b_index] == connections_internal[0,header_a_index]:
                            break
                        elif connections_internal[element_b_index,header_b_index] == "":
                            connections_internal[element_b_index,header_b_index] = connections_internal[0,header_a_index]
                            break
    for header_index in range(len(connections_internal[0,:])):
        connections_internal[:,header_index][1:].sort()
        connections_internal[:,header_index][1:] = remove_duplicates(connections_internal[:,header_index][1:][::-1])
    numpy.savetxt(connections_file_path, connections_internal, fmt='%s', delimiter=',')


def find_paths(path):
    connected_header_index = find_in_array(connections[0,:], path[len(path)-1])-1
    for element in connections[1:,connected_header_index]:
        if find_in_array(path, element):
            continue
        elif str(element) == "":
            break
        elif str(element) == str(to_city):
            path.append(element)
            possible_paths.append(list(path))
            del path[-1]
            continue
        else:
            path.append(element)
            find_paths(path)
    del path[-1]


def shortest_paths(n_paths):
    find_paths([from_city, ])
    path_lengths = numpy.empty((len(possible_paths)),dtype=int)
    for index in range(len(possible_paths)):
        path_lengths[index] = path_length(possible_paths[index])
    sorted_indices = numpy.argsort(path_lengths)
    sorted_shortest_paths = numpy.array(possible_paths, dtype=object)[sorted_indices][0:n_paths]
    print("top " + str(n_paths) + " shortest paths are: " + str(sorted_shortest_paths) + " (sorted)")
    return sorted_shortest_paths


#numpy.set_printoptions(threshold=sys.maxsize)
connections, deliveries, coordinates = warmup()
list_deliveries(shortest_paths(number_of_paths_to_consider))