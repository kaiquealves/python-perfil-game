import pathlib
import random

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

QUESTIONS_PATH = pathlib.Path(__file__).parent / "cards.toml"
POINTS_TO_WIN = 30


class Card:
    id = 0
    category = ""
    correct_answers = []

class Tip:
    cardId = 0
    number = 0
    action = ""
    text = ""

class Participant:

    def __init__(self, name, points):
        self.name = name
        self.points = points

def pick_card(path,used_cards):
    cards = tomllib.loads(path.read_text())["cards"]

    if len(cards) == len(used_cards):
        return None

    card = random.sample(cards,1)[0]

    while card["id"] in used_cards:
       card = random.sample(cards,1)[0]

    print("| I got a new card. Good Luck!")
    print("| The category is ", card["category"])

    return card


def print_action(tip):

    special_points = random.randint(1,5)

    if tip == "#lost_turn":
        print("| Sorry! Unfortunately you lost your turn!")
        return 0
    elif tip == "#penalty":
        print("| Oh no! If you hit the answer you will loose {} points .".format(special_points))
        return special_points * -1    
    elif tip == "#bonus":
        print("| Uhul!! Bonus! If you hit the answer you will earn {} additional points.".format(special_points)) 
        return special_points

def print_tip(card, requested_tip, points):
    
    tips = card["tips"]
    actions = {"#lost_turn","#penalty","#bonus"}

    tip = tips[int(requested_tip)-1]
    
    if tip in actions:
        tip_points = print_action(tip)
        if (tip_points == 0):
            points = 0
        else:
            points += tip_points
    else:
        print("| Tip", str(requested_tip), "-", tip, "\n")
        points -= 1
    
    return points
    

def ask_response(card):
    if card["category"] == "Person":
        msg_guess = "Do you know who is?"
    elif card["category"] == "Year":
        msg_guess = "Do you know when was this?"
    elif card["category"] == "Object":
        msg_guess = "Do you know what thing is it?"
    elif card["category"] == "Place":
        msg_guess = "Do you know where is it?"
    else: 
        "Do you have any guess?"

    answer = input("| " + msg_guess + "=> ")
    
    return answer

def ask_YesOrNo(msgQuestion):

    yes_answers = ["YES", "Y"]
    no_answers = ["NO", "N"]

    while True:
        ans = input("| " + msgQuestion + " (Y or N) => ")
        if ans.upper() in yes_answers:
            return True
        elif ans.upper() in no_answers:
            return False
        else:
            print("| Please type 'Y' for Yes or 'N' for No.")

def ask_TipNumber(tipsRequested):
    while True:
        tip_request = input("| What tip do you want? => ")
        try:
            tip_request = int(tip_request)
        except ValueError:
            print("| (!) Please type a number between 1 and 20.")
            continue
        if tip_request in tipsRequested:
            print("| (!) This tip was already requested. Please, choose another number.")
        elif 1 <= tip_request <= 20:
            break
        else:
            print("| (!) Please type a number between 1 and 20.")
    return tip_request


def check_response(given_answer, correct_answers):
    if (given_answer.lower() in correct_answers):
        print("| Correct! Congratulations, you got it! ")
        return True
    else:
        print("| No, ", given_answer, "isn't the correct answer for this card! Keep trying...")
        return False


def get_participants():
    participants = []
    nextParticipant = True

    while nextParticipant:
        name = input("| Type Participant Name? => ")
        participants.append(Participant(name,0))

        nextParticipant = ask_YesOrNo("Do you wanna add another player?")

    return participants


def print_score(participants):
    print("\n##########################")
    print("######### SCORES #########")
    print("##########################")

    for obj in participants:
        print(obj.name, obj.points, sep=' => ')
    print("##########################\n")


def check_winner(participants):
    
    participants = list(filter(lambda item: item.points > POINTS_TO_WIN, participants))

    return participants


def run_round(card):
    
    points = 20
    tips_requested = []

    while (points > 0):
    
        tip_request = ask_TipNumber(tips_requested)
        tips_requested.append(tip_request)

        points = print_tip(card,tip_request, points)

        if points == 0:
            print("The correct response was: " + card["correct_answers"][0])
            break
                
        given_answer = ask_response(card)    
            
        if check_response(given_answer, card["correct_answers"]) == True:
            print("| You will receive", str(points), "new points. Let's check how is the ranking?")
            break
    
    return points

def next_participant(participants):

    participants.append(Participant(participants[0].name, participants[0].points))
    participants.__delitem__(0)

    return participants


def mock_participants():
    
    participants = []

    for i in range(1,4):
        participants.append(Participant("Player " + str(i),0))

    return participants

def run_game(participants):

    winners = []
    used_cards = []

    while winners == []:

        print("|\n|", participants[0].name ," it's your time!")
        card = pick_card(QUESTIONS_PATH,used_cards)
        if card == None:
            print("Played all cards!")
            break

        used_cards.append(card["id"])
        
        round_pts = run_round(card)          
                
        participants[0].points += round_pts

        ranking = sorted(participants, key=lambda x: x.points, reverse=True)
        
        print_score(ranking)

        participants = next_participant(participants)

        winners = check_winner(participants)

    print("\n|  Game Finished! The winner is ", ranking[0].name)


if __name__ == "__main__":
    print("JOGO PERFIL - Player vs CPU - V.01")

    participants = get_participants()

    while (answer_init := input("| Type 'start' to begin the game => ")) != "start":
        print("| Please, type 'start' when you're ready.")

    run_game(participants)
