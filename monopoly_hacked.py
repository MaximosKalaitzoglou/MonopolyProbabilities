from asyncio.windows_events import NULL
from math import floor
import numpy as np

#all possible dice combinations (rolls)
dice_combinations = [[1,1], [1,2], [1,3], [1,4], [1,5], [1,6],
                    [2,1], [2,2], [2,3], [2,4], [2,5], [2,6],
                    [3,1], [3,2], [3,3], [3,4], [3,5], [3,6],
                    [4,1], [4,2], [4,3], [4,4], [4,5], [4,6],
                    [5,1], [5,2], [5,3], [5,4], [5,5], [5,6],
                    [6,1], [6,2], [6,3], [6,4], [6,5], [6,6]]

#monopoly_transition_matrix = [[0] * 12] * 40

class streets:

    def __init__(self) -> None:

        #position of the block i am standing
        self.pos = 0
        #name of the block i am standing
        self.name = 'start'

        self.substreets = []
        #array with the special events : Tax , goto Jail, Jail, Free parking, chance, community chest
        self.special_events = [2, 7, 17, 22, 33, 36]

        self.Tax = [4, 38]

        self.Big4 = [0,10,20,30]

        
        #Array containing the matrix location of railroads
        self.railsroads = [5, 15, 25, 35]
        #Array containing the electricity and water supply blocks
        self.Deh = [12, 28]
        #regions of color blocks
        self.regions = []
    
    def initSubstreets(self):
        # full array of number up to 40 (our board has 40 boxes)
        full_arr = [x for x in range(0,40)]
        
        # we get the difference of the full array of numbers and the special cases (electric, railroads, events) and we get 
        #the street blocks of monopoly
        #now we can subdivide them by 3 (except the brown blocks which are 2 and get the correct regions of each color)
        street_arr = self.Diff(full_arr,self.Deh + self.railsroads + self.special_events + self.Tax + self.Big4)

        #print(street_arr)

        #print(self.regions) 
        
        #iterate street_arr and make regions for each color 
        # brown = 2, light blue = 3, .. .. , dark blue = 2
        for i in range(2,len(street_arr) - 2,3):

            self.regions.append([street_arr[i], street_arr[i+1], street_arr[i+2]])

        self.regions.insert(0,[1, 3])

        self.regions.append([37, 39])

        print(self.regions)
        
            

    def getCurrentRegion(self,current_pos):
        self.pos = current_pos

    def Diff(self,li1, li2):

        return list(set(li1) - set(li2)) + list(set(li2) - set(li1))


class monopoly:
    def __init__(self) -> None:
        self.monopoly_transition_matrix = [[0] * 12] * 40
        self.current_position = 'start'


    def find_dice_probabilities(self):

        numberCount = [0] * 12

        for rolls in dice_combinations:

            diceSum = rolls[0] + rolls[1]

            for num in range(0,12):

                if diceSum == (num + 1):

                    numberCount[num] += 1
        
        print(numberCount)
        n = 1/36
        number_probabilities = [round(x * n,2) for x in numberCount]
        return number_probabilities
    

            






if __name__ == '__main__':
    print('hello')
    #monopoly object


    #streets object
    hood = streets()
    hood.initSubstreets()
    


