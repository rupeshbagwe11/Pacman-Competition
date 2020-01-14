# pacmanAgents.py
# ---------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from pacman import Directions
from game import Agent
import random
import math

class CompetitionAgent(Agent):
    # Initialization Function: Called one time when the game starts
    def registerInitialState(self, state):
        self.mWalls = None
        self.mPellets = None
        self.mCapsules = None

        self.mTargetDepth = 3
        self.mTotalGhosts = 0

        self.mPPossibleActions = None
        self.mGPossibleCombos = None

        self.mPelletsConsumePoints = 100
        self.mFarFromGhostPoints = 10
        self.mClosestNextFoodPoints = 5

        return

    # GetAction Function: Called with every frame
    def getAction(self, state):

        self.mWalls = state.getWalls()
        self.mPellets = state.getPellets()
        self.mCapsules = state.getCapsules()

        lPCIndex = state.getPacmanPosition()
        self.mPPossibleActions = state.getAllPossibleActions()

        lGIndexesF = state.getGhostPositions()
        lGIndexes = [(int(x), int(y)) for x, y in lGIndexesF]
        self.mTotalGhosts = len(lGIndexes)
        lAllGhostsActionsComboTotal = pow(4,  self.mTotalGhosts)
        lGhostsActionsComboList = []
        for i in range(0, lAllGhostsActionsComboTotal):
            lGhostsActionsComboList.append(self.getAllGhostsActionsCombo(i, self.mTotalGhosts))
        self.mGPossibleCombos = lGhostsActionsComboList

        self.mPelletsConsumePoints = 100
        self.mFarFromGhostPoints = 10
        self.mClosestNextFoodPoints = 5

        lMinDistFromCGhost, lClosestGhost = self.getClosestConsideringWall(lPCIndex,lGIndexes)
        if lMinDistFromCGhost < 3:
            self.mPelletsConsumePoints = 25
            self.mFarFromGhostPoints = 100
            self.mClosestNextFoodPoints = 5

        lMinDistFromCPellet, lClosestPellet = self.getClosest(lPCIndex, self.mPellets)
        if lMinDistFromCPellet > 1 and self.mFarFromGhostPoints != 100:
            self.mPelletsConsumePoints = 25
            self.mClosestNextFoodPoints = 100
            self.mFarFromGhostPoints = 5

        lEmptyAction = []
        lScore, lBestAction = self.getBestScoreActionMinMax(0, True, lPCIndex, lGIndexes, lEmptyAction)
       # print(lScore,lBestAction)

        return lBestAction

    def getAllGhostsActionsCombo(self, pActionNo, pTotalGhosts):
        lGhostsActionCombo = []
        lGhostsActionIndex = self.covertToBase(pActionNo, 4, pTotalGhosts)
        for i in range(0, pTotalGhosts):
            lGhostsActionCombo.append(self.getPossibleDirection(lGhostsActionIndex[i]))
        return lGhostsActionCombo

    def covertToBase(self, pNo, pBase, pLength):
        lAns = []
        for i in range(0, pLength):
            lAns.append(0)
        j = pLength - 1
        while pNo > 0:
            lAns[j] = pNo % pBase
            pNo = pNo // pBase
            j = j - 1
        return lAns

    def getPossibleDirection(self, pIndex):
        if pIndex == 0:
            return Directions.NORTH
        elif pIndex == 1:
            return Directions.EAST
        elif pIndex == 2:
            return Directions.SOUTH
        elif pIndex == 3:
            return Directions.WEST
        return Directions.STOP


    def getClosestConsideringWall(self,pPos, pPosArray):
        lMinDist = 10000
        lClosestPosition = (-1, -1)
        for i in range(0, len(pPosArray)):
            lDistBetweenPosition = self.getDistanceBWPos(pPos, pPosArray[i])
            if self.isWallInMiddle(pPos,pPosArray[i]):
                lDistBetweenPosition = lDistBetweenPosition + 4
            if lDistBetweenPosition < lMinDist:
                lMinDist = lDistBetweenPosition
                lClosestPosition = pPosArray[i]
        return lMinDist, lClosestPosition





    def getClosest(self, pPos, pPosArray):
        lMinDist = 10000
        lClosestPosition = (-1, -1)
        for i in range(0,len(pPosArray)):
            lDistBetweenPosition = self.getDistanceBWPos(pPos, pPosArray[i])
            if lDistBetweenPosition < lMinDist:
                lMinDist = lDistBetweenPosition
                lClosestPosition = pPosArray[i]
        return lMinDist, lClosestPosition

    def getDistanceBWPos(self, pPos1, pPos2):
        lXdiff = abs( pPos1[0] - pPos2[0] )
        lYdiff = abs( pPos1[1] - pPos2[1] )
        lTdiff = lXdiff + lYdiff
        return lTdiff

    def getBestScoreActionMinMax(self,pCDepth, pMaxMin, pPIndex, pGIndexes, pMovedIndexes):

        if pCDepth == self.mTargetDepth:
            return self.getWinningProb(pPIndex, pGIndexes, pMovedIndexes), pMovedIndexes

        if pMaxMin == True:
            lBestScore = -999999999
            lBestAction = Directions.STOP

            for lPAction in self.mPPossibleActions:
                # print(lPAction)
                lMovedIndexes = list(pMovedIndexes)
                lbIsValidPNIndex, lPacmanNIndex = self.getValidPacmanNewIndex(pPIndex, lPAction)
                if lbIsValidPNIndex == False:
                    continue

                lMovedIndexes.append(lPacmanNIndex)
                lScore, lTempDir = self.getBestScoreActionMinMax(pCDepth+1,False,lPacmanNIndex,pGIndexes,lMovedIndexes)
                # print(str(lScore) + " " + str(lPAction))
                if lScore > lBestScore:
                    lBestScore = lScore
                    lBestAction = lPAction

            return lBestScore, lBestAction
        else:
            lTotalScore = 0
            lTotalValidGhostActions = 0

            for lGActionCombo in self.mGPossibleCombos:
                lbIsValidGNIndexes, lGhostNIndexes = self.getValidGhostNewIndexes(pGIndexes, lGActionCombo)
                if lbIsValidGNIndexes == False:
                    continue

                lScore, lTempDir = self.getBestScoreActionMinMax(pCDepth + 1, False, pPIndex, lGhostNIndexes,
                                                                 pMovedIndexes)

                lTotalScore = lTotalScore + lScore
                lTotalValidGhostActions = lTotalValidGhostActions + 1

            #Average is taken in place of min since ghost aren't optimal but random
            lAverageScore = int(lTotalScore/lTotalValidGhostActions)

            return lAverageScore, pMovedIndexes


    def getValidGhostNewIndexes(self, pGIndexes, pGhostActionCombos):
        lGNIndexes = []
        for i in range(0, self.mTotalGhosts):
            lGCIndex = pGIndexes[i]
            lGNIndexes.append(self.getNewIndex(pGhostActionCombos[i], lGCIndex))
            if (self.mWalls[lGNIndexes[i][0]][lGNIndexes[i][1]] == True):
                return False, lGNIndexes
        return True, lGNIndexes

    def getValidPacmanNewIndex(self, pPIndex, pAction):
        lPNIndex = self.getNewIndex(pAction, pPIndex)
        if self.mWalls[lPNIndex[0]][lPNIndex[1]] == True:
            return False, lPNIndex
        return True, lPNIndex

    def getNewIndex(self, pDirection, pCIndex):
        if pDirection == Directions.EAST:
            pNIndex = pCIndex[0] + 1, pCIndex[1]
            return pNIndex
        elif pDirection == Directions.WEST:
            pNIndex = pCIndex[0] - 1, pCIndex[1]
            return pNIndex
        elif pDirection == Directions.NORTH:
            pNIndex = pCIndex[0], pCIndex[1] + 1
            return pNIndex
        elif pDirection == Directions.SOUTH:
            pNIndex = pCIndex[0], pCIndex[1] - 1
            return pNIndex
        return pCIndex

    def getWinningProb(self, pPIndex, pGIndexes, pMovedIndexes):

        lWinningChance = 0
        lPellets = list(self.mPellets)
        lCapsules = list(self.mCapsules)

        for i in range(0, len(pMovedIndexes)):
            if pMovedIndexes[i] in lPellets:
                lWinningChance = lWinningChance + self.mPelletsConsumePoints
                lPellets.remove(pMovedIndexes[i])
            if pMovedIndexes[i] in lCapsules:
                lWinningChance = lWinningChance + self.mPelletsConsumePoints + 50
                lCapsules.remove(pMovedIndexes[i])

        # if len(lPellets) == 0:    print("PC" + str(lWinningChance))

        if len(lPellets) == 0 and len(lCapsules) == 0:
            lWinningChance = lWinningChance + 10000

        lMinDistFromGhost, lClosestGhost = self.getClosest(pPIndex, pGIndexes)
        if lMinDistFromGhost == 0:
            lWinningChance = lWinningChance - 10000
        else:
            lWinningChance = lWinningChance + ( lMinDistFromGhost * self.mFarFromGhostPoints)

        # print(self.mFarFromGhostPoints)
        # if len(lPellets) == 0: print("GP" + str(lMinDistFromGhost * self.mFarFromGhostPoints))

        if len(lPellets) != 0 or len(lCapsules) != 0:
            lMinDistFromRemPellets, lClosestPellets = self.getClosestConsideringWall(pPIndex, lPellets)
            lWinningChance = lWinningChance + (lMinDistFromRemPellets * -self.mClosestNextFoodPoints)

        #print(self.mClosestNextFoodPoints)
            # if len(lPellets) == 1:
            # print("CF" + str(lMinDistFromRemPellets * -self.mClosestNextFoodPoints))

        lRandomWinningChance = random.randint(1, 11)
        lWinningChance = lWinningChance + lRandomWinningChance

        return lWinningChance

    def isWallInMiddle(self,pIndex1,pIndex2):
        if pIndex1[0] == pIndex2[0]:
            ldiff = pIndex2[1] - pIndex1[1]
            if ldiff > 0:
                for i in range(1,ldiff):
                    if(self.mWalls[pIndex1[0]][pIndex1[1] + i]):
                        return True
            else:
                for i in range(ldiff+1,0):
                    if(self.mWalls[pIndex1[0]][pIndex1[1] + i]):
                        return True

        elif pIndex1[1] == pIndex2[1]:
            ldiff = pIndex2[0] - pIndex1[0]
            if ldiff > 0:
                for i in range(1,ldiff):
                    if(self.mWalls[pIndex1[0] + i][pIndex1[1]]):
                        return True
            else:
                for i in range(ldiff+1,0):
                    if(self.mWalls[pIndex1[0] + i][pIndex1[1]]):
                        return True

        return False





