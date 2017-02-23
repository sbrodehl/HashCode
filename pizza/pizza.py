import numpy as np

min_cells_per_slice = 0
max_cells_par_slice = 0
min_ingredients_per_slice = 0
all_slices = []
pizza_array = []

pizza_rows = 0
pizza_cols = 0


def find_best_solution(input_file_name):
    global pizza_array

    pizza_array = np.array(read_in_file(input_file_name))
    find_all_slices()

    solutions = []

    for slice in all_slices:
        solutions.append([slice])

    best_solution = []
    best_score = 0

    for solution in solutions:
        score = calc_points_of_solution(solution)
        if score > best_score:
            best_score = score
            best_solution = solution

    for slices in range(2, 2000):
        solutions = add_slice([best_solution])
        for solution in solutions:
            score = calc_points_of_solution(solution)
            if score > best_score:
                best_score = score
                best_solution = solution
                break

        if len(solutions) == 0:
            break

    print(best_score)
    return best_solution


def add_slice(former_solutions):
    global all_slices

    new_solutions = []
    for former_solution in former_solutions:
        for slice in all_slices:
            collission = False
            for solution_slice in former_solution:
                if check_collission(solution_slice, slice):
                    collission = True
                    break
            if not collission:
                new_solutions.append(former_solution + [slice])
                return new_solutions
    return new_solutions


def calc_points_of_solution(solution=[]):
    score = 0
    for solution_slice in solution:
        rowCells = abs(solution_slice[0] - solution_slice[2]) + 1
        colCells = abs(solution_slice[1] - solution_slice[3]) + 1
        score += rowCells * colCells
    return score


def check_collission(rec1=[], rec2=[]):
    return not (
        (rec1[3] < rec2[1]) or  # right
        (rec2[3] < rec1[1]) or  # left
        (rec1[2] < rec2[0]) or  # up
        (rec2[2] < rec1[0]))  # down


def find_all_slices():
    global all_slices
    all_slices = []

    # Get vertical slices of size n
    for counter in range(14, max_cells_par_slice + 1):
        all_slices.extend(find_all_slices_by_max_cells(counter))


def find_all_slices_by_max_cells(cells):
    slices = []

    for rowStep in range(1, 27):
        if cells % rowStep != 0:
            continue

        colStep = int(cells / rowStep)

        for rowIndex in range(0, pizza_rows - rowStep + 1):
            for colIndex in range(0, pizza_cols - colStep + 1):
                if check_ingridient_constraint([rowIndex, colIndex, rowIndex + rowStep - 1, colIndex + colStep - 1]):
                    slices.append([rowIndex, colIndex, rowIndex + rowStep - 1, colIndex + colStep - 1])

    return slices


def check_ingridient_constraint(rec=[]):
    global pizza_array
    global min_ingredients_per_slice
    count_tomatos = 0
    count_mushrooms = 0

    if rec[0] == rec[2]:
        for col in range(rec[1], rec[3] + 1):
            if pizza_array[rec[0]][col] == 'T':
                count_tomatos += 1
            else:
                count_mushrooms += 1
    elif rec[1] == rec[3]:
        for row in range(rec[0], rec[2] + 1):
            if pizza_array[row][rec[1]] == 'T':
                count_tomatos += 1
            else:
                count_mushrooms += 1
    else:
        for row in range(rec[0], rec[2] + 1):
            for col in range(rec[1], rec[3] + 1):
                if pizza_array[row][col] == 'T':
                    count_tomatos += 1
                else:
                    count_mushrooms += 1

    return count_tomatos >= min_ingredients_per_slice and count_mushrooms >= min_ingredients_per_slice


def read_in_file(file_name):
    pizza_array = []
    input_file = open(file_name, "r")

    # read in header
    header = input_file.readline()
    header = header.replace("\n", "")
    splitted_header = header.split(' ')

    global pizza_rows
    global pizza_cols
    global min_ingredients_per_slice
    global max_cells_par_slice
    global max_number_of_slices
    global min_cells_per_slice

    pizza_rows = int(splitted_header[0])
    pizza_cols = int(splitted_header[1])
    min_ingredients_per_slice = int(splitted_header[2])
    max_cells_par_slice = int(splitted_header[3])

    min_cells_per_slice = int(min_ingredients_per_slice * 2)
    max_number_of_slices = int((pizza_cols * pizza_rows) / min_cells_per_slice)

    for line in input_file:
        line = line.replace("\n", "")
        pizza_array.append(list(line))

    input_file.close()
    return pizza_array


# for former_solution in damenproblem(8, 8):
#    print(former_solution)

def write_output_file(solution_file_name, solution=[]):
    f = open(solution_file_name, "a+")
    f.write(str(len(solution)) + "\n")

    for slice in solution:
        f.write(str(slice[0]) + " " + str(slice[1]) + " " + str(slice[2]) + " " + str(slice[3]) + "\n")

    f.close()





write_output_file("solution_big.txt", find_best_solution("big.in"))