from json import load
from main import get_measure_sequence, create_jumps

file_names = ["situation1.json",
              "situation2.json",
              "situation3.json",
              "situation4.json",
              "situation4bis.json",
              "situation5.json",
              "situation6.json",
              "situation7.json",
              "situation8.json",
              "situation9.json",
              "situation10.json",
              ]

if __name__ == '__main__':
    for file_name in file_names:
        situation = load(open("data/" + file_name))
        expected = (situation['measure_sequence'])
        result = get_measure_sequence(create_jumps(situation['lists']), situation['total_number_of_measures'])
        print(situation["lists"])
        print("expected: ", expected)
        print("result  : ", result)
        print()
        assert expected == result