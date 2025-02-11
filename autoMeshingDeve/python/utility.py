import numpy as np

def can_P_project_to_AB(P,A,B):

#             projectable                        Not projectable
#
#                  P                                                     P
#                  |                                                     |
#                  |                                                     |
#                  |                                                     |  
#      A---------- H -----B                A------------------B          H
#       \     t    /                         \                          /
#                                                          t
    vector_AP = np.array([P.x-A.x,  P.y-A.y,  P.z-A.z])
    vector_AB = np.array([B.x-A.x,  B.y-A.y,  B.z-A.z])
    vector_AB_square = np.dot(vector_AB, vector_AB)
    t = np.dot(vector_AP,vector_AB) / vector_AB_square
    if 0 <= t and t <= 1:
        return True

def calculate_PH_length(P,A,B):
    vector_AP = np.array([P.x-A.x,  P.y-A.y,  P.z-A.z])
    vector_AB = np.array([B.x-A.x,  B.y-A.y,  B.z-A.z])
    vector_AB_square = np.dot(vector_AB, vector_AB)
    t = np.dot(vector_AP,vector_AB) / vector_AB_square
    vector_AH = t*vector_AB
    vector_PH = vector_AH - vector_AP
    return(np.linalg.norm(vector_PH))
