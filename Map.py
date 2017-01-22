import copy

class Map:
    def __init__(self, map_file):
        file_temp=open(map_file,'r')
        line_temp=file_temp.readline()
        # print line_temp
        self.__L = len([i for i in line_temp.split('\t') if i == '0'])
        self.__B = len(line_temp.split('\t'))
        # self.__L=len([i for i in line_temp .split(',') if i==' 0'])
        # self.__B=len(line_temp.split(','))
        self.__car_list=[]

        line_count=1
        while(file_temp.readline()):
            line_count+=1

        self.__length=line_count
        file_temp.close()

        map_temp=[[0 for i in range(self.__B)] for i in range(self.__length)]
        self.__map=[[0 for i in range(self.__length)] for i in range(self.__B)]

        file_temp=open(map_file)


        for i in range(self.__length):
            line_temp=file_temp.readline()
            line_temp = line_temp.split('\t')
            #line_temp=line_temp.split(',')

            for j in range(self.__B):
                if line_temp[j].strip()=='-1':
                    map_temp[i][j]=-1
                else:
                    map_temp[i][j]=0

        # print map_temp

        for i in range(self.__length):
            for j in range(self.__B):
                self.__map[j][self.__length-1-i]=map_temp[i][j]


    def get_L(self):
        return self.__L
    def get_B(self):
        return self.__B
    def get_length(self):
        return self.__length
    def show_map(self):
        for i in range(self.__length)[::-1]:
            for j in range(self.__B):
                if self.__map[j][i]==-1:
                    print str(self.__map[j][i]) + '\t',
                elif self.__map[j][i]==0:
                    print str(self.__map[j][i]) + '\t',
                    #print ' '+str(self.__map[j][i]),
                else:
                    print str(self.__map[j][i].car_id) + '\t',
                    #print ' '+str(self.__map[j][i].car_id),
            print('\n'),

    def is_road(self,x,y):
        if self.__map[x][y]!=-1:
            return 1
        else:
            return 0

    def have_car(self,x,y):
        if self.__map[x][y]!=0 and self.__map[x][y]!=-1:
            return 1
        else:
            return 0

    def put_car(self,x,y,car):
        self.__map[x][y]=car
        self.__car_list.append(car)

    def get_car(self,x,y):
        return self.__map[x][y]

    def is_road_can_go(self,x,y):
        if self.__map[x][y]==0:
            return 1
        else:
            return 0

    def move(self,car,x_start,y_start,x_end,y_end):

        self.__map[x_start][y_start]=0
        try:
            self.__map[x_end][y_end]=car
        except IndexError:
            print ("Car %d going out of map!" %(car.car_id))
            self.__car_list.remove(car)

    def avi(self):
        return self.__car_list


# have_car(x,y)
# put_cat(x,y,car)
# get_cat()
# is_road()


def test():
    t=Map('./map_scheme_test_1')
    print t.get_L()
    print t.get_B()
    print t.get_length()
    t.show_map()


if __name__=='__main__':
    test()