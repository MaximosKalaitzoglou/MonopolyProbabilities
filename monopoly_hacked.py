from asyncio.windows_events import NULL
import pandas as pd
from re import X
import numpy as np
from collections import deque
import matplotlib.pyplot as plt
 
from scipy.linalg import eig


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
        self.chance = [7, 22, 36]
        self.community_chest = [22, 17, 33]

        self.Tax = [4, 38]

        self.Big4 = [0,10,20,30]

        self.square_names = ["Go","Mediterranean Avenue","Community Chest1","Baltic Avenue","Income Tax","Reading Railroad","Oriental Avenue",
                            "Chance1","Vermont Avenue","Connecticut Avenue","Jail / Just Visiting","St. Charles Place","Electric Company","States Avenue","Virginia Avenue","Pennsylvania Railroad",
                            "St. James Place","Community Chest2","Tennessee Avenue","New York Avenue","Free Parking","Kentucky Avenue","Chance2","Indiana Avenue","Illinois Avenue","B. & O. Railroad",
                            "Atlantic Avenue","Ventnor Avenue","Water Works","Marvin Gardens","Go To Jail","Pacific Avenue","North Carolina Avenue","Community Chest3","Pennsylvania Avenue",
                            "Short Line","Chance3","Park Place","Luxury Tax","Boardwalk"]
        
        #Array containing the matrix location of railroads
        self.railsroads = [5, 15, 25, 35]
        #Array containing the electricity and water supply blocks
        self.Deh = [12, 28,200]
        #regions of color blocks
        self.regions = []
    
    def initSubstreets(self):
        # full array of number up to 40 (our board has 40 boxes)
        full_arr = [x for x in range(0,40)]
        
        # we get the difference of the full array of numbers and the special cases (electric, railroads, events) and we get 
        #the street blocks of monopoly
        #now we can subdivide them by 3 (except the brown blocks which are 2 and get the correct regions of each color)
        street_arr = self.Diff(full_arr,self.Deh + self.railsroads + self.chance + self.community_chest + self.Tax + self.Big4)

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


class markov_chains:
    def __init__(self) -> None:
        self.monopoly_transition_matrix = np.zeros(shape=(40,40))
        self.current_position = 'start'
        self.new_street = streets()



    def find_dice_probabilities(self):

        numberCount = [0] * 12

        for rolls in dice_combinations:

            diceSum = rolls[0] + rolls[1]

            for num in range(0,12):

                if diceSum == (num + 1):

                    numberCount[num] += 1
        
        #print(numberCount)
        n = 1/36
        number_probabilities = [round(x * n,2) for x in numberCount]
        return number_probabilities
    

    def setup_transition_matrix(self):
        #set markov probability transition matrix based on probabilities of dice rolls
        #only for street blocks
        #we need to add also special event blocks

        transition_prob = self.find_dice_probabilities()
        
        #print(transition_prob)
        for j in range(0,12):
            self.monopoly_transition_matrix[0][j] = transition_prob[j]
        
        temp = self.monopoly_transition_matrix[0]
        

        for i in range(1,40):
            if  i != 30 and i != 10:

                self.monopoly_transition_matrix[i] = np.roll(temp,i)
            else:
                if i == 30:
                    #if go to jail block is visited you can only go to jail
                    self.monopoly_transition_matrix[i][10] = 1.0
        
        
        #
        self.when_in_Jail()

        #chance square 
        self.chance_square_probs()
        #Community chest square  
        self.community_chest_probs()
        #rolling 3 doubles prob
        self.roll_3_doubles()

        #self.check_sum_of_rows()

        

        np.savetxt("transition_matrixDoubles.csv",self.monopoly_transition_matrix, fmt = '%.5f')
        
            
    def distance_nearest(self,i,to):
        nearest = 90
        near_pos = -1
        for r in to:
            if abs(r - i) < nearest:
                nearest = abs(r-i)
                near_pos = r
            #if r == 12 or r == 28:
                #print("i = 22 , railroad = %d , (r-i) = %d" % (r,near_pos))
            
        #print(near_pos)
        return near_pos   
        #print(self.monopoly_transition_matrix)
    

    def chance_square_probs(self):
        #chance and community chest squares
        for i in self.new_street.chance:
            for j in range(i-12,i):
                p = self.monopoly_transition_matrix[j][i]
                #Reading railroad
                self.monopoly_transition_matrix[j][5] += (1/16) * p
                #illinois square
                self.monopoly_transition_matrix[j][24] += (1/16)*p
                #Charles place
                self.monopoly_transition_matrix[j][11] += (1/16)*p 
                #broadwalk
                self.monopoly_transition_matrix[j][39] += (1/16)*p
                #Jail
                self.monopoly_transition_matrix[j][10] += (1/16)*p
                #Go
                self.monopoly_transition_matrix[j][0] += (1/16)*p
                #Go back three spaces
                self.monopoly_transition_matrix[j][i-3] += (1/16)*p 
                #Nearest railroad
                #print(i)
                nearest = self.distance_nearest(i,self.new_street.railsroads)
                
                self.monopoly_transition_matrix[j][nearest] += (2/16)*p     
                #Nearest utility
                nearest = self.distance_nearest(i,self.new_street.Deh)
                self.monopoly_transition_matrix[j][nearest] += (1/16)*p


    def community_chest_probs(self):
       for c in self.new_street.community_chest:
            for j in range(c-12,c-2):
                p = self.monopoly_transition_matrix[j][c]      
                #Go to jail
                self.monopoly_transition_matrix[j][10] += (1/16)*p
                #go to start
                self.monopoly_transition_matrix[j][0] += (1/16)*p
                

   
    def most_likely_to_visit(self,stationary):
        m = {}
        for i in range(0,40):
            m[self.new_street.square_names[i]] = stationary[i]
        m = dict(sorted(m.items(), key = lambda item: item[1], reverse=True))
        print(m)
        self.export_to_xlsx(m)
        
    def export_to_csv(self,m):
        csv_columns = ['Square Name', 'Probability of visiting']
        csv_file = 'most_likely_to_visit.csv'
        df = pd.DataFrame(m.items(), columns=["Square Name", "Probability of Visiting"]) 
        df.to_csv(csv_file)

    def export_to_xlsx(self,m):
        xl_file = 'most_likely_to_visit.xlsx'
        df = pd.DataFrame(m.items(), columns=["Square Name", "Probability of Visiting"])
        df.to_excel(xl_file); 
    
    def stationary_distribution(self):
        #left eigen vectors close to 1 for the transition matrix
        #so that we can get the stationary distribution also known by the equations
        # w * P = w 

        v = eig(self.monopoly_transition_matrix,left=True,right=False)[1][:,0]
        
        # normalize v 
        stationary = v / v.sum()
        
        #eigs finds complex eigenvalues and eigenvectors, so you'll want the real part.
        stationary = stationary.real
        np.savetxt("stationary_distribution.csv",stationary, fmt = '%.5f')
        self.most_likely_to_visit(stationary)
        #print(stationary)
        
        
        


    def check_sum_of_rows(self):
        count = 0
        for row in self.monopoly_transition_matrix:
            
            prob_sum = sum(row)
            print("Probability sum of row : %d = %d"%(count,prob_sum))
            count += 1

    def roll_3_doubles(self):
        #rolling 3 doubles has a probability of (1/6) ^ 3 (we have 6 possible double outcomes)
        #so the probability of going to jail at any given time is 1/216 (from any block)
        #we need to add this probability to our transition matrix P
        # this though will mess up the sum of the rows making them greater or lower than 1 we can;t have that
        # So its a simple equation to figure out how to overcome this 
        # We know that sum(row) for row in transition_matrix = 1 so now we have:
        # x (sum of rows) = 1 => x = 1/sum of rows
        for row in self.monopoly_transition_matrix:
            row[10] = row[10] + 1/216
            sumOfRow = sum(row)
            e = 1/sumOfRow
            row = [x * e for x in row]
        #self.check_sum_of_rows()
    
    def when_in_Jail(self):
        #when you are in jail you can only get out after 3 rounds 
        #or when you roll a double
        # we have 6 doubles that sum to the numbers -> 2, 4, 6, 8, 10, 12
        #so let's fix our jail square each of the doubles has a prob of occuring 1/6
        # also we can roll 3 doubles so we can end up on the jail square again
        

        for i in range(12,22,2):
            self.monopoly_transition_matrix[10][i] += 1/6
        self.monopoly_transition_matrix[10][10] += 1/216
        self.monopoly_transition_matrix[10][22] += 1/6
        


if __name__ == '__main__':
    print('hello')
    #monopoly object
    mynopoly = markov_chains()
    mynopoly.setup_transition_matrix()
    mynopoly.stationary_distribution()
    #my_data = pd.read_csv('most_likely_to_visit.csv')
    #print(my_data.head(10))
    
    #plt.hist(my_data['Square Name','Probability of Visiting'], color ='blue', edgecolor= 'black', bins = int(180/5))
    #plt.show()









    #h = streets()
    #print(h.square_names)
    #probabilities need to add up to 1 if not we made an error
    #mynopoly.check_sum_of_rows()

    #streets object
    #new_street = streets()
    #new_street.initSubstreets()

    
    


