"""
    This is the best example to understand Closure concept
"""

def raise_to(exp):
    def raise_to_exp(x):
        return(pow(x,exp))
    return raise_to_exp

#test the above function

square = raise_to(2)
print("square(3)::{}".format(square(3)))  #Ans: 9
print("square(4)::{}".format(square(4)))  #Ans: 16

cube = raise_to(3)
print("cube(2)::{}".format(cube(2)))   #Ans: 8
print("cube(3)::{}".format(cube(3)))   #Ans: 27

print("done with closure test")