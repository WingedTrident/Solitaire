import pygame
import pygame.freetype
import random
import sys
from pygame.locals import*

#init
pygame.init()

#Window Dimensions
SCREEN_WIDTH = 1350
SCREEN_HEIGHT = 950
SCREEN_TITLE = "Solitaire v0.1"

#screen
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(SCREEN_TITLE)

#fps
FPS = 30
FPS_CLOCK = pygame.time.Clock()

#FONTS
GAME_FONT = pygame.freetype.Font("./fonts/ARCADEPI.TTF")

#image fast load
def load(imageName, with_alpha = True):
    imageLink = pygame.image.load(f"./assets/{imageName}.png")
    if with_alpha:
        return imageLink.convert_alpha()
    else:
        return imageLink.convert()
    
class Card():
    def __init__(self, type, number):
        self.type = type
        self.number = number
        self.sprite = load(f"{self.type}{self.number}")
        if (self.type == "clover" or self.type == "spade"):
            self.color = "black"
        elif (self.type == "heart" or self.type == "diamond"):
            self.color = "red"
        self.backSprite = load("card_back")
        self.x = 0
        self.y = 500
        self.height = 200
        self.width = 150
        self.showBack = False
        self.bottomCard = False
          
    def blit(self):
        if (self.showBack):
            SCREEN.blit(self.backSprite, (self.x, self.y)) 
        else:    
            SCREEN.blit(self.sprite, (self.x, self.y))  
            
class CardHolder():
    def __init__(self, type, x, y):
        self.type = type   
        self.sprite = load(f"empty{type}") 
        self.x = x
        self.y = y
        self.acceptedNumber = 1
        self.cards = []
        
    def blit(self):
        SCREEN.blit(self.sprite, (self.x, self.y))  
        
        if (len(self.cards) != 0):
            if (len(self.cards) > 1):
                SCREEN.blit(self.cards[len(self.cards)-2].sprite, (self.x, self.y)) 
            SCREEN.blit(self.cards[len(self.cards)-1].sprite, (self.cards[len(self.cards)-1].x, self.cards[len(self.cards)-1].y))   
                
class GameScreen():
    def __init__(self):
        self.deck = [] 
        self.allPiles = [[], [], [], [], [], [], []]
        self.extraPile = []
        self.selectedCard = None
        self.selectedCardPile = None
        
        self.saveOriginalPos = []
        self.pointofMouseCollision = []
        
        self.moveList = []
        
        self.cardHolders = [CardHolder("spade", 530, 30), CardHolder("clover", 690, 30), CardHolder("heart", 850, 30), CardHolder("diamond", 1010, 30)]
        self.emptyDeck = load("emptyDeck")
        
        self.extraPileBookmark = -1
        
        self.cardBack = load("card_back")
        
        self.winCondition = 0
        
        self.clicks = 0
        self.moves = 0
        self.timeMinutes = 0
        self.timeSeconds = 0
        self.startTime = 0
        
        self.retryButton = False
        self.autoWinButton = False
        self.quitButton = False
        self.pauseButton = False
        
        self.cardOffset = 40
        self.timeStage = 0
        
    def trackTime(self):
        if (self.clicks > 0 and self.timeStage == 0):
            self.timeStage = 1
        if (self.timeStage == 1):
            self.startTime = pygame.time.get_ticks()
            self.timeStage = 2
        elif (self.timeStage == 2):
            time = pygame.time.get_ticks() - self.startTime
            self.timeSeconds = round(time/1000)
            if (self.timeSeconds >= 60):
                self.timeMinutes += 1
                self.timeSeconds = 0
                self.startTime = pygame.time.get_ticks()
        if (self.timeSeconds < 10):        
            GAME_FONT.render_to(SCREEN, (1165, 250), f"Time: {self.timeMinutes}:0{self.timeSeconds}", "black", size=25)       
        else:
            GAME_FONT.render_to(SCREEN, (1165, 250), f"Time: {self.timeMinutes}:{self.timeSeconds}", "black", size=25)
    
    def pauseScreen(self):
        save = pygame.time.get_ticks() - self.startTime
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.startTime = pygame.time.get_ticks() - save
                    main()       
            GAME_FONT.render_to(SCREEN, (450, 450), "PAUSED", "blue", size=90)
            GAME_FONT.render_to(SCREEN, (300, 550), "Press Anywhere To Unpause", "blue", size=35)
            pygame.display.update()
            FPS_CLOCK.tick(FPS)        
                    
    def endScreen(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()  
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if (self.retryButton):
                        self.resetGame()
                        main()
                    if (self.quitButton):
                        pygame.quit()
                        sys.exit() 
        
            pygame.draw.rect(SCREEN, (163, 163, 163), (500, 250, 400, 450))
            GAME_FONT.render_to(SCREEN, (530, 280), "Round Complete", "black", size=35)
            GAME_FONT.render_to(SCREEN, (530, 330), f"Clicks: {self.clicks}", "black", size=35)
            GAME_FONT.render_to(SCREEN, (530, 382), f"Moves: {self.moves}", "black", size=35)
            if (self.timeSeconds < 10):
                GAME_FONT.render_to(SCREEN, (530, 430), f"Time: {self.timeMinutes}:0{self.timeSeconds}", "black", size=35)
            else:    
                GAME_FONT.render_to(SCREEN, (530, 430), f"Time: {self.timeMinutes}:{self.timeSeconds}", "black", size=35)
            GAME_FONT.render_to(SCREEN, (530, 485), f"Rem Cards: {self.getRemainingCardNum()}", "black", size=35)    
                
            if (Rect(620, 550, 167, 35).collidepoint(pygame.mouse.get_pos())):
                GAME_FONT.render_to(SCREEN, (620, 550), f"RETRY", "white", size=45)
                self.retryButton = True
            else:
                GAME_FONT.render_to(SCREEN, (620, 550), f"RETRY", "black", size=45)       
                self.retryButton = False
            if (Rect(640, 620, 130, 35).collidepoint(pygame.mouse.get_pos())):
                GAME_FONT.render_to(SCREEN, (640, 620), f"QUIT", "white", size=45)
                self.quitButton = True
            else:   
                GAME_FONT.render_to(SCREEN, (640, 620), f"QUIT", "black", size=45)        
                self.quitButton = False
                    
            pygame.display.update()
            FPS_CLOCK.tick(FPS)          
           
    def blitWin(self):
        pygame.draw.rect(SCREEN, (0, 0, 0), (1200, 180, 100, 50))
        pygame.draw.rect(SCREEN, (163, 163, 163), (1203, 183, 94, 44))
        if (Rect(1203, 183, 94, 44).collidepoint(pygame.mouse.get_pos())):
            GAME_FONT.render_to(SCREEN, (1206, 197), "Pause", "white", size=25)
            self.pauseButton = True
        else:    
            GAME_FONT.render_to(SCREEN, (1206, 197), "Pause", "black", size=25) 
            self.pauseButton = False

        if (self.winCondition == 0):
            pygame.draw.rect(SCREEN, (0, 0, 0), (1200, 100, 100, 50))
            pygame.draw.rect(SCREEN, (163, 163, 163), (1203, 103, 94, 44))
            if (Rect(1203, 103, 94, 44).collidepoint(pygame.mouse.get_pos())):
                GAME_FONT.render_to(SCREEN, (1208, 115), "Retry", "white", size=25)
                self.retryButton = True
            else:    
                GAME_FONT.render_to(SCREEN, (1208, 115), "Retry", "black", size=25) 
                self.retryButton = False
        elif (self.winCondition == 1):
            pygame.draw.rect(SCREEN, (0, 0, 0), (1180, 50, 150, 50))
            pygame.draw.rect(SCREEN, (163, 163, 163), (1183, 53, 144, 44))
            if (Rect(1183, 53, 144, 44)).collidepoint(pygame.mouse.get_pos()):
                GAME_FONT.render_to(SCREEN, (1187, 63), "Auto-Win", "white", size=25)
                self.autoWinButton = True
            else:    
                GAME_FONT.render_to(SCREEN, (1187, 63), "Auto-Win", "black", size=25)
                self.autoWinButton = False
        elif (self.winCondition == 2):
            self.autoWinButton = False
            self.endScreen()
                   
    def resetGame(self):
        self.allPiles = [[], [], [], [], [], [], []]
        self.extraPile = []
        self.cardHolders = [CardHolder("spade", 530, 30), CardHolder("clover", 690, 30), CardHolder("heart", 850, 30), CardHolder("diamond", 1010, 30)]
        
        self.extraPileBookmark = -1  
        
        self.winCondition = 0
        
        self.clicks = 0
        self.moves = 0
        self.timeMinutes = 0
        self.timeSeconds = 0
        self.startTime = 0
        self.timeStage = 0
        
        self.loadCards()
        self.generateStage()  
        self.structureAllPile()          
                   
    def loadCards(self):
        for i in range(1, 14):
            self.deck.append(Card("clover", i))
            self.deck.append(Card("spade", i))
            self.deck.append(Card("heart", i))
            self.deck.append(Card("diamond", i))
            
    def generateStage(self):
        x = 1
        for i in range(7):
            for i in range(x):
                self.allPiles[x-1].append(self.drawRandomCard())
            x += 1
            
        for i in range(len(self.deck)):
            self.extraPile.append(self.drawRandomCard())    
            
    def blitEmptySpots(self):
        for item in self.cardHolders:
            item.blit()
        x = 50  
        y = 250  
        for i in range(7):
            SCREEN.blit(self.emptyDeck, (x, y))    
            x += 160
            
        SCREEN.blit(self.emptyDeck, (50, 30))    
               
    def drawRandomCard(self):
        randNum = random.randint(0, (len(self.deck)-1))
        save = self.deck[randNum]
        self.deck.pop(randNum)
        return save
    
    def structureAllPile(self):
        xDif = 0
        yDif = 0
        for pile in self.allPiles:
            for card in pile:
                card.x = 50 + xDif
                card.y = 250 + yDif
                yDif += self.cardOffset
                if (card != pile[len(pile)-1]):
                    card.showBack = True   
                else:    
                    card.bottomCard = True
            xDif += 160
            yDif = 0
            
        for card in self.extraPile:
            card.x = 210
            card.y = 30    
            
    def blitAllPiles(self):
        emptyPiles = 0
        unknownCard = False
        for pile in self.allPiles:
            if (len(pile)==0):
                emptyPiles+=1
            for card in pile:
                if (not unknownCard and card.showBack):
                    unknownCard = True
                card.blit()  
                
        if (emptyPiles == 7 and self.winCondition < 2):
            self.winCondition = 2         
                
        if (len(self.extraPile)!=0 and self.extraPileBookmark != len(self.extraPile)-1):
            SCREEN.blit(self.cardBack, (50, 30))
                             
        if (self.extraPileBookmark >= 0):
            if (self.extraPileBookmark >= 1):
                self.extraPile[self.extraPileBookmark-1].blit()
            self.extraPile[self.extraPileBookmark].blit()
                                 
        if (self.selectedCard != None):
            self.selectedCard.blit()  
            if (len(self.moveList)!=0):
                for card in self.moveList:
                    card.blit() 
                    
        if (not unknownCard and self.winCondition < 1):
            self.winCondition = 1                          
    
    def drawCard(self):
        if (Rect(50, 30, 150, 200).collidepoint(pygame.mouse.get_pos())):
            self.moves += 1
            self.extraPileBookmark += 1
            if (self.extraPileBookmark == (len(self.extraPile))):
                self.extraPileBookmark = -1
                       
                
    def selectCard(self):
        if (self.selectedCard != None):
            mousePos = pygame.mouse.get_pos()
            self.selectedCard.x = mousePos[0] - self.pointofMouseCollision[0]
            self.selectedCard.y = mousePos[1] - self.pointofMouseCollision[1]
            y = self.cardOffset
            for card in self.moveList:
                card.x = mousePos[0] - self.pointofMouseCollision[0]
                card.y = mousePos[1] - self.pointofMouseCollision[1] + y
                y += self.cardOffset
            return
        
        if (self.extraPileBookmark >= 0):
            card = self.extraPile[self.extraPileBookmark]
            if (Rect(card.x, card.y, card.width, card.height).collidepoint(pygame.mouse.get_pos())):
                mousePos = pygame.mouse.get_pos()
                if (len(self.saveOriginalPos) == 0):
                    self.saveOriginalPos = [card.x, card.y]
                    self.selectedCard = card
                    self.selectedCardPile = self.extraPile
                    self.pointofMouseCollision = [mousePos[0] - card.x, mousePos[1]- card.y]  
                    return
            
        lowerHeight = .20    
        for pile in self.allPiles:
            for card in pile:
                if (card.showBack):
                    continue
                if (card.bottomCard):
                    lowerHeight = 1
                else:
                    lowerHeight = .20    
                if (Rect(card.x, card.y, card.width, card.height*lowerHeight).collidepoint(pygame.mouse.get_pos()) and self.selectedCard == None):
                    mousePos = pygame.mouse.get_pos()
                    if (len(self.saveOriginalPos) == 0):
                        self.saveOriginalPos = [card.x, card.y]
                        self.selectedCard = card
                        self.selectedCardPile = pile
                        self.pointofMouseCollision = [mousePos[0] - card.x, mousePos[1]- card.y]    
                if (pile == self.selectedCardPile and card != self.selectedCard and card.y > self.selectedCard.y):
                    self.moveList.append(card) 
                    
        for holder in self.cardHolders:
                if (len(holder.cards)==0):
                    continue
                card = holder.cards[len(holder.cards)-1]
                if (Rect(card.x, card.y, card.width, card.height*lowerHeight).collidepoint(pygame.mouse.get_pos()) and self.selectedCard == None):
                    mousePos = pygame.mouse.get_pos()
                    if (len(self.saveOriginalPos) == 0):
                        self.saveOriginalPos = [card.x, card.y]
                        self.selectedCard = card
                        self.selectedCardPile = holder
                        self.pointofMouseCollision = [mousePos[0] - card.x, mousePos[1]- card.y]
                                                           
    def restoreSelectedCard(self):
        if (self.selectedCard == None):
            return
        if (not self.transferCard()):
            self.selectedCard.x = self.saveOriginalPos[0]
            self.selectedCard.y = self.saveOriginalPos[1]
            y = self.cardOffset
            for card in self.moveList:
                card.x = self.saveOriginalPos[0]
                card.y = self.saveOriginalPos[1] + y
                y += self.cardOffset  
        else:
            self.refurbishBottom(self.selectedCardPile)                     
        self.saveOriginalPos.clear()
        self.pointofMouseCollision.clear()
        self.moveList.clear()
        self.selectedCard = None
        self.selectedCardPile = None
        
    def transferCard(self):
        xDif = 50
        for pile in self.allPiles:
            if (pile == self.selectedCardPile):
                xDif += 160
                continue
            
            if (self.selectedCard.number == 13):
                if (len(pile) == 0):
                        if (Rect(xDif, 250, 150, 200)).colliderect(Rect(self.selectedCard.x, self.selectedCard.y, self.selectedCard.width, self.selectedCard.height)):
                            pile.append(self.selectedCard)
                            if (isinstance(self.selectedCardPile, CardHolder)):
                                self.selectedCardPile.cards.remove(self.selectedCard) 
                                self.selectedCardPile.acceptedNumber -= 1
                            elif (self.selectedCardPile == self.extraPile):
                                self.selectedCardPile.remove(self.selectedCard) 
                                self.extraPileBookmark -= 1   
                            else:
                                self.selectedCardPile.remove(self.selectedCard)     
                            self.selectedCard.x = xDif
                            self.selectedCard.y = 250
                            
                            if (len(self.moveList) != 0):
                                y = self.cardOffset
                                for addCard in self.moveList:
                                    pile.append(addCard)
                                    self.selectedCardPile.remove(addCard)
                                    addCard.x = xDif
                                    addCard.y = 220 + 30 + y
                                    y += self.cardOffset
                            self.refurbishBottom(self.selectedCardPile) 
                            self.refurbishBottom(pile) 
                            self.moves += 1      
                            return True    
            xDif += 160    
                            
            for item in self.cardHolders:
                if (len(self.moveList) != 0):
                        continue
                if (Rect(self.selectedCard.x, self.selectedCard.y, self.selectedCard.width, self.selectedCard.height)).colliderect(Rect(item.x, item.y, 150, 200)):
                    if (self.selectedCard.number == item.acceptedNumber and self.selectedCard.type == item.type):
                        item.acceptedNumber += 1
                        item.cards.append(self.selectedCard)
                        self.selectedCardPile.remove(self.selectedCard)
                        self.selectedCard.x = item.x
                        self.selectedCard.y = item.y
                        self.refurbishBottom(self.selectedCardPile)
                        if (self.selectedCardPile == self.extraPile):
                            self.extraPileBookmark -= 1 
                        self.moves += 1    
                        return True
            
            for card in pile:         
                if (card.bottomCard == False):
                    continue
                if (Rect(card.x, card.y, card.width, card.height)).colliderect(Rect(self.selectedCard.x, self.selectedCard.y, self.selectedCard.width, self.selectedCard.height)):
                    if (card.number - 1 == self.selectedCard.number and card.color != self.selectedCard.color):
                        pile.append(self.selectedCard)
                        if (isinstance(self.selectedCardPile, CardHolder)):
                            self.selectedCardPile.cards.remove(self.selectedCard) 
                            self.selectedCardPile.acceptedNumber -= 1
                        elif (self.selectedCardPile == self.extraPile):
                            self.selectedCardPile.remove(self.selectedCard) 
                            self.extraPileBookmark -= 1   
                        else:
                            self.selectedCardPile.remove(self.selectedCard)      
                        self.selectedCard.x = card.x
                        self.selectedCard.y = card.y + self.cardOffset
                        card.bottomCard = False
                        
                        if (len(self.moveList) != 0):
                            y = self.cardOffset
                            for addCard in self.moveList:
                                pile.append(addCard)
                                self.selectedCardPile.remove(addCard)
                                addCard.x = card.x
                                addCard.y = card.y + self.cardOffset + y
                                y += self.cardOffset
                        self.refurbishBottom(self.selectedCardPile) 
                        self.refurbishBottom(pile) 
                        self.moves +=  1      
                        return True

    def refurbishBottom(self, pile):
        if (isinstance(pile, CardHolder) or len(pile) == 0):
            return
        
        for card in pile:
            if (card == pile[len(pile)-1]):
                card.showBack = False
                card.bottomCard = True     
                
    def getRemainingCardNum(self):
        total = 0
        for pile in self.allPiles:
            for card in pile:
                total += 1
        
        for card in self.extraPile:
            total += 1
        return total    
                    
                                 

game = GameScreen()
game.loadCards()
game.generateStage()
game.structureAllPile()
def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()    
            if event.type == pygame.MOUSEBUTTONDOWN:
                game.clicks += 1
                game.drawCard()
                if (game.retryButton):
                    game.resetGame() 
                if (game.autoWinButton):
                    game.winCondition = 2  
                if (game.pauseButton):
                    game.pauseScreen()        
                
        SCREEN.fill((60, 143, 56))
        game.trackTime()
        game.blitEmptySpots()
        game.blitAllPiles()
        if (pygame.mouse.get_pressed()[0]):
            game.selectCard() 
        else:
            game.restoreSelectedCard()  
            
        game.blitWin()      
    
        pygame.display.update()
        FPS_CLOCK.tick(FPS)  

if __name__ == "__main__":
    main()    
