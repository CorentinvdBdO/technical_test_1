from json import load

REPEAT_FORWARD = 'repeat_forward'
REPEAT_BACKWARD = 'repeat_backward'
ENDING_ONE = 'ending_one'
ENDING_TWO = 'ending_two'
SEGNO = 'segno'
DALSEGNO = 'dalsegno'
DACAPO = 'dacapo'
TOCODA = 'tocoda'
CODA = 'coda'


class Jump:
    # This class defines any kind of flash forward or backwards

    def __init__(self, start, finish, coda_compatible, single_use=True):
        # start : int : the starting bar
        # finish : int : the bar to go to
        # coda_compatible : bool : True for da capo and segno
        # single_use : bool : True for segno as it is the only jump that can be replayed

        self.start = start
        self.finish = finish
        self.coda_compatible = coda_compatible
        self.forward = start < finish
        self.single_use = single_use


def create_jumps(jumps_dict):
    # Create the jumps from the provided list
    # repeats come before dal segno and da capo to preserve priority
    # The list is ordered by the starting point

    # Error types:
    #   1. Different number of start/end points                         CHECKED
    #   2. start < finish for backwards and opposite for forward jumps  CHECKED
    #   3. Jump forward without a previous jump backward                IGNORED (no consequence)

    jumps_list = []

    for i in range(min(len(jumps_dict[REPEAT_BACKWARD]), len(jumps_dict[REPEAT_FORWARD]))):
        if jumps_dict[REPEAT_BACKWARD][i] > jumps_dict[REPEAT_FORWARD][i]:
            jumps_list += [Jump(
                jumps_dict[REPEAT_BACKWARD][i],
                jumps_dict[REPEAT_FORWARD][i],
                False)]
    for i in range(min(len(jumps_dict[ENDING_ONE]), len(jumps_dict[ENDING_TWO]))):
        if jumps_dict[ENDING_ONE][i] < jumps_dict[ENDING_TWO][i]:
            jumps_list += [Jump(
                jumps_dict[ENDING_ONE][i],
                jumps_dict[ENDING_TWO][i],
                False)]
    for i in range(min(len(jumps_dict[DALSEGNO]), len(jumps_dict[SEGNO]))):
        if jumps_dict[DALSEGNO][i] > jumps_dict[SEGNO][i]:
            jumps_list += [Jump(
                jumps_dict[DALSEGNO][i],
                jumps_dict[SEGNO][i],
                True,
                False)]  # Segno / dal segno can be replayed
    for i in range(len(jumps_dict[DACAPO])):
        jumps_list += [Jump(
            jumps_dict[DACAPO][i],
            1,
            True)]
    for i in range(min(len(jumps_dict[TOCODA]), len(jumps_dict[CODA]))):
        if jumps_dict[TOCODA][i] < jumps_dict[CODA][i]:
            jumps_list += [Jump(
                jumps_dict[TOCODA][i],
                jumps_dict[CODA][i],
                True)]

    return sorted(jumps_list, key=lambda x: x.start)  # Sort the jumps by their starting measure


def get_measure_sequence(jumps_list, total_measures):
    current_measure = 1
    measures_sequence = []
    multiple_use_jumps = [jump for jump in jumps_list if
                          jump.single_use is False]  # Segno can be played again and should not be removed completely
    jumps_forward = [jump for jump in jumps_list if jump.forward]
    jumps_list = [jump for jump in jumps_list if not jump.forward]

    while current_measure <= total_measures:
        if jumps_list != [] and jumps_list[0].start == current_measure:  # Jumps are sorted by starting measure and type
            jump = jumps_list.pop(0)  # The jump should not replay (segno treated bellow)

            if not jump.forward:  # Jump backward
                # Jump backward -> load compatible jumps forward
                jumps_list += [j for j in jumps_forward
                               if j.start < jump.start  # take the jumps before the current one
                               and jump.coda_compatible == j.coda_compatible][  # that are of the same type
                              -1:]  # keep the last one only

                # Jump backward -> load multiple use jumps again (segno/dal segno pair)
                reuse_backward = [j for j in multiple_use_jumps
                                  if j.start < jump.start      # The jumps must be within the replayed part
                                  and j.finish >= jump.finish]

                jumps_list = sorted(reuse_backward + jumps_list,
                                    key=lambda x: x.start)  # Put the jump(s) in the right place

            measures_sequence += [current_measure]  # The measure is played
            current_measure = jump.finish  # Jump to the measure

        else:  # No jump
            measures_sequence += [current_measure]  # The measure is played
            current_measure += 1  # No jump

    return measures_sequence


if __name__ == '__main__':
    situation = load(open("data/situation3.json"))
    print(situation)
    print(situation['measure_sequence'])
    print(get_measure_sequence(create_jumps(situation['lists']), situation['total_number_of_measures']))
